# Module: agents

Computational agent ontology module for waterFRAME. Enables semantic
    discovery of computational services, operation specification with preconditions/postconditions,
    and automatic compositional reasoning for workflow construction.

    Key Innovation: Extends existing waterFRAME patterns by adding an agent abstraction layer
    on top of ProcessModel, enabling service-oriented discovery and compositional queries like
    'Given data {α, β, γ} and agents {A, B, C}, can I compute information X?'

**Module URI:** `https://ugentbiomath.github.io/waterframe/modules/agents`

**Source:** `ontology/modules/agents.ttl`

**Total Entities:** 31

## Contents

- [Classes](#classes) (10)
- [Object Properties](#object-properties) (12)
- [Datatype Properties](#datatype-properties) (9)

---

## Classes

## ComputationalAgent {#https___ugentbiomath.github.io_waterframe_computationalagent}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#ComputationalAgent`

### Labels

- Computational agent

### Description

A software system providing computational services for water system
    simulation, analysis, or optimization. Distinct from physical actors (humans, organizations).

    Key distinction: ComputationalAgent is an informational entity (software/service) while
    wawo:Actor represents physical/institutional entities. These are disjoint categories.

    An agent implements one or more ProcessModels and offers Operations with defined
    inputs/outputs and execution conditions.

### Superclasses

- [BFO_0000031](#https___ugentbiomath.github.io_waterframe_bfo_0000031)

### Subclasses

- [DataTransformAgent](#https___ugentbiomath.github.io_waterframe_datatransformagent)
- [OptimizationAgent](#https___ugentbiomath.github.io_waterframe_optimizationagent)
- [ReasoningAgent](#https___ugentbiomath.github.io_waterframe_reasoningagent)
- [SimulationAgent](#https___ugentbiomath.github.io_waterframe_simulationagent)

### Related Entities

- [DataTransformAgent](#https___ugentbiomath.github.io_waterframe_datatransformagent)
- [OptimizationAgent](#https___ugentbiomath.github.io_waterframe_optimizationagent)
- [ReasoningAgent](#https___ugentbiomath.github.io_waterframe_reasoningagent)
- [SimulationAgent](#https___ugentbiomath.github.io_waterframe_simulationagent)


---

## DataTransformAgent {#https___ugentbiomath.github.io_waterframe_datatransformagent}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#DataTransformAgent`

### Labels

- Data transformation agent

### Description

An agent that transforms data between formats or coordinate systems.

### Superclasses

- [ComputationalAgent](#https___ugentbiomath.github.io_waterframe_computationalagent)

### Related Entities

- [ComputationalAgent](#https___ugentbiomath.github.io_waterframe_computationalagent)


---

## ExecutionCondition {#https___ugentbiomath.github.io_waterframe_executioncondition}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#ExecutionCondition`

### Labels

- Execution condition

### Description

A logical condition that constrains operation execution. Conditions can
    reference input parameters, output parameters, or state variables.

    Conditions are expressed as constraint expressions (strings) for flexibility, with optional
    structured links to the constrained parameters for queryability.

### Superclasses

- [BFO_0000023](#https___ugentbiomath.github.io_waterframe_bfo_0000023)

### Subclasses

- [Postcondition](#https___ugentbiomath.github.io_waterframe_postcondition)
- [Precondition](#https___ugentbiomath.github.io_waterframe_precondition)

### Related Entities

- [Postcondition](#https___ugentbiomath.github.io_waterframe_postcondition)
- [Precondition](#https___ugentbiomath.github.io_waterframe_precondition)


---

## HTTPGrounding {#https___ugentbiomath.github.io_waterframe_httpgrounding}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#HTTPGrounding`

### Labels

- HTTP grounding

### Description

Technical specification for invoking an operation via HTTP. Includes
    method (GET/POST/PUT/DELETE), path, content types, and authentication requirements.

    Separating grounding from operation semantics allows multiple invocation protocols
    (HTTP, gRPC, WebSocket) for the same operation.

### Superclasses

- [BFO_0000023](#https___ugentbiomath.github.io_waterframe_bfo_0000023)


---

## Operation {#https___ugentbiomath.github.io_waterframe_operation}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#Operation`

### Labels

- Computational operation

### Description

A specific computation with defined inputs, outputs, preconditions, and
    postconditions. Operations are process types that can be instantiated during execution.

    Operations reuse ModelInput/ModelOutput objects from the information module, ensuring
    consistency between model specifications and agent operations.

### Superclasses

- [BFO_0000015](#https___ugentbiomath.github.io_waterframe_bfo_0000015)


---

## OptimizationAgent {#https___ugentbiomath.github.io_waterframe_optimizationagent}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#OptimizationAgent`

### Labels

- Optimization agent

### Description

An agent that performs optimization to find optimal operating conditions or design parameters.

### Superclasses

- [ComputationalAgent](#https___ugentbiomath.github.io_waterframe_computationalagent)

### Related Entities

- [ComputationalAgent](#https___ugentbiomath.github.io_waterframe_computationalagent)


---

## Postcondition {#https___ugentbiomath.github.io_waterframe_postcondition}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#Postcondition`

### Labels

- Postcondition

### Description

A condition guaranteed to hold after successful operation execution.
    Postconditions typically assert invariants (e.g., 'mass_balance_satisfied(COD)').

### Superclasses

- [ExecutionCondition](#https___ugentbiomath.github.io_waterframe_executioncondition)

### Related Entities

- [ExecutionCondition](#https___ugentbiomath.github.io_waterframe_executioncondition)


---

## Precondition {#https___ugentbiomath.github.io_waterframe_precondition}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#Precondition`

### Labels

- Precondition

### Description

A condition that must hold before an operation can execute. Preconditions
    typically constrain input values (e.g., 'flow_rate > 0', 'timestep < maxTimestep').

### Superclasses

- [ExecutionCondition](#https___ugentbiomath.github.io_waterframe_executioncondition)

### Related Entities

- [ExecutionCondition](#https___ugentbiomath.github.io_waterframe_executioncondition)


---

## ReasoningAgent {#https___ugentbiomath.github.io_waterframe_reasoningagent}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#ReasoningAgent`

### Labels

- Reasoning agent

### Description

An agent that performs logical reasoning or knowledge-based inference.

### Superclasses

- [ComputationalAgent](#https___ugentbiomath.github.io_waterframe_computationalagent)

### Related Entities

- [ComputationalAgent](#https___ugentbiomath.github.io_waterframe_computationalagent)


---

## SimulationAgent {#https___ugentbiomath.github.io_waterframe_simulationagent}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#SimulationAgent`

### Labels

- Simulation agent

### Description

An agent that performs dynamic or steady-state simulation of water systems.

### Superclasses

- [ComputationalAgent](#https___ugentbiomath.github.io_waterframe_computationalagent)

### Related Entities

- [ComputationalAgent](#https___ugentbiomath.github.io_waterframe_computationalagent)


---

## Object Properties

## acceptsOptionalInput {#https___ugentbiomath.github.io_waterframe_acceptsoptionalinput}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#acceptsOptionalInput`

### Labels

- accepts optional input

### Description

Links an operation to an optional input parameter that can be provided but is not required

### Domains

- [Operation](#https___ugentbiomath.github.io_waterframe_operation)

### Ranges

- ModelInput

### Related Entities

- [ModelInput](#https___ugentbiomath.github.io_waterframe_modelinput)
- [Operation](#https___ugentbiomath.github.io_waterframe_operation)


---

## constrainsParameter {#https___ugentbiomath.github.io_waterframe_constrainsparameter}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#constrainsParameter`

### Labels

- constrains parameter

### Description

Links a condition to the parameter(s) it constrains

### Domains

- [ExecutionCondition](#https___ugentbiomath.github.io_waterframe_executioncondition)

### Ranges

- nd89c8debfb4f4f47b7df79c85391d5d5b1

### Related Entities

- [ExecutionCondition](#https___ugentbiomath.github.io_waterframe_executioncondition)


---

## dataFlowsTo {#https___ugentbiomath.github.io_waterframe_dataflowsto}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#dataFlowsTo`

### Labels

- data flows to

### Description

Indicates that output from this operation can serve as input to the target operation.

    This property is inferred via property chain axiom: if operation A produces output X AND
    operation B requires input X, THEN A dataFlowsTo B. This enables automatic discovery of
    composable operation sequences.

### Domains

- [Operation](#https___ugentbiomath.github.io_waterframe_operation)

### Ranges

- Operation

### Related Entities

- [Operation](#https___ugentbiomath.github.io_waterframe_operation)


---

## hasHTTPGrounding {#https___ugentbiomath.github.io_waterframe_hashttpgrounding}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasHTTPGrounding`

### Labels

- has HTTP grounding

### Description

Links an operation to its HTTP invocation specification

### Domains

- [Operation](#https___ugentbiomath.github.io_waterframe_operation)

### Ranges

- HTTPGrounding

### Related Entities

- [HTTPGrounding](#https___ugentbiomath.github.io_waterframe_httpgrounding)
- [Operation](#https___ugentbiomath.github.io_waterframe_operation)


---

## hasPostcondition {#https___ugentbiomath.github.io_waterframe_haspostcondition}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasPostcondition`

### Labels

- has postcondition

### Description

Links an operation to a postcondition guaranteed after successful execution

### Domains

- [Operation](#https___ugentbiomath.github.io_waterframe_operation)

### Ranges

- Postcondition

### Related Entities

- [Operation](#https___ugentbiomath.github.io_waterframe_operation)
- [Postcondition](#https___ugentbiomath.github.io_waterframe_postcondition)


---

## hasPrecondition {#https___ugentbiomath.github.io_waterframe_hasprecondition}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasPrecondition`

### Labels

- has precondition

### Description

Links an operation to a precondition that must hold before execution

### Domains

- [Operation](#https___ugentbiomath.github.io_waterframe_operation)

### Ranges

- Precondition

### Related Entities

- [Operation](#https___ugentbiomath.github.io_waterframe_operation)
- [Precondition](#https___ugentbiomath.github.io_waterframe_precondition)


---

## implements {#https___ugentbiomath.github.io_waterframe_implements}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#implements`

### Labels

- implements

### Description

Links an agent to the ProcessModel it implements

### Domains

- [ComputationalAgent](#https___ugentbiomath.github.io_waterframe_computationalagent)

### Ranges

- ProcessModel

### Related Entities

- [ComputationalAgent](#https___ugentbiomath.github.io_waterframe_computationalagent)
- [ProcessModel](#https___ugentbiomath.github.io_waterframe_processmodel)


---

## offersOperation {#https___ugentbiomath.github.io_waterframe_offersoperation}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#offersOperation`

### Labels

- offers operation

### Description

Links an agent to the operations it provides as services

### Domains

- [ComputationalAgent](#https___ugentbiomath.github.io_waterframe_computationalagent)

### Ranges

- Operation

### Related Entities

- [ComputationalAgent](#https___ugentbiomath.github.io_waterframe_computationalagent)
- [Operation](#https___ugentbiomath.github.io_waterframe_operation)


---

## producesOutput {#https___ugentbiomath.github.io_waterframe_producesoutput}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#producesOutput`

### Labels

- produces output

### Description

Links an operation to an output it produces upon successful execution

### Domains

- [Operation](#https___ugentbiomath.github.io_waterframe_operation)

### Ranges

- ModelOutput

### Related Entities

- [ModelOutput](#https___ugentbiomath.github.io_waterframe_modeloutput)
- [Operation](#https___ugentbiomath.github.io_waterframe_operation)


---

## requiresInput {#https___ugentbiomath.github.io_waterframe_requiresinput}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#requiresInput`

### Labels

- requires input

### Description

Links an operation to a required input parameter. All required inputs must be provided for execution.

### Domains

- [Operation](#https___ugentbiomath.github.io_waterframe_operation)

### Ranges

- ModelInput

### Related Entities

- [ModelInput](#https___ugentbiomath.github.io_waterframe_modelinput)
- [Operation](#https___ugentbiomath.github.io_waterframe_operation)


---

## runsOn {#https___ugentbiomath.github.io_waterframe_runson}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#runsOn`

### Labels

- runs on

### Description

Links an agent to the SoftwareSystem it executes on (deployment relationship)

### Domains

- [ComputationalAgent](#https___ugentbiomath.github.io_waterframe_computationalagent)

### Ranges

- SoftwareSystem

### Related Entities

- [ComputationalAgent](#https___ugentbiomath.github.io_waterframe_computationalagent)
- [SoftwareSystem](#https___ugentbiomath.github.io_waterframe_softwaresystem)


---

## simulates {#https___ugentbiomath.github.io_waterframe_simulates}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#simulates`

### Labels

- simulates

### Description

Links an agent to the physical entity (tank, treatment plant, pipe) it simulates

### Domains

- [ComputationalAgent](#https___ugentbiomath.github.io_waterframe_computationalagent)

### Ranges

- BFO_0000040

### Related Entities

- [ComputationalAgent](#https___ugentbiomath.github.io_waterframe_computationalagent)


---

## Datatype Properties

## agentVersion {#https___ugentbiomath.github.io_waterframe_agentversion}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#agentVersion`

### Labels

- agent version

### Description

Version identifier for the agent implementation

### Domains

- [ComputationalAgent](#https___ugentbiomath.github.io_waterframe_computationalagent)

### Ranges

- string

### Related Entities

- [ComputationalAgent](#https___ugentbiomath.github.io_waterframe_computationalagent)


---

## computationalComplexity {#https___ugentbiomath.github.io_waterframe_computationalcomplexity}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#computationalComplexity`

### Labels

- computational complexity

### Description

Computational complexity in Big-O notation (e.g., 'O(n²)', 'O(n*m)')

### Domains

- [Operation](#https___ugentbiomath.github.io_waterframe_operation)

### Ranges

- string

### Related Entities

- [Operation](#https___ugentbiomath.github.io_waterframe_operation)


---

## constraintExpression {#https___ugentbiomath.github.io_waterframe_constraintexpression}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#constraintExpression`

### Labels

- constraint expression

### Description

A constraint expression as a string (e.g., 'BOD > 0', 'timestep < maxTimestep').

    Balance between simplicity and structure: queryable via SPARQL, human-readable,
    extensible for future constraint types.

### Domains

- [ExecutionCondition](#https___ugentbiomath.github.io_waterframe_executioncondition)

### Ranges

- string

### Related Entities

- [ExecutionCondition](#https___ugentbiomath.github.io_waterframe_executioncondition)


---

## estimatedExecutionTime {#https___ugentbiomath.github.io_waterframe_estimatedexecutiontime}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#estimatedExecutionTime`

### Labels

- estimated execution time

### Description

Estimated execution time in seconds

### Domains

- [Operation](#https___ugentbiomath.github.io_waterframe_operation)

### Ranges

- float

### Related Entities

- [Operation](#https___ugentbiomath.github.io_waterframe_operation)


---

## httpMethod {#https___ugentbiomath.github.io_waterframe_httpmethod}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#httpMethod`

### Labels

- HTTP method

### Description

The HTTP method for operation invocation (GET, POST, PUT, DELETE, PATCH)

### Domains

- [HTTPGrounding](#https___ugentbiomath.github.io_waterframe_httpgrounding)

### Ranges

- string

### Related Entities

- [HTTPGrounding](#https___ugentbiomath.github.io_waterframe_httpgrounding)


---

## operationPath {#https___ugentbiomath.github.io_waterframe_operationpath}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#operationPath`

### Labels

- operation path

### Description

The relative path for the operation (e.g., '/simulate', '/optimize')

### Domains

- [HTTPGrounding](#https___ugentbiomath.github.io_waterframe_httpgrounding)

### Ranges

- string

### Related Entities

- [HTTPGrounding](#https___ugentbiomath.github.io_waterframe_httpgrounding)


---

## requestFormat {#https___ugentbiomath.github.io_waterframe_requestformat}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#requestFormat`

### Labels

- request format

### Description

The content type for request body (e.g., 'application/json', 'application/xml')

### Domains

- [HTTPGrounding](#https___ugentbiomath.github.io_waterframe_httpgrounding)

### Ranges

- string

### Related Entities

- [HTTPGrounding](#https___ugentbiomath.github.io_waterframe_httpgrounding)


---

## requiresAuthentication {#https___ugentbiomath.github.io_waterframe_requiresauthentication}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#requiresAuthentication`

### Labels

- requires authentication

### Description

Whether the operation requires authentication

### Domains

- [HTTPGrounding](#https___ugentbiomath.github.io_waterframe_httpgrounding)

### Ranges

- boolean

### Related Entities

- [HTTPGrounding](#https___ugentbiomath.github.io_waterframe_httpgrounding)


---

## responseFormat {#https___ugentbiomath.github.io_waterframe_responseformat}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#responseFormat`

### Labels

- response format

### Description

The content type for response body (e.g., 'application/json')

### Domains

- [HTTPGrounding](#https___ugentbiomath.github.io_waterframe_httpgrounding)

### Ranges

- string

### Related Entities

- [HTTPGrounding](#https___ugentbiomath.github.io_waterframe_httpgrounding)


---

