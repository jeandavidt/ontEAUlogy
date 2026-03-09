# Plan: Query Resolution Trace Visualization

**Branch:** `feature/reusable-orchestrator-frontend`
**Goal:** Emit structured events from all agents during query resolution, store them KG-natively (PROV-O), and visualize the resolution process in the household frontend as an interactive diagram with parallel scenario support.

---

## Decisions

- Test fixture agents (for 2-layer chain) go in a **separate TTL**: `case_studies/household/data/test_agents_chain.ttl` — loaded only in test config.
- Parallel scenarios use the **existing `/compose-and-execute` endpoint** with a new `parallel_scenarios` field on the request body.
- Frontend `QueryTimeline` opens in **diagram mode** (boxes + arrows like the reference image) by default; timeline (swimlane) mode is a toggle.

---

## Phase 1 — Ontology: Execution Event Vocabulary

**New file: `data/ontology/modules/execution_events.ttl`**

```turtle
@prefix wf: <https://ugentbiomath.github.io/waterframe#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

wf:ExecutionEvent   rdfs:subClassOf prov:Activity .    # one agent invocation
wf:ExecutionScenario rdfs:subClassOf prov:Bundle .     # one parallel branch
wf:EventParameter   rdfs:subClassOf prov:Entity .      # input or output datum

wf:inLayer       rdfs:domain wf:ExecutionEvent ;  rdfs:range xsd:integer .
wf:inScenario    rdfs:domain wf:ExecutionEvent ;  rdfs:range wf:ExecutionScenario .
wf:parentScenario rdfs:domain wf:ExecutionScenario ; rdfs:range wf:ExecutionScenario .
wf:branchPoint   rdfs:domain wf:ExecutionScenario ; rdfs:range wf:ExecutionEvent .
wf:parameterValue rdfs:domain wf:EventParameter ; rdfs:range xsd:string .
wf:parameterUnit  rdfs:domain wf:EventParameter ; rdfs:range xsd:string .
wf:refersToKGNode rdfs:domain wf:EventParameter .  # links to e.g. household:MBR_EffluentCOD
```

Reuse `prov:used` (agent consumed this input), `prov:wasGeneratedBy` (output produced by this event), `prov:startedAtTime`, `prov:endedAtTime`.

**Modify `data/ontology/waterframe.ttl`:** add `owl:imports <.../modules/execution_events>`.

---

## Phase 2 — Backend: Enrich Execution Trace Model

**Modify `case_studies/core/orchestrator/src/ontEAUlogy_core/services/execution_trace.py`**

### New dataclasses (additive — keep existing API working)

```python
@dataclass
class EventParameter:
    name: str
    value: Any
    unit: Optional[str] = None
    kg_node_uri: Optional[str] = None    # e.g. "household:MBR_EffluentCOD"
    kg_node_label: Optional[str] = None  # resolved rdfs:label

@dataclass
class ExecutionEvent:
    event_id: str                          # uuid4
    agent_uri: str                         # full KG URI
    agent_name: str                        # rdfs:label from KG
    agent_type: AgentType
    operation_uri: str
    operation_name: str
    layer_index: Optional[int] = None
    scenario_id: Optional[str] = None
    parent_event_id: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    inputs: List[EventParameter] = field(default_factory=list)
    outputs: List[EventParameter] = field(default_factory=list)
    status: str = "running"               # running | completed | failed
    error: Optional[str] = None

@dataclass
class ExecutionScenario:
    scenario_id: str
    label: str
    parent_scenario_id: Optional[str] = None
    branch_event_id: Optional[str] = None
    events: List[ExecutionEvent] = field(default_factory=list)
    status: str = "running"

@dataclass
class QueryTrace:
    trace_id: str
    query: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"
    events: List[ExecutionEvent] = field(default_factory=list)
    scenarios: List[ExecutionScenario] = field(default_factory=list)
    total_layers: int = 0
```

### Updated `ExecutionTraceService` methods

| Method | Signature | Notes |
|--------|-----------|-------|
| `start_query_trace` | `(trace_id, query) → QueryTrace` | replaces `start_trace` for new API |
| `start_event` | `(trace_id, agent_uri, agent_name, agent_type, operation_uri, operation_name, *, layer_index, scenario_id, parent_event_id, inputs) → event_id` | returns uuid string |
| `end_event` | `(trace_id, event_id, outputs, status, error)` | sets `end_time` |
| `create_scenario` | `(trace_id, label, parent_scenario_id, branch_event_id) → scenario_id` | adds `ExecutionScenario` |
| `get_trace_json` | `(trace_id) → Dict` | full serialization for API |
| `to_prov_rdf` | `(trace_id) → rdflib.ConjunctiveGraph` | PROV-O JSON-LD export |

`to_prov_rdf()` maps:
- `ExecutionEvent` → `prov:Activity` with `prov:startedAtTime` / `prov:endedAtTime`
- `EventParameter` → `prov:Entity`; inputs via `prov:used`; outputs via `prov:wasGeneratedBy`
- `agent_uri` → `prov:Agent` referenced via `prov:wasAssociatedWith`
- `ExecutionScenario` → `prov:Bundle` containing its events

Keep `start_trace()` / `add_step()` / `end_trace()` unchanged for backward compatibility.

---

## Phase 3 — Backend: Instrument Agent Composer

**Modify `case_studies/core/orchestrator/src/ontEAUlogy_core/services/agent_composer.py`**

### `compose()` signature change

```python
async def compose(
    self,
    initial_data: Set[str],
    target_outputs: Set[str],
    timeout_seconds: float = 30.0,
    trace_id: Optional[str] = None,        # NEW
    scenario_id: Optional[str] = None,     # NEW
) -> CompositionResult:
```

### Events emitted inside the loop

At each iteration (layer discovery):
```python
layer_event_id = trace_service.start_event(
    trace_id,
    agent_uri="wf:ComposerAgent",
    agent_name="Composer Agent",
    agent_type=AgentType.ORCHESTRATOR,
    operation_uri="wf:DiscoverLayer",
    operation_name=f"Discover Layer {iteration}",
    layer_index=iteration,
    scenario_id=scenario_id,
    inputs=[EventParameter(name="available_data", value=sorted(available_data))]
)
# ... discovery ...
trace_service.end_event(
    trace_id, layer_event_id,
    outputs=[EventParameter(name="discovered_agents", value=[a.id for a in new_agents])],
    status="completed"
)
```

At each agent execution (inside `execute_composition_layers()` in the query router):
```python
agent_event_id = trace_service.start_event(
    trace_id,
    agent_uri=agent.id,
    agent_name=agent.name,
    agent_type=AgentType.MODEL,
    operation_uri=agent.operation_uri,
    operation_name=agent.name,
    layer_index=layer.layer_index,
    scenario_id=scenario_id,
    inputs=[EventParameter(name=k, value=v, kg_node_uri=kg_uri_for(k, ontology))
            for k, v in params.items()]
)
result = await call_agent(agent, params)
trace_service.end_event(
    trace_id, agent_event_id,
    outputs=[EventParameter(name=k, value=v, kg_node_uri=kg_uri_for(k, ontology))
             for k, v in result.items()],
    status="completed"
)
```

`kg_uri_for(param_name, ontology)` is a helper that SPARQL-queries:
```sparql
SELECT ?node WHERE {
  ?node wf:parameterName ?name .
  FILTER(str(?name) = "${param_name}")
}
LIMIT 1
```
Returns the full URI string so that the frontend can later query the KG for node details. Cached per session to avoid repeated queries.

### Parallel scenario support

Add `ScenarioSpec` to `AgentCompositionRequest`:
```python
class ScenarioSpec(BaseModel):
    initial_parameters: Dict[str, Any]
    target_outputs: List[str]
    label: str

class AgentCompositionRequest(BaseModel):
    # existing fields unchanged
    initial_parameters: Dict[str, Any]
    target_outputs: List[str]
    max_layers: int = 5
    timeout_seconds: float = 30.0
    # NEW
    parallel_scenarios: Optional[List[ScenarioSpec]] = None
```

When `parallel_scenarios` is set, the query router:
1. Creates one `ExecutionScenario` per spec via `trace_service.create_scenario()`
2. Runs all compositions in `asyncio.gather()`, each with its `scenario_id`
3. Merges results into one `QueryTrace`

---

## Phase 4 — Backend: Trace API

**Implement `case_studies/core/orchestrator/src/ontEAUlogy_core/routers/trace.py`** (currently a non-functional stub):

```
GET  /api/v1/traces               → list all traces (summary: id, query, status, start_time, total_layers)
GET  /api/v1/traces/{trace_id}    → full QueryTrace JSON
GET  /api/v1/traces/{trace_id}/prov  → PROV-O as JSON-LD
```

WebSocket events are pushed via the existing `/ws` router: when `start_event` / `end_event` / `create_scenario` / `end_trace` are called, broadcast to all WebSocket clients subscribed to `trace_id`. Message schema:
```json
{"type": "event_started",    "trace_id": "...", "event": {...}}
{"type": "event_completed",  "trace_id": "...", "event": {...}}
{"type": "scenario_created", "trace_id": "...", "scenario": {...}}
{"type": "trace_completed",  "trace_id": "..."}
```

**Modify `case_studies/core/orchestrator/src/ontEAUlogy_core/schemas/models.py`:**
- Add `EventParameterResponse`, `ExecutionEventResponse`, `ExecutionScenarioResponse`, `QueryTraceResponse`
- Add `ScenarioSpec` (see above)
- Add `trace_id: Optional[str]` to `AgentCompositionResponse`

---

## Phase 5 — Frontend: Types and API Hooks

**Modify `case_studies/household/frontend-react/src/api/types.ts`:**

```typescript
export interface EventParameter {
  name: string;
  value: unknown;
  unit?: string;
  kgNodeUri?: string;
  kgNodeLabel?: string;
}

export interface ExecutionEvent {
  eventId: string;
  agentUri: string;
  agentName: string;
  agentType: 'llm' | 'model' | 'orchestrator' | 'user';
  operationUri: string;
  operationName: string;
  layerIndex?: number;
  scenarioId?: string;
  parentEventId?: string;
  startTime: string;       // ISO 8601
  endTime?: string;
  inputs: EventParameter[];
  outputs: EventParameter[];
  status: 'running' | 'completed' | 'failed';
  error?: string;
}

export interface ExecutionScenario {
  scenarioId: string;
  label: string;
  parentScenarioId?: string;
  branchEventId?: string;
  events: ExecutionEvent[];
  status: 'running' | 'completed' | 'failed';
}

export interface QueryTrace {
  traceId: string;
  query: string;
  startTime: string;
  endTime?: string;
  status: 'running' | 'completed' | 'failed';
  events: ExecutionEvent[];
  scenarios: ExecutionScenario[];
  totalLayers: number;
}
```

**Modify `case_studies/household/frontend-react/src/api/queries.ts`:**
- `useQueryTrace(traceId?: string)` — React Query hook, polls `GET /api/v1/traces/{id}` every 500ms while status is `running`, stops when `completed` or `failed`
- `useTraceWebSocket(traceId?: string, onEvent: (msg) => void)` — subscribes to WebSocket, updates local state with live events

---

## Phase 6 — Frontend: QueryTimeline Component

### Files to create

| File | Description |
|------|-------------|
| `src/components/QueryTimeline.tsx` | Root component: mode toggle, scenario selector, renders diagram or timeline |
| `src/components/trace/AgentEventNode.tsx` | ReactFlow custom node: shows agent name, duration, status badge, expandable I/O |
| `src/components/trace/LayerGroupNode.tsx` | ReactFlow group node: colored column per composition layer |
| `src/components/trace/DataFlowEdge.tsx` | ReactFlow custom edge: labeled with shared parameter name |
| `src/components/trace/TraceTimeline.tsx` | SVG-based swimlane timeline (secondary mode) |
| `src/components/trace/KGNodeTooltip.tsx` | Hover tooltip: SPARQL-queries KG node and shows all properties |

### Diagram Mode layout (default)

Uses ReactFlow with `dagre` auto-layout:

- **Columns** = composition phases in order:
  `Discovery Layer 0` → `Discovery Layer 1` → ... → `Agent Plan Resolution` → `Simulation 1` → `Simulation 2` → ... → `Query Resolution`
- **Rows within a column** = individual agents executing in that layer
- **`AgentEventNode`**: rounded rectangle, header = agent name + type icon, body = status badge + duration. Click to expand and show full inputs/outputs list. Each `EventParameter` with `kgNodeUri` is a hoverable chip.
- **`DataFlowEdge`**: animated arrow from an output chip to a downstream input chip when `output.name === input.name`. No hardcoded knowledge of what connects to what — matching is purely by parameter name string from the trace data.
- **`LayerGroupNode`**: translucent colored background grouping all nodes with the same `layerIndex`. Label at top: "Discovery Layer N" / "Simulation N".
- **Scenario tabs**: if `trace.scenarios.length > 1`, show a tab bar above the diagram, one tab per scenario. Switching tabs re-renders the diagram filtered to that scenario's events.

### Timeline Mode

SVG component with:
- X-axis: milliseconds from `QueryTrace.startTime`; tick marks and labels
- Y-axis: one swimlane row per agent URI (label = `agentName`), grouped by `scenarioId` with a divider
- Bars: `height=20px`, colored by `agentType` (orchestrator=purple, model=teal, llm=amber), width = `endTime - startTime`, positioned by `startTime - traceStart`
- Running bars: animated pulse (no endTime yet)
- Click/hover: shows same `EventParameter` chip list as diagram mode

### KGNodeTooltip

When hovering over any `EventParameter` chip with `kgNodeUri`:
```sparql
SELECT ?label ?type ?unit ?comment ?value WHERE {
  <${kgNodeUri}> rdfs:label ?label ;
                 a ?type .
  OPTIONAL { <${kgNodeUri}> rdfs:comment ?comment }
  OPTIONAL { <${kgNodeUri}> wf:unit ?unit }
  OPTIONAL { <${kgNodeUri}> wf:nominalValue ?value }
}
```
Renders a small floating card with: type badge (from KG class label), label, unit, comment, and a link to the entity in the system topology view (if applicable). This makes all parameter semantics come from the KG — zero hardcoding in the component.

### Integration

In `Dashboard.tsx` or the relevant query section: after a `compose-and-execute` response that includes `trace_id`, render:
```tsx
{lastTraceId && (
  <QueryTimeline traceId={lastTraceId} orchestratorUrl={ORCHESTRATOR_URL} />
)}
```

---

## Phase 7 — Test Scenarios

### Test fixture TTL: `case_studies/household/data/test_agents_chain.ttl`

```turtle
@prefix wf: <https://ugentbiomath.github.io/waterframe#> .
@prefix household: <https://w3id.org/waterframe/case/household/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# WaterQualityAnalyzer: accepts MBR outputs → enables 2-layer chain
household:WQA_Software a wf:SoftwareSystem ;
    wf:apiEndpoint <http://localhost:8104> .

household:WQA_Agent a wf:SimulationAgent ;
    rdfs:label "Water Quality Analyzer" ;
    wf:runsOn household:WQA_Software ;
    wf:offersOperation household:WQA_AnalyzeOp .

household:WQA_AnalyzeOp a wf:Operation ;
    rdfs:label "Analyze Effluent Quality" ;
    wf:requiresInput
        [ a wf:ModelInput ; wf:parameterName "effluent_cod" ],
        [ a wf:ModelInput ; wf:parameterName "effluent_tss" ],
        [ a wf:ModelInput ; wf:parameterName "effluent_flow" ] ;
    wf:producesOutput
        [ a wf:ModelOutput ; wf:parameterName "water_quality_score" ],
        [ a wf:ModelOutput ; wf:parameterName "treatment_efficiency" ] ;
    wf:hasHTTPGrounding [
        wf:httpMethod "POST" ;
        wf:operationPath "/analyze" ;
        wf:requestFormat "application/json" ;
        wf:responseFormat "application/json" ;
    ] .
```

This fixture is loaded only when the test config sets `extra_ontology_files: [test_agents_chain.ttl]`. The corresponding mock HTTP endpoint for port 8104 is implemented as a `pytest` fixture using `httpx.MockTransport`.

### Test config: `case_studies/household/config/orchestrator_test.yaml`

Same as `orchestrator.yaml` but with `test_agents_chain.ttl` added to `ontology_files`.

### Test file: `case_studies/household/tests/test_query_trace_visualization.py`

Six scenarios (use `pytest.mark.asyncio` + `httpx.AsyncClient`):

| ID | Layers | Scenarios | Request | Assertions |
|----|--------|-----------|---------|------------|
| T1 | 0 | 1 | `POST /api/v1/query/sparql` with `SELECT ?a WHERE { ?a a wf:ComputationalAgent }` | `trace.total_layers == 0`; 1 event of type `orchestrator`; `end_time` set |
| T2 | 0 | 1 | `POST /api/v1/query/nl` with `"What agents are available?"` | `trace.total_layers == 0`; 1 LLM event; events have `start_time` and `end_time` |
| T3 | 1 | 1 | `POST /api/v1/query/compose-and-execute` with `target_outputs=["effluent_cod"]` + MBR inputs | `trace.total_layers == 1`; 1 MBR model event; event has `inputs` with `kg_node_uri` set; `outputs[0].name == "effluent_cod"` |
| T4 | 2 | 1 | Same initial params, `target_outputs=["water_quality_score"]` | `trace.total_layers == 2`; 2 model events (MBR then WQA); MBR `outputs` overlap with WQA `inputs` by name |
| T5 | 1 | 2 | `parallel_scenarios=[{target: ["effluent_cod"], label: "MBR"}, {target: ["infiltrated_flow"], label: "Infiltration"}]` | `len(trace.scenarios) == 2`; each scenario has 1 model event; both have `status == "completed"` |
| T6 | 2 | 3 | `parallel_scenarios=[{target: ["water_quality_score"]}, {target: ["infiltrated_flow"]}, {target: ["permeate_flow"]}]` (RO needs feed params so this tests graceful failure for scenario 3) | `len(trace.scenarios) == 3`; scenario 1: 2 events (MBR+WQA); scenario 2: 1 event (Infiltration); scenario 3: `status == "failed"`, `error` contains missing params |

Also assert for all tests with model events:
- `event.inputs` are `EventParameter` objects with `name`, `value`, and `kg_node_uri != None`
- `event.start_time < event.end_time`
- `trace.events` and scenario events are consistent (scenario events are a subset of trace events)

---

## File Change Summary

| File | Change | Description |
|------|--------|-------------|
| `data/ontology/modules/execution_events.ttl` | **NEW** | `wf:ExecutionEvent`, `wf:ExecutionScenario`, `wf:EventParameter` using PROV-O |
| `data/ontology/waterframe.ttl` | modify | `owl:imports execution_events` |
| `case_studies/household/data/test_agents_chain.ttl` | **NEW** | `WaterQualityAnalyzer_Agent` fixture for 2-layer chain test |
| `case_studies/household/config/orchestrator_test.yaml` | **NEW** | Test config loading extra TTL |
| `case_studies/core/.../services/execution_trace.py` | modify | `EventParameter`, `ExecutionEvent`, `ExecutionScenario`, `QueryTrace`; new service methods; `to_prov_rdf()` |
| `case_studies/core/.../services/agent_composer.py` | modify | Emit events at each layer/agent; `trace_id`/`scenario_id` params; `kg_uri_for()` helper |
| `case_studies/core/.../routers/trace.py` | implement | `GET /traces`, `GET /traces/{id}`, `GET /traces/{id}/prov`, WebSocket push |
| `case_studies/core/.../routers/query.py` | modify | Pass `trace_id`/`scenario_id` through compose+execute; handle `parallel_scenarios` |
| `case_studies/core/.../schemas/models.py` | modify | Response types for trace; `ScenarioSpec`; `trace_id` on `AgentCompositionResponse` |
| `case_studies/household/frontend-react/src/api/types.ts` | modify | `EventParameter`, `ExecutionEvent`, `ExecutionScenario`, `QueryTrace` |
| `case_studies/household/frontend-react/src/api/queries.ts` | modify | `useQueryTrace()`, `useTraceWebSocket()` |
| `case_studies/household/frontend-react/src/components/QueryTimeline.tsx` | **NEW** | Root component: mode toggle, scenario tabs, renders diagram or timeline |
| `case_studies/household/frontend-react/src/components/trace/AgentEventNode.tsx` | **NEW** | ReactFlow custom node |
| `case_studies/household/frontend-react/src/components/trace/LayerGroupNode.tsx` | **NEW** | ReactFlow group node per composition layer |
| `case_studies/household/frontend-react/src/components/trace/DataFlowEdge.tsx` | **NEW** | ReactFlow edge matching by parameter name |
| `case_studies/household/frontend-react/src/components/trace/TraceTimeline.tsx` | **NEW** | SVG swimlane timeline (secondary mode) |
| `case_studies/household/frontend-react/src/components/trace/KGNodeTooltip.tsx` | **NEW** | SPARQL-powered hover tooltip for `EventParameter` chips |
| `case_studies/household/frontend-react/src/pages/Dashboard.tsx` | modify | Render `<QueryTimeline traceId={...} />` after compose-and-execute |
| `case_studies/household/tests/test_query_trace_visualization.py` | **NEW** | T1–T6 integration tests |

---

## Implementation Prompt

```
You are implementing the query resolution trace visualization feature for the ontEAUlogy project on branch `feature/reusable-orchestrator-frontend`. The full plan is at `plans/query-trace-visualization.md`. Read it completely before starting.

Architecture: FastAPI orchestrator (core at `case_studies/core/orchestrator/`) + React/TypeScript frontend (`case_studies/household/frontend-react/`). Agents are registered in the knowledge graph (RDF/OWL, loaded via rdflib) and discovered via SPARQL. The existing execution trace service is at `case_studies/core/orchestrator/src/ontEAUlogy_core/services/execution_trace.py`.

Implement in this order:
1. Ontology module (`execution_events.ttl`) + import in `waterframe.ttl`
2. Test fixture TTL (`household/data/test_agents_chain.ttl`) + test config yaml
3. Enrich `execution_trace.py` with `EventParameter`, `ExecutionEvent`, `ExecutionScenario`, `QueryTrace`, new service methods, and `to_prov_rdf()`
4. Instrument `agent_composer.py`: add `trace_id`/`scenario_id` params, emit events at each layer discovery and agent execution; add `kg_uri_for()` helper
5. Update `schemas/models.py`: `ScenarioSpec`, `QueryTraceResponse`, `trace_id` on `AgentCompositionResponse`
6. Update `routers/query.py`: pass trace context through compose+execute; handle `parallel_scenarios` via `asyncio.gather`
7. Implement `routers/trace.py`: `GET /traces`, `GET /traces/{id}`, `GET /traces/{id}/prov`, WebSocket push on each trace mutation
8. Frontend types + hooks (`types.ts`, `queries.ts`)
9. Frontend trace components (`QueryTimeline.tsx` and `trace/` subdirectory): diagram mode default (ReactFlow + dagre), timeline mode toggle, KGNodeTooltip with live SPARQL lookup
10. Wire into `Dashboard.tsx`
11. Write and run `test_query_trace_visualization.py` (T1–T6)

Key constraints:
- Never hardcode parameter names or agent names in frontend components — all semantics come from trace data or KG SPARQL queries.
- Keep backward compatibility: existing `start_trace()`/`add_step()`/`end_trace()` must still work.
- The test fixture agents (port 8104) must be mocked in tests using httpx MockTransport — do not require running services.
- DataFlowEdge connections are derived purely by matching `output.name === input.name` across events — no hardcoded topology.
- Run existing tests after each phase to catch regressions.
```
