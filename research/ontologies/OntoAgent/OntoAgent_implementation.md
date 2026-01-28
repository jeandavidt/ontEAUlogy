# Implementation Plan: Computational Agent Ontology Module

## Executive Summary

Build a new waterFRAME ontology module (`agents.ttl`) for representing computational agents with semantic interfaces, enabling compositional queries like "Given data {α, β, γ} and agents {A, B, C}, can I compute information X?"

**Key Innovation**: Extends existing waterFRAME patterns by adding an agent abstraction layer on top of ProcessModel, enabling service-oriented discovery, operation specification with preconditions/postconditions, and automatic compositional reasoning.

---

## 1. Module Architecture

### 1.1 Core Design Decisions

**Reuse Over Reinvention:**
- **REUSE** existing `ModelInput`/`ModelOutput` classes from information.ttl
- **REUSE** existing `wf:hasCapability` property from capabilities.ttl
- **EXTEND** existing `SoftwareSystem` class rather than creating parallel hierarchy
- **FOLLOW** waterFRAME's shallow hierarchy principle (6 core classes + properties)

**Integration Points:**
```
agents.ttl (NEW)
  ├── imports information.ttl (ProcessModel, ModelInput/Output, SoftwareSystem)
  ├── imports capabilities.ttl (ModelCapability taxonomy, hasCapability property)
  └── imports core/properties.ttl (namespace and basic properties)
```

**BFO Alignment:**
- `ComputationalAgent` → subclass of `bfo:BFO_0000031` (Generically dependent continuant / ICE)
- `Operation` → subclass of `bfo:BFO_0000015` (Process)
- `ExecutionCondition` → subclass of `bfo:BFO_0000023` (Specifically dependent continuant)

**Separation from WaWO+:**
- `ComputationalAgent` is **disjoint** from `wawo:Actor` (humans, organizations)
- Different semantic categories: informational vs physical/institutional

---

## 2. Class Hierarchy (6 Classes)

### 2.1 Primary Classes

```turtle
# ========== COMPUTATIONAL AGENT ==========
wf:ComputationalAgent a owl:Class ;
    rdfs:subClassOf bfo:BFO_0000031 ;  # ICE
    rdfs:label "Computational agent" ;
    rdfs:comment "Software system providing computational services for water system
    simulation/analysis. Distinct from physical actors (wawo:Actor)." ;
    owl:disjointWith wawo:Actor .

# ========== OPERATION ==========
wf:Operation a owl:Class ;
    rdfs:subClassOf bfo:BFO_0000015 ;  # Process
    rdfs:label "Computational operation" ;
    rdfs:comment "Specific computation with defined inputs, outputs, preconditions,
    and postconditions. Operations are process types instantiated during execution." .

# ========== EXECUTION CONDITION ==========
wf:ExecutionCondition a owl:Class ;
    rdfs:subClassOf bfo:BFO_0000023 ;  # SDC
    rdfs:label "Execution condition" ;
    rdfs:comment "Logical condition constraining operation execution." .

wf:Precondition rdfs:subClassOf wf:ExecutionCondition ;
    rdfs:label "Precondition" ;
    rdfs:comment "Must hold before operation executes." .

wf:Postcondition rdfs:subClassOf wf:ExecutionCondition ;
    rdfs:label "Postcondition" ;
    rdfs:comment "Guaranteed after successful execution." .

# ========== HTTP GROUNDING ==========
wf:HTTPGrounding a owl:Class ;
    rdfs:subClassOf bfo:BFO_0000023 ;
    rdfs:label "HTTP grounding" ;
    rdfs:comment "Technical specification for HTTP invocation (method, path, format)." .
```

### 2.2 Agent Type Specializations (for discovery)

```turtle
wf:SimulationAgent rdfs:subClassOf wf:ComputationalAgent .
wf:OptimizationAgent rdfs:subClassOf wf:ComputationalAgent .
wf:DataTransformAgent rdfs:subClassOf wf:ComputationalAgent .
wf:ReasoningAgent rdfs:subClassOf wf:ComputationalAgent .
```

---

## 3. Object Properties (10 Properties)

### 3.1 Agent-Model Relationships

```turtle
# Agent implements computational model
wf:implements a owl:ObjectProperty ;
    rdfs:domain wf:ComputationalAgent ;
    rdfs:range wf:ProcessModel .

# Agent simulates physical entity
wf:simulates a owl:ObjectProperty ;
    rdfs:domain wf:ComputationalAgent ;
    rdfs:range bfo:BFO_0000040 .  # Material entity

# Agent runs on software system (REUSE existing class!)
wf:runsOn a owl:ObjectProperty ;
    rdfs:domain wf:ComputationalAgent ;
    rdfs:range wf:SoftwareSystem .
```

### 3.2 Operation Specifications

```turtle
# Agent offers operations
wf:offersOperation a owl:ObjectProperty ;
    rdfs:domain wf:ComputationalAgent ;
    rdfs:range wf:Operation .

# Operation I/O (REUSE existing ModelInput/ModelOutput!)
wf:requiresInput a owl:ObjectProperty ;
    rdfs:domain wf:Operation ;
    rdfs:range wf:ModelInput .

wf:producesOutput a owl:ObjectProperty ;
    rdfs:domain wf:Operation ;
    rdfs:range wf:ModelOutput .

wf:acceptsOptionalInput a owl:ObjectProperty ;
    rdfs:domain wf:Operation ;
    rdfs:range wf:ModelInput .
```

### 3.3 Execution Conditions

```turtle
# Link operations to conditions
wf:hasPrecondition a owl:ObjectProperty ;
    rdfs:domain wf:Operation ;
    rdfs:range wf:Precondition .

wf:hasPostcondition a owl:ObjectProperty ;
    rdfs:domain wf:Operation ;
    rdfs:range wf:Postcondition .

# Link conditions to constrained parameters
wf:constrainsParameter a owl:ObjectProperty ;
    rdfs:domain wf:ExecutionCondition ;
    rdfs:range [ owl:unionOf (wf:ModelInput wf:ModelOutput wf:ModelVariable) ] .
```

### 3.4 HTTP Grounding

```turtle
# Link operation to HTTP specification
wf:hasHTTPGrounding a owl:ObjectProperty ;
    rdfs:domain wf:Operation ;
    rdfs:range wf:HTTPGrounding .
```

### 3.5 Compositional Reasoning

```turtle
# Enable workflow composition queries
wf:dataFlowsTo a owl:ObjectProperty ;
    rdfs:label "data flows to" ;
    rdfs:comment "Output from this operation can serve as input to target operation" ;
    rdfs:domain wf:Operation ;
    rdfs:range wf:Operation .

# Inferred via property chain axiom:
# IF operation A produces output X AND operation B requires input X
# THEN A dataFlowsTo B
wf:dataFlowsTo owl:propertyChainAxiom (
    wf:producesOutput
    [ owl:inverseOf wf:requiresInput ]
) .
```

---

## 4. Datatype Properties (9 Properties)

### 4.1 HTTP Grounding Details

```turtle
# HTTP method and paths
wf:httpMethod a owl:DatatypeProperty ;
    rdfs:domain wf:HTTPGrounding ;
    rdfs:range xsd:string .  # GET, POST, PUT, etc.

wf:operationPath a owl:DatatypeProperty ;
    rdfs:domain wf:HTTPGrounding ;
    rdfs:range xsd:string .  # e.g., "/simulate"

wf:requestFormat a owl:DatatypeProperty ;
    rdfs:domain wf:HTTPGrounding ;
    rdfs:range xsd:string .  # e.g., "application/json"

wf:responseFormat a owl:DatatypeProperty ;
    rdfs:domain wf:HTTPGrounding ;
    rdfs:range xsd:string .

wf:requiresAuthentication a owl:DatatypeProperty ;
    rdfs:domain wf:HTTPGrounding ;
    rdfs:range xsd:boolean .
```

### 4.2 Execution Conditions

```turtle
# Constraint expression (string representation)
wf:constraintExpression a owl:DatatypeProperty ;
    rdfs:domain wf:ExecutionCondition ;
    rdfs:range xsd:string .  # e.g., "BOD > 0", "timestep < maxTimestep"
```

### 4.3 Performance Metadata

```turtle
wf:estimatedExecutionTime a owl:DatatypeProperty ;
    rdfs:domain wf:Operation ;
    rdfs:range xsd:float .  # seconds

wf:computationalComplexity a owl:DatatypeProperty ;
    rdfs:domain wf:Operation ;
    rdfs:range xsd:string .  # e.g., "O(n²)"
```

### 4.4 Agent Version

```turtle
wf:agentVersion a owl:DatatypeProperty ;
    rdfs:domain wf:ComputationalAgent ;
    rdfs:range xsd:string .
```

---

## 5. Complete Example Instance

```turtle
@prefix wf: <https://ugentbiomath.github.io/waterframe#> .
@prefix cap: <https://ugentbiomath.github.io/waterframe/capability#> .
@prefix ghent: <https://w3id.org/waterframe/case/ghent/> .

# ========== PHYSICAL ENTITY ==========
ghent:WWTP1 a wf:WastewaterTreatmentPlant ;
    rdfs:label "Wastewater Treatment Plant 1" .

# ========== PROCESS MODEL ==========
ghent:WWTP1_Model a wf:SimulationModel ;
    rdfs:label "WWTP1 ASM1 Model" ;
    wf:representsEntity ghent:WWTP1 ;
    wf:hasInput ghent:InflowRate_Input, ghent:InfluentCOD_Input ;
    wf:hasOutput ghent:EffluentCOD_Output, ghent:SludgeProduction_Output .

# ========== MODEL I/O (from information.ttl - REUSED!) ==========
ghent:InflowRate_Input a wf:ModelInput ;
    wf:parameterName "inflow_rate" ;
    wf:hasUnit "m³/d" ;
    wf:minValue "0.0"^^xsd:float .

ghent:InfluentCOD_Input a wf:ModelInput ;
    wf:parameterName "influent_cod" ;
    wf:hasUnit "mg/L" ;
    wf:minValue "0.0"^^xsd:float .

ghent:EffluentCOD_Output a wf:ModelOutput ;
    wf:parameterName "effluent_cod" ;
    wf:hasUnit "mg/L" .

ghent:SludgeProduction_Output a wf:ModelOutput ;
    wf:parameterName "sludge_production" ;
    wf:hasUnit "kg/d" .

# ========== SOFTWARE SYSTEM (from information.ttl - EXTENDED!) ==========
ghent:WWTP1_Software a wf:SoftwareSystem ;
    wf:apiEndpoint "http://localhost:8003"^^xsd:anyURI ;
    wf:apiVersion "1.0" .

# ========== COMPUTATIONAL AGENT (NEW!) ==========
ghent:WWTP1_Agent a wf:SimulationAgent ;
    rdfs:label "WWTP1 Agent" ;
    wf:implements ghent:WWTP1_Model ;
    wf:simulates ghent:WWTP1 ;
    wf:runsOn ghent:WWTP1_Software ;
    wf:hasCapability cap:DynamicSimulation, cap:MassBalance, cap:WaterQualityPrediction ;
    wf:offersOperation ghent:WWTP1_SimulateOp ;
    wf:agentVersion "1.0.0" .

# ========== OPERATION (NEW!) ==========
ghent:WWTP1_SimulateOp a wf:Operation ;
    rdfs:label "Simulate WWTP1" ;

    # REUSE same input/output objects as model!
    wf:requiresInput ghent:InflowRate_Input, ghent:InfluentCOD_Input ;
    wf:producesOutput ghent:EffluentCOD_Output, ghent:SludgeProduction_Output ;

    # Preconditions
    wf:hasPrecondition [
        a wf:Precondition ;
        wf:constrainsParameter ghent:InflowRate_Input ;
        wf:constraintExpression "inflow_rate > 0" ;
        rdfs:comment "Flow rate must be positive"
    ] ;

    wf:hasPrecondition [
        a wf:Precondition ;
        wf:constrainsParameter ghent:InfluentCOD_Input ;
        wf:constraintExpression "influent_cod >= 0" ;
        rdfs:comment "COD cannot be negative"
    ] ;

    # Postcondition
    wf:hasPostcondition [
        a wf:Postcondition ;
        wf:constraintExpression "mass_balance_satisfied(COD)" ;
        rdfs:comment "Mass balance maintained"
    ] ;

    # HTTP grounding
    wf:hasHTTPGrounding [
        a wf:HTTPGrounding ;
        wf:httpMethod "POST" ;
        wf:operationPath "/simulate" ;
        wf:requestFormat "application/json" ;
        wf:responseFormat "application/json" ;
        wf:requiresAuthentication "false"^^xsd:boolean
    ] ;

    # Performance
    wf:estimatedExecutionTime "2.5"^^xsd:float ;
    wf:computationalComplexity "O(n*m)" .
```

**Key Pattern**: Notice how `ghent:InflowRate_Input` is used by BOTH:
1. Model (`ghent:WWTP1_Model wf:hasInput ghent:InflowRate_Input`)
2. Operation (`ghent:WWTP1_SimulateOp wf:requiresInput ghent:InflowRate_Input`)

This enables queries like: "Which agents implement model X?" → automatic match via shared input objects.

---

## 6. Compositional Reasoning: SPARQL Queries

### 6.1 CQ-AG1: Agent Discovery

**Question**: "Which agents can simulate entity X?"

```sparql
PREFIX wf: <https://ugentbiomath.github.io/waterframe#>

SELECT ?agent ?model WHERE {
    ?agent wf:simulates :WWTP1 ;
           wf:implements ?model .
}
```

### 6.2 CQ-AG2: Capability-Based Discovery

**Question**: "Which agents provide water quality prediction capability?"

```sparql
PREFIX cap: <https://ugentbiomath.github.io/waterframe/capability#>

SELECT ?agent WHERE {
    ?agent wf:hasCapability cap:WaterQualityPrediction .
}
```

### 6.3 CQ-AG3: Compositional Data Flow

**Question**: "Given available data {FlowRate, Temperature}, which operations can execute?"

```sparql
PREFIX wf: <https://ugentbiomath.github.io/waterframe#>

SELECT ?agent ?operation WHERE {
    VALUES ?availableData { :FlowRate_Data :Temperature_Data }

    # Find operations where all required inputs are available
    ?agent wf:offersOperation ?operation .
    ?operation wf:requiresInput ?requiredInput .

    # Check NO required inputs are missing
    FILTER NOT EXISTS {
        ?operation wf:requiresInput ?missingInput .
        FILTER(?missingInput NOT IN (:FlowRate_Data, :Temperature_Data))
    }
}
```

### 6.4 CQ-AG4: Operation Sequencing

**Question**: "What sequence of operations transforms data α into information β?"

```sparql
PREFIX wf: <https://ugentbiomath.github.io/waterframe#>

# Find two-step chains (extend for longer chains)
SELECT ?op1 ?op2 ?intermediate WHERE {
    # Op1 requires starting data, produces intermediate
    ?op1 wf:requiresInput :DataAlpha ;
         wf:producesOutput ?intermediate .

    # Op2 requires intermediate, produces target
    ?op2 wf:requiresInput ?intermediate ;
         wf:producesOutput :DataBeta .

    # Verify data flow relationship
    ?op1 wf:dataFlowsTo ?op2 .
}
```

### 6.5 CQ-AG5: HTTP Invocation Discovery

**Question**: "How do I invoke operation O?"

```sparql
PREFIX wf: <https://ugentbiomath.github.io/waterframe#>

SELECT ?endpoint ?method ?path ?format WHERE {
    ?agent wf:offersOperation :OperationO ;
           wf:runsOn [ wf:apiEndpoint ?endpoint ] .

    :OperationO wf:hasHTTPGrounding [
        wf:httpMethod ?method ;
        wf:operationPath ?path ;
        wf:requestFormat ?format
    ] .
}
# Result: http://localhost:8003 POST /simulate application/json
```

---

## 7. Python Integration: Extending BaseWaterModel

### 7.1 Enhanced Turtle Generation

Add method to [base.py](case_studies/ghent/src/ghent_water/models/base.py):

```python
def generate_agent_ttl(self) -> str:
    """Generate agent-aware Turtle description extending base model TTL."""

    # Generate base model TTL (existing method)
    base_ttl = self.generate_ttl_description()

    # Generate software system instance
    software_ttl = f"""
# Software System
ghent:{self.entity_id}_Software a wf:SoftwareSystem ;
    wf:apiEndpoint <{self.api_endpoint}> ;
    wf:apiVersion "1.0" .
"""

    # Generate agent instance
    capabilities_refs = ", ".join(f"cap:{cap}" for cap in self.capabilities)

    agent_ttl = f"""
# Computational Agent
ghent:{self.entity_id}_Agent a wf:SimulationAgent ;
    rdfs:label "{self.entity_name} Agent" ;
    wf:implements ghent:{self.entity_id}_Model ;
    wf:simulates ghent:{self.entity_id} ;
    wf:runsOn ghent:{self.entity_id}_Software ;
    wf:hasCapability {capabilities_refs} ;
    wf:offersOperation ghent:{self.entity_id}_SimulateOp ;
    wf:agentVersion "1.0.0" .
"""

    # Generate operation instance
    input_refs = ", ".join(f"ghent:{inp['name']}_Input" for inp in self.inputs)
    output_refs = ", ".join(f"ghent:{out['name']}_Output" for out in self.outputs)

    operation_ttl = f"""
# Operation
ghent:{self.entity_id}_SimulateOp a wf:Operation ;
    rdfs:label "Simulate {self.entity_name}" ;
    wf:requiresInput {input_refs} ;
    wf:producesOutput {output_refs} ;
    wf:hasHTTPGrounding [
        a wf:HTTPGrounding ;
        wf:httpMethod "POST" ;
        wf:operationPath "/simulate" ;
        wf:requestFormat "application/json" ;
        wf:responseFormat "application/json" ;
        wf:requiresAuthentication "false"^^xsd:boolean
    ] .
"""

    return base_ttl + software_ttl + agent_ttl + operation_ttl
```

### 7.2 Update Orchestrator Registration

Modify [model_registry.py](case_studies/ghent/src/ghent_water/orchestrator/services/model_registry.py) to:
1. Accept agent-aware TTL from models
2. Load agent triples into ontology store
3. Enable agent-based SPARQL queries

---

## 8. File Structure

### 8.1 New Files

```
data/ontology/modules/
└── agents.ttl                     # NEW - this module (~300 lines)

case_studies/ghent/
└── src/ghent_water/models/
    └── base.py                     # MODIFY - add generate_agent_ttl()
```

### 8.2 Modified Files

```
data/ontology/
└── waterframe.ttl                 # ADD import for agents module

case_studies/ghent/src/ghent_water/
├── models/base.py                 # ADD generate_agent_ttl() method
└── orchestrator/services/
    └── model_registry.py          # UPDATE to handle agent TTL
```

---

## 9. Implementation Steps

### Step 1: Create agents.ttl Module

**File**: `data/ontology/modules/agents.ttl`

**Content**:
- Header with imports (information, capabilities, core/properties)
- 6 core classes (ComputationalAgent, Operation, ExecutionCondition subclasses, HTTPGrounding)
- 4 agent specializations (SimulationAgent, OptimizationAgent, etc.)
- 10 object properties (implements, simulates, runsOn, offersOperation, etc.)
- 9 datatype properties (httpMethod, operationPath, constraintExpression, etc.)
- Complete example instance (WWTP1_Agent)
- Documentation comments

**Estimated size**: ~350 lines

### Step 2: Update waterframe.ttl

**File**: `data/ontology/waterframe.ttl`

**Changes**:
- Add import statement: `owl:imports <https://ugentbiomath.github.io/waterframe/modules/agents>`
- Update competency question coverage comments

### Step 3: Extend BaseWaterModel

**File**: `case_studies/ghent/src/ghent_water/models/base.py`

**Changes**:
- Add `generate_agent_ttl()` method (as shown in section 7.1)
- Update `describe()` method to optionally include agent triples
- Add `operation_iri` property

### Step 4: Update Model Stubs

**Files**: All model stubs in `case_studies/ghent/src/ghent_water/models/stubs/`

**Changes**:
- Call `generate_agent_ttl()` instead of `generate_ttl_description()` during registration
- Optionally add preconditions for specific operations (e.g., "flow_rate > 0")

### Step 5: Update Model Registry

**File**: `case_studies/ghent/src/ghent_water/orchestrator/services/model_registry.py`

**Changes**:
- Update registration endpoint to accept and store agent TTL
- Add methods: `find_agents_by_capability()`, `find_operations_by_input()`, `get_operation_chain()`

### Step 6: Create Test SPARQL Queries

**File**: `case_studies/ghent/tests/test_agent_queries.sparql`

**Content**:
- Agent discovery tests (CQ-AG1, CQ-AG2)
- Compositional reasoning tests (CQ-AG3, CQ-AG4)
- HTTP invocation tests (CQ-AG5)

---

## 10. Validation Strategy

### 10.1 Ontology Validation

1. **Load agents.ttl in Protégé** - verify no OWL DL violations
2. **Run reasoner** (HermiT or Pellet) - check consistency
3. **Test SPARQL queries** - verify competency question coverage
4. **Check import closure** - ensure all referenced entities resolve

### 10.2 Python Integration Tests

```python
# Test 1: Agent TTL generation
def test_agent_ttl_generation():
    dwp = DrinkingWaterPlantStub(entity_id="DWP1", port=8001)
    agent_ttl = dwp.generate_agent_ttl()

    g = Graph()
    g.parse(data=agent_ttl, format="turtle")

    # Verify agent exists
    agent_uri = URIRef(f"{CASE_GHENT}DWP1_Agent")
    assert (agent_uri, RDF.type, WF.SimulationAgent) in g

    # Verify operation links to same inputs as model
    model_inputs = set(g.objects(URIRef(f"{CASE_GHENT}DWP1_Model"), WF.hasInput))
    operation = g.value(subject=agent_uri, predicate=WF.offersOperation)
    op_inputs = set(g.objects(operation, WF.requiresInput))
    assert model_inputs == op_inputs

# Test 2: Compositional query
def test_data_flow_query():
    result = sparql_engine.execute("""
        SELECT ?op1 ?op2 WHERE { ?op1 wf:dataFlowsTo ?op2 }
    """)
    assert len(result) >= 1  # At least one composition path exists
```

### 10.3 End-to-End Test

1. Start orchestrator and all 12 model services
2. Models register with agent-aware TTL
3. Query: "Which agents can compute effluent COD from inflow rate and influent COD?"
4. Verify: WWTP agents returned
5. Query: "What is the HTTP invocation for WWTP1 simulation?"
6. Verify: Correct endpoint + method returned
7. Invoke operation via HTTP using discovered endpoint
8. Verify: Simulation executes successfully

---

## 11. Documentation

### 11.1 Module Documentation

**File**: `docs/modules/agents.md`

**Sections**:
- Module overview and purpose
- Core concepts (Agent, Operation, ExecutionCondition, HTTPGrounding)
- Class hierarchy diagram
- Property reference
- SPARQL query examples
- Integration guide for model developers
- Competency questions answered

### 11.2 Tutorial

**File**: `docs/tutorials/agent_composition.md`

**Content**:
- How to describe an agent
- How to define operations with preconditions
- How to discover agents by capability
- How to query compositional workflows
- How to invoke operations via HTTP

---

## 12. Design Rationale

### Why Reuse ModelInput/Output?

**Decision**: Operations use **same objects** as models for inputs/outputs.

**Rationale**:
- Single source of truth for parameter specifications
- Automatic synchronization between model and agent views
- Enables query: "Which agents implement model X?" → inputs match automatically
- Follows DRY principle

**Alternative rejected**: Creating separate `OperationInput`/`OperationOutput` classes would duplicate information and break semantic linkage.

### Why Extend SoftwareSystem?

**Decision**: Use existing `wf:SoftwareSystem` class from information.ttl for API endpoints.

**Rationale**:
- SoftwareSystem already has `wf:apiEndpoint` and `wf:apiVersion` properties
- Agent `wf:runsOn` SoftwareSystem establishes deployment relationship
- Avoids creating redundant `ServiceInterface` class

**Alternative rejected**: Creating parallel `ServiceInterface` class would duplicate endpoint properties.

### Why HTTPGrounding as Separate Class?

**Decision**: Create `wf:HTTPGrounding` class for HTTP invocation details.

**Rationale**:
- HTTP details are implementation-specific (separate from operation semantics)
- Allows multiple groundings (HTTP, gRPC, WebSocket) for same operation
- Follows separation of concerns principle

### Why Preconditions as Blank Nodes?

**Decision**: Model preconditions as structured blank nodes with `constraintExpression` string.

**Rationale**:
- Balance between simplicity and structure
- Queryable via SPARQL
- Extensible (can add constraint type, severity later)
- Human-readable fallback via `rdfs:comment`

**Alternatives rejected**:
- Full logic language (OWL-S, SWRL) - too complex, requires reasoner
- Pure strings - not machine-processable, can't query

---

## 13. Critical Files to Modify

### High Priority

1. **data/ontology/modules/agents.ttl** (CREATE) - Core ontology module
2. **case_studies/ghent/src/ghent_water/models/base.py** (MODIFY) - Add agent TTL generation
3. **data/ontology/waterframe.ttl** (MODIFY) - Add import statement

### Medium Priority

4. **case_studies/ghent/src/ghent_water/orchestrator/services/model_registry.py** (MODIFY) - Handle agent TTL
5. **case_studies/ghent/src/ghent_water/models/stubs/*.py** (MODIFY) - Use new generation method

### Low Priority

6. **docs/modules/agents.md** (CREATE) - Documentation
7. **case_studies/ghent/tests/test_agent_queries.sparql** (CREATE) - Test queries

---

## 14. Success Criteria

✅ **Ontology Module**:
- agents.ttl loads without OWL DL violations
- Reasoner confirms consistency
- All 6 core classes and 19 properties defined
- Example instance validates

✅ **Python Integration**:
- BaseWaterModel.generate_agent_ttl() produces valid TTL
- All 12 model stubs register with agent triples
- Orchestrator loads agent data into RDF store

✅ **Compositional Queries**:
- CQ-AG1 to CQ-AG5 return correct results
- Property chain inference works for `dataFlowsTo`
- Agent discovery by capability functions correctly

✅ **HTTP Invocation**:
- SPARQL query returns correct endpoint + method
- Operation can be invoked via discovered HTTP details
- End-to-end workflow executes successfully

---

## 15. Timeline Estimate

- **Step 1-2** (Create agents.ttl, update waterframe.ttl): 2-3 hours
- **Step 3** (Extend BaseWaterModel): 1 hour
- **Step 4** (Update model stubs): 30 min
- **Step 5** (Update model registry): 1 hour
- **Step 6** (Create test queries): 1 hour
- **Validation & Testing**: 2 hours
- **Documentation**: 2 hours

**Total**: ~10 hours of implementation work

---

## 16. Future Extensions

**Phase 2 (Not in This Plan)**:
- Workflow composition engine (automatic agent chaining)
- Constraint solver for precondition satisfaction
- Performance optimization (caching, parallel execution)
- Security layer (authentication, authorization)
- Agent monitoring and health checks
- Dynamic agent discovery (registry service)

**Phase 3 (Advanced)**:
- Agent negotiation protocols
- Multi-objective optimization across agents
- Federated agent networks
- Event-driven agent coordination
