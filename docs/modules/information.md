# Module: information

Classes and properties for computational model metadata. Adapted from OntoCAPE model/mathematical_model and model/process_model patterns without importing due to OWL DL violations in original.

**Module URI:** `https://ugentbiomath.github.io/waterframe/modules/information`

**Source:** `ontology/modules/information.ttl`

**Total Entities:** 33

## Contents

- [Classes](#classes) (12)
- [Object Properties](#object-properties) (13)
- [Datatype Properties](#datatype-properties) (8)

---

## Classes

## DecisionVariable {#https___ugentbiomath.github.io_waterframe_decisionvariable}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#DecisionVariable`

### Labels

- Decision variable

### Description

A model variable that can be adjusted during optimization.

### Superclasses

- [ModelVariable](#https___ugentbiomath.github.io_waterframe_modelvariable)

### Related Entities

- [ModelVariable](#https___ugentbiomath.github.io_waterframe_modelvariable)


---

## InputVariable {#https___ugentbiomath.github.io_waterframe_inputvariable}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#InputVariable`

### Labels

- Input variable

### Description

An independent input variable to a model (boundary condition, driver).

### Superclasses

- [ModelVariable](#https___ugentbiomath.github.io_waterframe_modelvariable)

### Related Entities

- [ModelVariable](#https___ugentbiomath.github.io_waterframe_modelvariable)


---

## MathematicalModel {#https___ugentbiomath.github.io_waterframe_mathematicalmodel}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#MathematicalModel`

### Labels

- Mathematical model

### Description

A mathematical representation of a system using equations and parameters.

### Superclasses

- [ProcessModel](#https___ugentbiomath.github.io_waterframe_processmodel)

### Subclasses

- [SimulationModel](#https___ugentbiomath.github.io_waterframe_simulationmodel)

### Related Entities

- [ProcessModel](#https___ugentbiomath.github.io_waterframe_processmodel)
- [SimulationModel](#https___ugentbiomath.github.io_waterframe_simulationmodel)


---

## ModelInput {#https___ugentbiomath.github.io_waterframe_modelinput}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#ModelInput`

### Labels

- Model input

### Description

An input parameter to a computational model with associated metadata (name, unit, constraints).

### Superclasses

- [BFO_0000023](#https___ugentbiomath.github.io_waterframe_bfo_0000023)


---

## ModelOutput {#https___ugentbiomath.github.io_waterframe_modeloutput}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#ModelOutput`

### Labels

- Model output

### Description

An output parameter from a computational model with associated metadata.

### Superclasses

- [BFO_0000023](#https___ugentbiomath.github.io_waterframe_bfo_0000023)


---

## ModelVariable {#https___ugentbiomath.github.io_waterframe_modelvariable}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#ModelVariable`

### Labels

- Model variable

### Description

A variable in a mathematical model (state, input, or output).

### Superclasses

- [BFO_0000019](#https___ugentbiomath.github.io_waterframe_bfo_0000019)

### Subclasses

- [DecisionVariable](#https___ugentbiomath.github.io_waterframe_decisionvariable)
- [InputVariable](#https___ugentbiomath.github.io_waterframe_inputvariable)
- [OutputVariable](#https___ugentbiomath.github.io_waterframe_outputvariable)
- [Parameter](#https___ugentbiomath.github.io_waterframe_parameter)
- [StateVariable](#https___ugentbiomath.github.io_waterframe_statevariable)

### Related Entities

- [DecisionVariable](#https___ugentbiomath.github.io_waterframe_decisionvariable)
- [InputVariable](#https___ugentbiomath.github.io_waterframe_inputvariable)
- [OutputVariable](#https___ugentbiomath.github.io_waterframe_outputvariable)
- [Parameter](#https___ugentbiomath.github.io_waterframe_parameter)
- [StateVariable](#https___ugentbiomath.github.io_waterframe_statevariable)


---

## OutputVariable {#https___ugentbiomath.github.io_waterframe_outputvariable}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#OutputVariable`

### Labels

- Output variable

### Description

A computed output variable from a model.

### Superclasses

- [ModelVariable](#https___ugentbiomath.github.io_waterframe_modelvariable)

### Related Entities

- [ModelVariable](#https___ugentbiomath.github.io_waterframe_modelvariable)


---

## Parameter {#https___ugentbiomath.github.io_waterframe_parameter}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#Parameter`

### Labels

- Parameter

### Description

A constant parameter in a model (kinetic coefficient, yield coefficient, etc.).

### Superclasses

- [ModelVariable](#https___ugentbiomath.github.io_waterframe_modelvariable)

### Related Entities

- [ModelVariable](#https___ugentbiomath.github.io_waterframe_modelvariable)


---

## ProcessModel {#https___ugentbiomath.github.io_waterframe_processmodel}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#ProcessModel`

### Labels

- Process model

### Description

A computational model that represents the behavior of a process system. Adapted from OntoCAPE ProcessModel pattern.

### Superclasses

- [BFO_0000031](#https___ugentbiomath.github.io_waterframe_bfo_0000031)

### Subclasses

- [MathematicalModel](#https___ugentbiomath.github.io_waterframe_mathematicalmodel)

### Related Entities

- [MathematicalModel](#https___ugentbiomath.github.io_waterframe_mathematicalmodel)


---

## SimulationModel {#https___ugentbiomath.github.io_waterframe_simulationmodel}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#SimulationModel`

### Labels

- Simulation model

### Description

A dynamic simulation model of a water treatment process.

### Superclasses

- [MathematicalModel](#https___ugentbiomath.github.io_waterframe_mathematicalmodel)

### Related Entities

- [MathematicalModel](#https___ugentbiomath.github.io_waterframe_mathematicalmodel)


---

## SoftwareSystem {#https___ugentbiomath.github.io_waterframe_softwaresystem}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#SoftwareSystem`

### Labels

- Software system

### Description

A software system that implements one or more process models.

### Superclasses

- [BFO_0000031](#https___ugentbiomath.github.io_waterframe_bfo_0000031)


---

## StateVariable {#https___ugentbiomath.github.io_waterframe_statevariable}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#StateVariable`

### Labels

- State variable

### Description

A dependent variable in a model whose value changes over time based on system dynamics.

### Superclasses

- [ModelVariable](#https___ugentbiomath.github.io_waterframe_modelvariable)

### Related Entities

- [ModelVariable](#https___ugentbiomath.github.io_waterframe_modelvariable)


---

## Object Properties

## correspondsToVariable {#https___ugentbiomath.github.io_waterframe_correspondstovariable}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#correspondsToVariable`

### Labels

- corresponds to variable

### Description

Links a ModelInput or ModelOutput to the underlying ModelVariable

### Domains

- [n4ba5c5c8f6e2415098049d853d716846b1](#https___ugentbiomath.github.io_waterframe_n4ba5c5c8f6e2415098049d853d716846b1)

### Ranges

- ModelVariable

### Related Entities

- [ModelVariable](#https___ugentbiomath.github.io_waterframe_modelvariable)


---

## hasInput {#https___ugentbiomath.github.io_waterframe_hasinput}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasInput`

### Labels

- has input

### Description

Links a model to its input parameters

### Domains

- [ProcessModel](#https___ugentbiomath.github.io_waterframe_processmodel)

### Ranges

- ModelInput

### Related Entities

- [ModelInput](#https___ugentbiomath.github.io_waterframe_modelinput)
- [ProcessModel](#https___ugentbiomath.github.io_waterframe_processmodel)


---

## hasInputVariable {#https___ugentbiomath.github.io_waterframe_hasinputvariable}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasInputVariable`

### Labels

- has input variable

### Description

Links a model to its input variables

### Domains

- [SimulationModel](#https___ugentbiomath.github.io_waterframe_simulationmodel)

### Ranges

- InputVariable

### Related Entities

- [InputVariable](#https___ugentbiomath.github.io_waterframe_inputvariable)
- [SimulationModel](#https___ugentbiomath.github.io_waterframe_simulationmodel)


---

## hasModelVariable {#https___ugentbiomath.github.io_waterframe_hasmodelvariable}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasModelVariable`

### Labels

- has model variable

### Description

Links a model to its variables (state, input, output)

### Domains

- [MathematicalModel](#https___ugentbiomath.github.io_waterframe_mathematicalmodel)

### Ranges

- ModelVariable

### Related Entities

- [MathematicalModel](#https___ugentbiomath.github.io_waterframe_mathematicalmodel)
- [ModelVariable](#https___ugentbiomath.github.io_waterframe_modelvariable)


---

## hasOutput {#https___ugentbiomath.github.io_waterframe_hasoutput}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasOutput`

### Labels

- has output

### Description

Links a model to its output parameters

### Domains

- [ProcessModel](#https___ugentbiomath.github.io_waterframe_processmodel)

### Ranges

- ModelOutput

### Related Entities

- [ModelOutput](#https___ugentbiomath.github.io_waterframe_modeloutput)
- [ProcessModel](#https___ugentbiomath.github.io_waterframe_processmodel)


---

## hasOutputVariable {#https___ugentbiomath.github.io_waterframe_hasoutputvariable}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasOutputVariable`

### Labels

- has output variable

### Description

Links a model to its output variables

### Domains

- [SimulationModel](#https___ugentbiomath.github.io_waterframe_simulationmodel)

### Ranges

- OutputVariable

### Related Entities

- [OutputVariable](#https___ugentbiomath.github.io_waterframe_outputvariable)
- [SimulationModel](#https___ugentbiomath.github.io_waterframe_simulationmodel)


---

## hasParameter {#https___ugentbiomath.github.io_waterframe_hasparameter}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasParameter`

### Labels

- has parameter

### Description

Links a model to its parameters

### Domains

- [MathematicalModel](#https___ugentbiomath.github.io_waterframe_mathematicalmodel)

### Ranges

- Parameter

### Related Entities

- [MathematicalModel](#https___ugentbiomath.github.io_waterframe_mathematicalmodel)
- [Parameter](#https___ugentbiomath.github.io_waterframe_parameter)


---

## hasStateVariable {#https___ugentbiomath.github.io_waterframe_hasstatevariable}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasStateVariable`

### Labels

- has state variable

### Description

Links a model to its state variables

### Domains

- [SimulationModel](#https___ugentbiomath.github.io_waterframe_simulationmodel)

### Ranges

- StateVariable

### Related Entities

- [SimulationModel](#https___ugentbiomath.github.io_waterframe_simulationmodel)
- [StateVariable](#https___ugentbiomath.github.io_waterframe_statevariable)


---

## hasSubmodel {#https___ugentbiomath.github.io_waterframe_hassubmodel}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasSubmodel`

### Labels

- has submodel

### Description

Links a composite model to its constituent submodels

### Domains

- [ProcessModel](#https___ugentbiomath.github.io_waterframe_processmodel)

### Ranges

- ProcessModel

### Related Entities

- [ProcessModel](#https___ugentbiomath.github.io_waterframe_processmodel)


---

## hasUnit {#https___ugentbiomath.github.io_waterframe_hasunit}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasUnit`

### Labels

- has unit

### Description

Links a quantity to its unit of measurement (QUDT compatible)

### Domains

- [ModelVariable](#https___ugentbiomath.github.io_waterframe_modelvariable)

### Ranges

- Unit

### Related Entities

- [ModelVariable](#https___ugentbiomath.github.io_waterframe_modelvariable)


---

## implementedBy {#https___ugentbiomath.github.io_waterframe_implementedby}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#implementedBy`

### Labels

- implemented by

### Description

Links a model to the software or code that implements it

### Domains

- [ProcessModel](#https___ugentbiomath.github.io_waterframe_processmodel)

### Ranges

- SoftwareSystem

### Related Entities

- [ProcessModel](#https___ugentbiomath.github.io_waterframe_processmodel)
- [SoftwareSystem](#https___ugentbiomath.github.io_waterframe_softwaresystem)


---

## isSubmodelOf {#https___ugentbiomath.github.io_waterframe_issubmodelof}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#isSubmodelOf`

### Labels

- is submodel of

### Description

Inverse of hasSubmodel

### Domains

- [ProcessModel](#https___ugentbiomath.github.io_waterframe_processmodel)

### Ranges

- ProcessModel

### Inverse Properties

- [hasSubmodel](#https___ugentbiomath.github.io_waterframe_hassubmodel)

### Related Entities

- [ProcessModel](#https___ugentbiomath.github.io_waterframe_processmodel)
- [hasSubmodel](#https___ugentbiomath.github.io_waterframe_hassubmodel)


---

## representsEntity {#https___ugentbiomath.github.io_waterframe_representsentity}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#representsEntity`

### Labels

- represents entity

### Description

Links a model to the entity (system, process, or component) it represents

### Domains

- [ProcessModel](#https___ugentbiomath.github.io_waterframe_processmodel)

### Ranges

- BFO_0000040

### Related Entities

- [ProcessModel](#https___ugentbiomath.github.io_waterframe_processmodel)


---

## Datatype Properties

## apiEndpoint {#https___ugentbiomath.github.io_waterframe_apiendpoint}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#apiEndpoint`

### Labels

- API endpoint

### Description

The API endpoint URL for invoking the model

### Domains

- [SoftwareSystem](#https___ugentbiomath.github.io_waterframe_softwaresystem)

### Ranges

- anyURI

### Related Entities

- [SoftwareSystem](#https___ugentbiomath.github.io_waterframe_softwaresystem)


---

## apiVersion {#https___ugentbiomath.github.io_waterframe_apiversion}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#apiVersion`

### Labels

- API version

### Description

The version of the API or software

### Domains

- [SoftwareSystem](#https___ugentbiomath.github.io_waterframe_softwaresystem)

### Ranges

- string

### Related Entities

- [SoftwareSystem](#https___ugentbiomath.github.io_waterframe_softwaresystem)


---

## defaultValue {#https___ugentbiomath.github.io_waterframe_defaultvalue}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#defaultValue`

### Labels

- default value

### Description

The default value for a parameter or input

### Domains

- [n4ba5c5c8f6e2415098049d853d716846b10](#https___ugentbiomath.github.io_waterframe_n4ba5c5c8f6e2415098049d853d716846b10)

### Ranges

- double


---

## isDecisionVariable {#https___ugentbiomath.github.io_waterframe_isdecisionvariable}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#isDecisionVariable`

### Labels

- is decision variable

### Description

Boolean indicating if this parameter/variable can be used as a decision variable in optimization (true/false)

### Domains

- [ModelVariable](#https___ugentbiomath.github.io_waterframe_modelvariable)

### Ranges

- boolean

### Related Entities

- [ModelVariable](#https___ugentbiomath.github.io_waterframe_modelvariable)


---

## maxValue {#https___ugentbiomath.github.io_waterframe_maxvalue}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#maxValue`

### Labels

- maximum value

### Description

The maximum allowed value for a parameter or input

### Domains

- [n4ba5c5c8f6e2415098049d853d716846b7](#https___ugentbiomath.github.io_waterframe_n4ba5c5c8f6e2415098049d853d716846b7)

### Ranges

- double


---

## minValue {#https___ugentbiomath.github.io_waterframe_minvalue}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#minValue`

### Labels

- minimum value

### Description

The minimum allowed value for a parameter or input

### Domains

- [n4ba5c5c8f6e2415098049d853d716846b4](#https___ugentbiomath.github.io_waterframe_n4ba5c5c8f6e2415098049d853d716846b4)

### Ranges

- double


---

## numericalValue {#https___ugentbiomath.github.io_waterframe_numericalvalue}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#numericalValue`

### Labels

- numerical value

### Description

The numeric value of a parameter

### Domains

- [Parameter](#https___ugentbiomath.github.io_waterframe_parameter)

### Ranges

- double

### Related Entities

- [Parameter](#https___ugentbiomath.github.io_waterframe_parameter)


---

## parameterName {#https___ugentbiomath.github.io_waterframe_parametername}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#parameterName`

### Labels

- parameter name

### Description

The name/identifier of a model parameter

### Domains

- [ModelVariable](#https___ugentbiomath.github.io_waterframe_modelvariable)

### Ranges

- string

### Related Entities

- [ModelVariable](#https___ugentbiomath.github.io_waterframe_modelvariable)


---

