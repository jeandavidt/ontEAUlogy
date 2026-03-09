# Graph-Based Agent Composition Algorithm Specification

## Overview

This document specifies how to extend the SPARQL query agent to implement a **graph-based agent composition algorithm** that automatically discovers and chains computational agents (models) to answer queries requiring multi-step simulations.

## The Core Problem

In water system modeling, answering queries often requires sequential execution of multiple models:

**Example Scenario (Household Case):**
- **Query**: "What is the permeate COD concentration from the RO system?"
- **Available Data**: Influent flow and COD to the MBR
- **Required Chain**: MBR → RO
  - MBR produces effluent flow/COD (intermediate data)
  - RO needs MBR effluent as its feed to produce permeate

Without composition, the query agent cannot answer this because:
1. RO model inputs are not in the current KG
2. The agent doesn't know it needs to run MBR first

## The Algorithm (Zhou et al., 2019)

The algorithm discovers agent compositions by iteratively simulating what data would become available:

```
function Composition(I₀, O₀):
    G ← ∅           # Final composition result (ordered layers)
    C ← ∅           # Set of all agents discovered
    D_collected ← I₀  # Currently available data
    
    repeat:
        i ← i + 1
        Lᵢ ← ∅      # Layer i of agents
        A ← ∅       # Agents discovered this iteration
        
        A ← discover_agent(D_collected)
        
        for all a = {Iₐ, Oₐ} ∈ A do:
            if a ∉ C then:
                Lᵢ ← Lᵢ ∪ {a}
                D_collected ← D_collected ∪ {Oₐ}  # Simulate outputs
        
        C ← C ∪ A
        G ← G ∪ {Lᵢ}
        
    until (O₀ ⊆ D_collected) or time out
    
    return G  # Ordered array of agent layers
```

### Key Concepts

| Symbol | Meaning |
|--------|---------|
| I₀ | Initial available data (from current KG state) |
| O₀ | Desired output data (from the query) |
| D_collected | Data available in the "alternate universe" KG |
| C | All agents discovered so far (prevent duplicates) |
| Lᵢ | Layer i: agents that can run in parallel at step i |
| G | Final result: ordered list of layers for execution |

## Ontology Representation

### Agent Capability Model

Agents must declare their I/O in the ontology using waterFRAME concepts:

```turtle
@prefix wf: <https://w3id.org/waterframe/> .
@prefix cap: <https://w3id.org/waterframe/capability/> .
@prefix case: <https://w3id.org/waterframe/case/household/> .

# MBR Agent Declaration
case:MBR_Agent a wf:ComputationalAgent ;
    rdfs:label "Membrane Bioreactor Model" ;
    wf:hasCapability cap:DynamicSimulation, cap:MassBalance ;
    wf:implements case:Membrane_bioreactor_Model ;
    wf:runsOn case:MBR_Service ;
    wf:offersOperation case:MBR_Simulation .

case:MBR_Simulation a wf:Operation ;
    rdfs:label "Run MBR simulation" ;
    wf:requiresInput case:MBR_Influent_Flow, case:MBR_Influent_COD ;
    wf:producesOutput case:MBR_Effluent_Flow, case:MBR_Effluent_COD, 
                       case:MBR_Biomass, case:MBR_Energy .

# Parameter declarations
case:MBR_Influent_Flow a wf:InputParameter ;
    wf:parameterName "influent_flow_m3d" ;
    wf:hasUnit "m³/d" ;
    wf:parameterType xsd:float .

case:MBR_Effluent_COD a wf:OutputParameter ;
    wf:parameterName "effluent_cod_mg_l" ;
    wf:hasUnit "mg/L" ;
    wf:parameterType xsd:float .
```

### Data Flow Relationships

Explicit data flow between operations enables chain discovery:

```turtle
# MBR effluent flows to RO feed
case:MBR_Simulation wf:dataFlowsTo case:RO_Simulation .

# Output-Input compatibility (MBR effluent COD is compatible with RO feed COD)
case:MBR_Effluent_COD wf:compatibleWith case:RO_Feed_COD .
```

## Implementation Architecture

### 1. New Service: `AgentComposer`

**Location**: `services/agent_composer.py`

**Responsibilities**:
- Discover agents based on available data
- Build composition layers iteratively
- Return executable plan

```python
class AgentComposer:
    """
    Implements the graph-based agent composition algorithm.
    
    Discovers chains of computational agents that can transform
    available data into desired query outputs.
    """
    
    def __init__(self, ontology_store, model_registry):
        self._ontology = ontology_store
        self._registry = model_registry
        self._max_iterations = 10
        
    async def compose(
        self,
        initial_data: Set[str],  # Parameter names available in KG
        target_outputs: Set[str],  # Parameter names needed for query
        timeout_seconds: float = 30.0
    ) -> CompositionResult:
        """
        Discover agent composition to produce target outputs.
        
        Args:
            initial_data: Set of parameter names currently in KG
            target_outputs: Set of parameter names needed for the query
            timeout_seconds: Maximum time to search for composition
            
        Returns:
            CompositionResult with layers of agents to execute
        """
        
    def _discover_agents(self, available_data: Set[str]) -> List[Agent]:
        """
        Query ontology for agents whose inputs are satisfied.
        
        SPARQL pattern:
        - Find operations where all required inputs are in available_data
        - Return agent references and their input/output parameters
        """
        
    def _simulate_outputs(
        self, 
        agents: List[Agent], 
        available_data: Set[str]
    ) -> Set[str]:
        """
        Simulate what new data would be available if agents were executed.
        
        This is the "alternate universe" step - we don't actually run
        the agents, we just add their declared outputs to D_collected
        to see what else becomes possible.
        """
```

### 2. SPARQL Discovery Query

The `discover_agent(D_collected)` step uses this SPARQL pattern:

```sparql
PREFIX wf: <https://w3id.org/waterframe/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?agent ?operation ?endpoint ?inputParam ?outputParam
WHERE {
    ?agent a wf:ComputationalAgent ;
           wf:offersOperation ?operation ;
           wf:runsOn ?software .
    
    ?operation wf:producesOutput ?outputParam .
    
    OPTIONAL { ?software wf:apiEndpoint ?endpoint }
    
    # Get all required inputs for this operation
    ?operation wf:requiresInput ?inputParam .
    
    # Filter: only include operations where ALL inputs are available
    # This is done in Python post-processing
}
```

Post-processing logic:
```python
def _filter_executable_agents(agents: List[Agent], available_data: Set[str]) -> List[Agent]:
    """Keep only agents whose ALL inputs are satisfied."""
    executable = []
    for agent in agents:
        if agent.required_inputs.issubset(available_data):
            executable.append(agent)
    return executable
```

### 3. Enhanced Query Router

**Location**: `routers/query.py`

Modify the natural language query endpoint to use composition:

```python
@router.post("/natural", response_model=NaturalLanguageQueryResponse)
async def execute_natural_query(request: NaturalLanguageQueryRequest):
    """Execute natural language query with automatic agent composition."""
    
    # Step 1: Analyze what data the query needs
    query_analysis = await analyze_query_requirements(request.question)
    # Returns: {target_outputs: {"ro_permeate_cod", "ro_permeate_flow"}}
    
    # Step 2: Get current KG state
    kg_state = await get_kg_data_availability()
    # Returns: {"influent_flow_m3d", "influent_cod_mg_l", ...}
    
    # Step 3: Check if query can be answered directly
    if query_analysis.target_outputs.issubset(kg_state):
        # Execute SPARQL directly
        return await execute_sparql_query(...)
    
    # Step 4: Need agent composition - discover plan
    composer = AgentComposer(ontology_store, registry)
    composition = await composer.compose(
        initial_data=kg_state,
        target_outputs=query_analysis.target_outputs
    )
    
    if not composition.found:
        return NaturalLanguageQueryResponse(
            original_question=request.question,
            execution_plan=f"Cannot answer query. Missing data: {composition.missing}",
            simulation_required=True,
            suggested_models=[]
        )
    
    # Step 5: Execute composition layers
    execution_results = await execute_composition(composition)
    
    # Step 6: Store results in KG (alternate universe → real)
    await store_simulation_results(execution_results)
    
    # Step 7: Now answer the original query
    final_results = await execute_sparql_query(...)
    
    return NaturalLanguageQueryResponse(
        original_question=request.question,
        generated_sparql=final_results["sparql"],
        results=final_results["results"],
        execution_plan=composition.describe_plan(),
        simulation_required=True,
        suggested_models=composition.get_all_agent_ids()
    )
```

### 4. Query Requirement Analyzer

**Location**: `services/query_analyzer.py`

Uses LLM or SPARQL pattern matching to extract what outputs a query needs:

```python
class QueryAnalyzer:
    """
    Analyzes natural language queries to determine:
    - What output parameters are being asked for
    - What entities are involved
    - Whether simulation is required
    """
    
    async def analyze(self, question: str) -> QueryRequirements:
        """
        Example analyses:
        - "What is the RO permeate COD?" → {target_outputs: {"ro_permeate_cod"}}
        - "MBR effluent quality?" → {target_outputs: {"mbr_effluent_cod", "mbr_effluent_tss"}}
        - "Total energy consumption?" → {target_outputs: {"total_energy"}, aggregation: "sum"}
        """
        
    def _map_to_ontology_parameters(self, natural_language_terms: List[str]) -> Set[str]:
        """
        Map natural language to ontology parameter names.
        Uses fuzzy matching against wf:parameterName values.
        """
```

### 5. Data Availability Checker

**Location**: `services/kg_analyzer.py`

```python
class KGAnalyzer:
    """Analyzes what data is currently available in the knowledge graph."""
    
    async def get_available_parameters(self, entity_filter: Optional[str] = None) -> Set[str]:
        """
        Query the KG to find all parameters with values.
        
        SPARQL:
        SELECT DISTINCT ?paramName
        WHERE {
            ?entity wf:hasParameter ?param .
            ?param wf:parameterName ?paramName ;
                   rdf:value ?value .
        }
        """
        
    async def get_entity_outputs(self, entity_id: str) -> Set[str]:
        """Get all output parameters for a specific entity."""
```

## Data Structures

### Agent

```python
class Agent:
    """Represents a discoverable computational agent."""
    id: str                    # Unique identifier
    name: str                  # Human-readable name
    operation_uri: str         # Ontology URI for the operation
    endpoint: str              # HTTP endpoint to execute
    required_inputs: Set[str]  # Parameter names needed
    produced_outputs: Set[str] # Parameter names produced
    capabilities: List[str]    # e.g., ["DynamicSimulation"]
```

### CompositionLayer

```python
class CompositionLayer:
    """A layer of agents that can execute in parallel."""
    layer_index: int           # Position in composition (0, 1, 2...)
    agents: List[Agent]        # Agents in this layer
    required_inputs: Set[str]  # Combined inputs needed
    produced_outputs: Set[str] # Combined outputs produced
```

### CompositionResult

```python
class CompositionResult:
    """Result of agent composition discovery."""
    found: bool                     # Whether composition was found
    layers: List[CompositionLayer]  # Ordered layers to execute
    initial_data: Set[str]          # Data available at start
    target_outputs: Set[str]        # Data we needed to produce
    missing: Set[str]               # Unsatisfied outputs (if found=False)
    discovery_iterations: int       # How many iterations algorithm ran
    
    def describe_plan(self) -> str:
        """Generate human-readable execution plan."""
        lines = [f"Execution Plan ({len(self.layers)} layers):"]
        for layer in self.layers:
            agent_names = ", ".join(a.name for a in layer.agents)
            lines.append(f"  Layer {layer.layer_index}: {agent_names}")
        return "\n".join(lines)
        
    def get_all_agent_ids(self) -> List[str]:
        """Get all agent IDs in order of execution."""
        return [a.id for layer in self.layers for a in layer.agents]
```

## Example: Household Case Walkthrough

### Initial State

**KG contains:**
- `household:influent_flow_m3d = 1.5`
- `household:influent_cod_mg_l = 350`

**Query:** "What is the RO permeate COD?"

**Analysis:**
- Target outputs: `{ro_permeate_cod_mg_l}`
- Initial data: `{influent_flow_m3d, influent_cod_mg_l}`

### Iteration 1

**Discover agents with inputs ⊆ {influent_flow_m3d, influent_cod_mg_l}:**

| Agent | Required Inputs | Match? |
|-------|----------------|--------|
| MBR | {influent_flow_m3d, influent_cod_mg_l} | ✓ YES |
| RO | {feed_flow_m3d, feed_cod_mg_l} | ✗ No (feed_* not available) |
| Infiltration | {influent_flow_m3d} | ✓ YES |

**Layer 1**: MBR, Infiltration (can run in parallel)

**Simulate outputs:**
- D_collected = {influent_flow_m3d, influent_cod_mg_l, 
                 mbr_effluent_flow_m3d, mbr_effluent_cod_mg_l,
                 infiltration_outflow_m3d, infiltration_cod_removed_kg_d}

**Check target**: ro_permeate_cod_mg_l ∈ D_collected? No → Continue

### Iteration 2

**Discover agents with inputs ⊆ D_collected:**

| Agent | Required Inputs | Match? |
|-------|----------------|--------|
| MBR | Already in C | Skip |
| RO | {feed_flow_m3d, feed_cod_mg_l} | ✓ YES (MBR outputs match via wf:compatibleWith) |
| Infiltration | Already in C | Skip |

**Layer 2**: RO

**Simulate outputs:**
- D_collected += {ro_permeate_flow_m3d, ro_permeate_cod_mg_l, ...}

**Check target**: ro_permeate_cod_mg_l ∈ D_collected? **YES → STOP**

### Execution Plan

```
Execution Plan (2 layers):
  Layer 0: Membrane Bioreactor, Infiltration System
  Layer 1: Reverse Osmosis System
```

### Execution

```python
# Layer 0 - parallel execution
mbr_job = await run_simulation("mbr", inputs={
    "influent_flow_m3d": 1.5,
    "influent_cod_mg_l": 350
})
infil_job = await run_simulation("infiltration", inputs={
    "influent_flow_m3d": 1.5
})

# Wait for completion
mbr_results = await wait_for_job(mbr_job)
infil_results = await wait_for_job(infil_job)

# Layer 1 - depends on Layer 0
ro_job = await run_simulation("ro", inputs={
    "feed_flow_m3d": mbr_results["effluent_flow_m3d"],
    "feed_cod_mg_l": mbr_results["effluent_cod_mg_l"]
})
ro_results = await wait_for_job(ro_job)

# Answer query
answer = ro_results["permeate_cod_mg_l"]  # 17.5 mg/L
```

## API Schema Extensions

### New Request/Response Models

```python
class AgentCompositionRequest(BaseModel):
    """Request agent composition discovery."""
    initial_parameters: Dict[str, float]  # Parameter name → value
    target_query: str  # Natural language query
    max_layers: int = 10
    timeout_seconds: float = 30.0


class AgentCompositionResponse(BaseModel):
    """Response with discovered composition."""
    composition_found: bool
    execution_plan: str  # Human-readable description
    layers: List[CompositionLayerResponse]
    total_agents: int
    estimated_execution_time_seconds: float


class CompositionLayerResponse(BaseModel):
    """Serializable layer representation."""
    layer_index: int
    agent_ids: List[str]
    agent_names: List[str]
    parallelizable: bool
    inputs_needed: Dict[str, float]  # Parameter → source (from previous layer or initial)
    outputs_produced: List[str]
```

### New Endpoints

```python
@router.post("/compose", response_model=AgentCompositionResponse)
async def discover_composition(request: AgentCompositionRequest):
    """
    Discover agent composition to answer a query.
    
    Returns the plan without executing it.
    """


@router.post("/compose-and-execute")
async def compose_and_execute(request: AgentCompositionRequest):
    """
    Discover composition and immediately execute it.
    
    Returns final query results after all simulations complete.
    """
```

## Ontology Requirements

For the algorithm to work, the ontology must contain:

1. **Agent declarations** with `wf:offersOperation`
2. **Operation I/O** with `wf:requiresInput` and `wf:producesOutput`
3. **Parameter names** using `wf:parameterName` for matching
4. **Data flow hints** (optional but helpful):
   - `wf:dataFlowsTo` between operations
   - `wf:compatibleWith` between parameters (e.g., MBR effluent COD → RO feed COD)

### Minimal Example TTL

```turtle
@prefix wf: <https://w3id.org/waterframe/> .
@prefix case: <https://w3id.org/waterframe/case/household/> .

# MBR Agent
case:MBR_Service a wf:ModelService ;
    wf:apiEndpoint "http://localhost:8101" .

case:MBR_Agent a wf:ComputationalAgent ;
    rdfs:label "MBR Model" ;
    wf:runsOn case:MBR_Service ;
    wf:offersOperation case:MBR_Run .

case:MBR_Run a wf:Operation ;
    wf:requiresInput case:Influent_Flow, case:Influent_COD ;
    wf:producesOutput case:Effluent_Flow, case:Effluent_COD .

case:Influent_Flow a wf:InputParameter ;
    wf:parameterName "influent_flow_m3d" .

case:Effluent_COD a wf:OutputParameter ;
    wf:parameterName "effluent_cod_mg_l" ;
    wf:compatibleWith case:RO_Feed_COD .

# RO Agent
case:RO_Agent a wf:ComputationalAgent ;
    rdfs:label "RO Model" ;
    wf:runsOn case:RO_Service ;
    wf:offersOperation case:RO_Run .

case:RO_Run a wf:Operation ;
    wf:requiresInput case:RO_Feed_Flow, case:RO_Feed_COD ;
    wf:producesOutput case:Permeate_Flow, case:Permeate_COD .

case:RO_Feed_COD a wf:InputParameter ;
    wf:parameterName "feed_cod_mg_l" .
```

## Implementation Checklist

- [ ] Create `AgentComposer` service class
- [ ] Implement SPARQL discovery queries
- [ ] Create `QueryAnalyzer` for extracting target outputs
- [ ] Create `KGAnalyzer` for checking data availability
- [ ] Add composition endpoints to query router
- [ ] Extend ontology with agent declarations (TTL)
- [ ] Add `wf:compatibleWith` relationships for parameter mapping
- [ ] Write tests for composition algorithm
- [ ] Write integration tests for household case

## Testing Strategy

### Unit Tests

```python
async def test_mbr_ro_composition():
    """Test the classic MBR→RO chain discovery."""
    composer = AgentComposer(mock_ontology, mock_registry)
    
    result = await composer.compose(
        initial_data={"influent_flow_m3d", "influent_cod_mg_l"},
        target_outputs={"ro_permeate_cod_mg_l"}
    )
    
    assert result.found is True
    assert len(result.layers) == 2
    assert result.layers[0].agents[0].id == "mbr"
    assert result.layers[1].agents[0].id == "ro"


async def test_no_composition_possible():
    """Test when target cannot be reached."""
    result = await composer.compose(
        initial_data={"influent_flow_m3d"},
        target_outputs={"unknown_parameter_xyz"}
    )
    
    assert result.found is False
    assert "unknown_parameter_xyz" in result.missing
```

### Integration Test (Household Case)

```python
async def test_household_query_with_composition():
    """End-to-end test of query → composition → execution."""
    
    # Setup: Ensure MBR and RO are registered
    await register_model("mbr", endpoint="http://localhost:8101")
    await register_model("ro", endpoint="http://localhost:8102")
    
    # Query that requires composition
    response = await client.post("/api/v1/query/natural", json={
        "question": "What is the RO permeate COD concentration?"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # Should indicate composition was needed and executed
    assert data["simulation_required"] is True
    assert "MBR" in data["execution_plan"]
    assert "RO" in data["execution_plan"]
    assert len(data["results"]) > 0
```

## Summary

This specification enables the SPARQL query agent to:

1. **Understand** what data a query needs
2. **Discover** which agents can provide that data
3. **Plan** multi-step execution chains automatically
4. **Execute** agents in the right order to answer queries

The key innovation is the "alternate universe KG" simulation - by virtually adding agent outputs to the available data set iteratively, the algorithm discovers dependencies without actually running expensive simulations until necessary.
