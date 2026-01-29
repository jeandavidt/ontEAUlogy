# Module: capabilities

Capability taxonomy for computational models. Defines what models can do (simulation types, analysis types, etc.).

**Module URI:** `https://ugentbiomath.github.io/waterframe/modules/capabilities`

**Source:** `ontology/modules/capabilities.ttl`

**Total Entities:** 20

## Contents

- [Classes](#classes) (15)
- [Object Properties](#object-properties) (4)
- [Datatype Properties](#datatype-properties) (1)

---

## Classes

## BiokineticModeling {#https___ugentbiomath.github.io_waterframe_capability_biokineticmodeling}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe/capability#BiokineticModeling`

### Labels

- Biokinetic modeling

### Description

The ability to model biological kinetic processes.

### Superclasses

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)

### Related Entities

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)


---

## CostEstimation {#https___ugentbiomath.github.io_waterframe_capability_costestimation}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe/capability#CostEstimation`

### Labels

- Cost estimation

### Description

The ability to estimate costs (capital, operational).

### Superclasses

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)

### Related Entities

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)


---

## DynamicSimulation {#https___ugentbiomath.github.io_waterframe_capability_dynamicsimulation}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe/capability#DynamicSimulation`

### Labels

- Dynamic simulation

### Description

The ability to simulate a system with time-varying behavior.

### Superclasses

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)

### Related Entities

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)


---

## EnergyBalance {#https___ugentbiomath.github.io_waterframe_capability_energybalance}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe/capability#EnergyBalance`

### Labels

- Energy balance

### Description

The ability to perform energy balance calculations.

### Superclasses

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)

### Related Entities

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)


---

## HydraulicModeling {#https___ugentbiomath.github.io_waterframe_capability_hydraulicmodeling}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe/capability#HydraulicModeling`

### Labels

- Hydraulic modeling

### Description

The ability to model hydraulic behavior (flow rates, pressures).

### Superclasses

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)

### Related Entities

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)


---

## MassBalance {#https___ugentbiomath.github.io_waterframe_capability_massbalance}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe/capability#MassBalance`

### Labels

- Mass balance

### Description

The ability to perform mass balance calculations.

### Superclasses

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)

### Related Entities

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)


---

## ModelCapability {#https___ugentbiomath.github.io_waterframe_modelcapability}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#ModelCapability`

### Labels

- Model capability

### Description

A capability that a model or software system can perform.

### Superclasses

- [BFO_0000016](#https___ugentbiomath.github.io_waterframe_bfo_0000016)

### Subclasses

- [BiokineticModeling](#https___ugentbiomath.github.io_waterframe_biokineticmodeling)
- [CostEstimation](#https___ugentbiomath.github.io_waterframe_costestimation)
- [DynamicSimulation](#https___ugentbiomath.github.io_waterframe_dynamicsimulation)
- [EnergyBalance](#https___ugentbiomath.github.io_waterframe_energybalance)
- [HydraulicModeling](#https___ugentbiomath.github.io_waterframe_hydraulicmodeling)
- [MassBalance](#https___ugentbiomath.github.io_waterframe_massbalance)
- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)
- [NutrientRemoval](#https___ugentbiomath.github.io_waterframe_nutrientremoval)
- [Optimization](#https___ugentbiomath.github.io_waterframe_optimization)
- [SensitivityAnalysis](#https___ugentbiomath.github.io_waterframe_sensitivityanalysis)
- [SludgeProduction](#https___ugentbiomath.github.io_waterframe_sludgeproduction)
- [SteadyStateSimulation](#https___ugentbiomath.github.io_waterframe_steadystatesimulation)
- [UncertaintyQuantification](#https___ugentbiomath.github.io_waterframe_uncertaintyquantification)
- [WaterQualityPrediction](#https___ugentbiomath.github.io_waterframe_waterqualityprediction)

### Related Entities

- [BiokineticModeling](#https___ugentbiomath.github.io_waterframe_capability_biokineticmodeling)
- [CostEstimation](#https___ugentbiomath.github.io_waterframe_capability_costestimation)
- [DynamicSimulation](#https___ugentbiomath.github.io_waterframe_capability_dynamicsimulation)
- [EnergyBalance](#https___ugentbiomath.github.io_waterframe_capability_energybalance)
- [HydraulicModeling](#https___ugentbiomath.github.io_waterframe_capability_hydraulicmodeling)
- [MassBalance](#https___ugentbiomath.github.io_waterframe_capability_massbalance)
- [ModelCapability](#https___ugentbiomath.github.io_waterframe_capability_modelcapability)
- [NutrientRemoval](#https___ugentbiomath.github.io_waterframe_capability_nutrientremoval)
- [Optimization](#https___ugentbiomath.github.io_waterframe_capability_optimization)
- [SensitivityAnalysis](#https___ugentbiomath.github.io_waterframe_capability_sensitivityanalysis)
- [SludgeProduction](#https___ugentbiomath.github.io_waterframe_capability_sludgeproduction)
- [SteadyStateSimulation](#https___ugentbiomath.github.io_waterframe_capability_steadystatesimulation)
- [UncertaintyQuantification](#https___ugentbiomath.github.io_waterframe_capability_uncertaintyquantification)
- [WaterQualityPrediction](#https___ugentbiomath.github.io_waterframe_capability_waterqualityprediction)


---

## ModelCapability {#https___ugentbiomath.github.io_waterframe_capability_modelcapability}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe/capability#ModelCapability`

### Labels

- Model capability (capability namespace)

### Description

Base class for specific capability types.

### Superclasses

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)

### Related Entities

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)


---

## NutrientRemoval {#https___ugentbiomath.github.io_waterframe_capability_nutrientremoval}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe/capability#NutrientRemoval`

### Labels

- Nutrient removal modeling

### Description

The ability to model nitrogen and phosphorus removal.

### Superclasses

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)

### Related Entities

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)


---

## Optimization {#https___ugentbiomath.github.io_waterframe_capability_optimization}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe/capability#Optimization`

### Labels

- Optimization

### Description

The ability to find optimal parameter values or operating conditions.

### Superclasses

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)

### Related Entities

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)


---

## SensitivityAnalysis {#https___ugentbiomath.github.io_waterframe_capability_sensitivityanalysis}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe/capability#SensitivityAnalysis`

### Labels

- Sensitivity analysis

### Description

The ability to analyze how changes in inputs affect outputs.

### Superclasses

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)

### Related Entities

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)


---

## SludgeProduction {#https___ugentbiomath.github.io_waterframe_capability_sludgeproduction}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe/capability#SludgeProduction`

### Labels

- Sludge production modeling

### Description

The ability to predict sludge production rates.

### Superclasses

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)

### Related Entities

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)


---

## SteadyStateSimulation {#https___ugentbiomath.github.io_waterframe_capability_steadystatesimulation}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe/capability#SteadyStateSimulation`

### Labels

- Steady-state simulation

### Description

The ability to simulate a system under steady-state conditions (no change over time).

### Superclasses

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)

### Related Entities

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)


---

## UncertaintyQuantification {#https___ugentbiomath.github.io_waterframe_capability_uncertaintyquantification}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe/capability#UncertaintyQuantification`

### Labels

- Uncertainty quantification

### Description

The ability to quantify uncertainty in model predictions.

### Superclasses

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)

### Related Entities

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)


---

## WaterQualityPrediction {#https___ugentbiomath.github.io_waterframe_capability_waterqualityprediction}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe/capability#WaterQualityPrediction`

### Labels

- Water quality prediction

### Description

The ability to predict water quality parameters.

### Superclasses

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)

### Related Entities

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)


---

## Object Properties

## hasCapability {#https___ugentbiomath.github.io_waterframe_hascapability}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasCapability`

### Labels

- has capability

### Description

Links a model or software system to its capabilities

### Domains

- [n140511c042fe43ed9af3c69e530d3417b1](#https___ugentbiomath.github.io_waterframe_n140511c042fe43ed9af3c69e530d3417b1)

### Ranges

- ModelCapability

### Related Entities

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)


---

## implementedByModel {#https___ugentbiomath.github.io_waterframe_capability_implementedbymodel}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe/capability#implementedByModel`

### Labels

- implemented by model

### Description

Links a capability to the model that implements it

### Domains

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)

### Ranges

- ProcessModel

### Related Entities

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)
- [ProcessModel](#https___ugentbiomath.github.io_waterframe_processmodel)


---

## producesOutputs {#https___ugentbiomath.github.io_waterframe_capability_producesoutputs}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe/capability#producesOutputs`

### Labels

- produces outputs

### Description

The output variables produced by this capability

### Domains

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)

### Ranges

- ModelOutput

### Related Entities

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)
- [ModelOutput](#https___ugentbiomath.github.io_waterframe_modeloutput)


---

## requiredInputs {#https___ugentbiomath.github.io_waterframe_capability_requiredinputs}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe/capability#requiredInputs`

### Labels

- required inputs

### Description

The input variables required to perform this capability

### Domains

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)

### Ranges

- ModelInput

### Related Entities

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)
- [ModelInput](#https___ugentbiomath.github.io_waterframe_modelinput)


---

## Datatype Properties

## description {#https___ugentbiomath.github.io_waterframe_capability_description}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe/capability#description`

### Labels

- description

### Description

A textual description of the capability

### Domains

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)

### Ranges

- string

### Related Entities

- [ModelCapability](#https___ugentbiomath.github.io_waterframe_modelcapability)


---

