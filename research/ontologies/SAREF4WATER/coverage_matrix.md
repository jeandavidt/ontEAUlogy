# SAREF4WATER Coverage Matrix

## Competency Questions Coverage Analysis

### Legend
- ✓ Full Support: Ontology provides complete support for the requirement
- ◐ Partial Support: Ontology provides limited or indirect support
- ✗ No Support: Ontology does not address the requirement

---

## System Topology

| CQ ID | Competency Question | Support | Notes |
|-------|---------------------|---------|-------|
| CQ1 | What are all the nodes (plants, sources, junctions, sinks) in a given catchment? | ◐ Partial | Has WaterAsset class with subclasses (Dam, Reservoir, CatchmentWell, GroundWaterWell) but no treatment plant class, no junction class, no sink class, no catchment class |
| CQ2 | What flows connect Node A to Node B? | ✗ None | Has Pipe and Aqueduct classes for infrastructure but no properties to represent flow direction, source, or destination |
| CQ3 | What are the possible input sources for Plant X? | ✗ None | No properties to represent connectivity or flow relationships between assets |
| CQ4 | What downstream nodes receive effluent from Plant X? | ✗ None | No upstream/downstream relationship properties |
| CQ5 | What is the complete flow path from Source S to Sink K? | ✗ None | No transitive connectivity properties; cannot represent or query flow paths |

**Summary**: System topology support is severely limited. While basic asset types exist, there is no way to represent the network structure or flow relationships that are essential for catchment-scale modeling.

---

## Treatment Configuration

| CQ ID | Competency Question | Support | Notes |
|-------|---------------------|---------|-------|
| CQ6 | What unit processes comprise the treatment train at Plant X? | ✗ None | No representation of unit processes or treatment components |
| CQ7 | What is the sequence/topology of unit processes within Plant X? | ✗ None | No treatment train structure or sequencing |
| CQ8 | What treatment technologies are available for a given contaminant removal objective? | ✗ None | No treatment technology classification or removal capabilities |
| CQ9 | What is the design capacity of Unit Process U? | ✗ None | No capacity property for assets or processes; has Capacity as a named individual Property but not as a data property |

**Summary**: Treatment configuration is completely absent. The ontology cannot represent treatment plants as collections of unit processes with specific configurations.

---

## Water Quality and Fitness-for-Purpose

| CQ ID | Competency Question | Support | Notes |
|-------|---------------------|---------|-------|
| CQ10 | What quality parameters characterize the water at Node N? | ✓ Full | Has WaterProperty class with Physical and Chemical subclasses; includes named individuals for common parameters (pH, Turbidity, Hardness, Conductance, Temperature) |
| CQ11 | What are the regulatory limits for Parameter P for Reuse Category R? | ✗ None | No representation of regulatory limits, standards, or thresholds |
| CQ12 | Does the effluent quality at Plant X meet the requirements for agricultural reuse? | ✗ None | No fit-for-purpose categories, no reuse classifications, no requirement representation |
| CQ13 | What contaminants are present in Source S above threshold T? | ◐ Partial | Can represent measurements via SAREF Measurement class but no threshold/limit representation; can filter by value in SPARQL but thresholds are not encoded in ontology |

**Summary**: Water quality parameters are well represented via SAREF's measurement pattern, but regulatory compliance and fit-for-purpose classification are entirely missing.

---

## Source/Stream Classification

| CQ ID | Competency Question | Support | Notes |
|-------|---------------------|---------|-------|
| CQ14 | Is Stream S classified as greywater or blackwater? | ✗ None | No wastewater source classification scheme |
| CQ15 | What sources in the catchment are classified as fit-for-purpose Category C? | ✗ None | No fit-for-purpose classification or water reuse categories |
| CQ16 | What treatment is required to upgrade water from Quality Class Q1 to Q2? | ✗ None | No quality classes, no treatment requirements representation |

**Summary**: Water reuse and source classification concepts are completely absent.

---

## Model Metadata

| CQ ID | Competency Question | Support | Notes |
|-------|---------------------|---------|-------|
| CQ17 | What computational model is associated with Unit Process U? | ✗ None | No representation of computational models |
| CQ18 | What are the input variables for Model M? | ✗ None | No model input/output specification |
| CQ19 | What are the output variables for Model M? | ✗ None | No model variable representation |
| CQ20 | Which parameters of Model M are fixed vs. manipulable (decision variables)? | ✗ None | No parameter classification |
| CQ21 | What is the valid range for Parameter P in Model M? | ✗ None | No parameter range constraints |
| CQ22 | How is Model M invoked? (API endpoint, function signature, agent reference) | ✗ None | No invocation metadata |
| CQ23 | What mass/quality balances does Model M compute? | ✗ None | No balance equations representation |
| CQ24 | What time resolution does Model M operate at? (steady-state, dynamic, event-based) | ✗ None | No temporal resolution metadata |

**Summary**: Model metadata is completely absent. The ontology is focused on IoT device management, not process modeling.

---

## Optimization Agent Metadata

| CQ ID | Competency Question | Support | Notes |
|-------|---------------------|---------|-------|
| CQ25 | What optimization agents are available in the system? | ✗ None | No agent representation |
| CQ26 | What objective function types can Agent A handle? | ✗ None | No agent capability description |
| CQ27 | What constraint types can Agent A handle? | ✗ None | No constraint type taxonomy |
| CQ28 | What solvers does Agent A have access to? | ✗ None | No solver metadata |
| CQ29 | How is Agent A invoked? | ✗ None | No agent invocation protocol |

**Summary**: Optimization and agent concepts are completely absent.

---

## Optimization Problem Formulation

| CQ ID | Competency Question | Support | Notes |
|-------|---------------------|---------|-------|
| CQ30 | For a given objective, which nodes have relevant decision variables? | ✗ None | No decision variable classification |
| CQ31 | What constraints link the outputs of upstream nodes to the inputs of downstream nodes? | ✗ None | No constraint representation or node connectivity |
| CQ32 | What is the set of decision variables for a catchment-wide source selection problem? | ✗ None | No optimization problem structure |
| CQ33 | What models must be invoked to evaluate a candidate solution? | ✗ None | No model orchestration metadata |

**Summary**: Optimization problem formulation is completely absent.

---

## Provenance and Metadata

| CQ ID | Competency Question | Support | Notes |
|-------|---------------------|---------|-------|
| CQ34 | When was the model/data for Node N last updated? | ◐ Partial | SAREF Measurement has hasTimeStamp but no general update tracking for assets or models |
| CQ35 | What is the source of the regulatory limits for Parameter P? | ✗ None | No provenance representation beyond basic SAREF measurement attribution |
| CQ36 | Who is responsible for maintaining Model M? | ✗ None | No responsibility or ownership metadata |

**Summary**: Minimal provenance support via SAREF's measurement timestamp; no broader data governance or model maintenance tracking.

---

## What SAREF4WATER Actually Supports

While SAREF4WATER fails to address most of the competency questions for agent-based optimization over water treatment networks, it does provide capabilities in the following areas:

### 1. IoT Device Management (Sensors and Actuators)

| Capability | Support | Notes |
|------------|---------|-------|
| Sensor classification | ✓ Full | CapacitySensor, TankLevelSensor, WaterQualitySensor, WaterMeter subclasses |
| Actuator classification | ✓ Full | Pump, Valve, PressureRegulator subclasses |
| Device metadata | ✓ Full | Manufacturer, model, firmware version, hardware version, fabrication number |
| Device-to-infrastructure association | ✓ Full | usedIn property links devices to WaterInfrastructure |
| Device-to-asset management | ✓ Full | manageWaterAsset / isManagedBy properties |

### 2. Measurement and Properties

| Capability | Support | Notes |
|------------|---------|-------|
| Water quality properties | ✓ Full | Physical and Chemical property subclasses with named individuals |
| Measurements | ✓ Full | Via SAREF Measurement class with value, unit, timestamp, device attribution |
| Property-sensor mapping | ✓ Full | measuresProperty links sensors to properties they measure |
| Generic properties | ✓ Full | Flow rates, levels, capacity, volume, power, temperature |

### 3. Infrastructure Composition

| Capability | Support | Notes |
|------------|---------|-------|
| Infrastructure types | ◐ Partial | Pipe, Aqueduct, StorageTank classes but no comprehensive classification |
| Asset types | ◐ Partial | Dam, Reservoir, CatchmentWell, GroundWaterWell but missing treatment plants, junctions, sinks |
| Composition relationships | ✓ Full | isComposedBy property for WaterInfrastructure |

### 4. City-Level Indicators

| Capability | Support | Notes |
|------------|---------|-------|
| Indicator concept | ✓ Full | Indicator class for city-level metrics |
| City association | ✓ Full | assignedTo property links indicators to cities |
| Asset indicators | ✓ Full | hasIndicator property links assets to performance indicators |

### 5. Spatial Representation

| Capability | Support | Notes |
|------------|---------|-------|
| Geometry | ◐ Partial | References GeoSPARQL (hasGeometry, sfContains, sfWithin) but doesn't import it |
| Geographic location | ◐ Partial | References WGS84 (location, lat, long, alt) but doesn't import it |

---

## Overall Coverage Summary

| Category | Questions | Fully Supported | Partially Supported | Not Supported | Coverage % |
|----------|-----------|-----------------|---------------------|---------------|------------|
| System Topology | 5 | 0 | 1 | 4 | 10% |
| Treatment Configuration | 4 | 0 | 0 | 4 | 0% |
| Water Quality | 4 | 1 | 1 | 2 | 37.5% |
| Source Classification | 3 | 0 | 0 | 3 | 0% |
| Model Metadata | 8 | 0 | 0 | 8 | 0% |
| Optimization Agents | 5 | 0 | 0 | 5 | 0% |
| Optimization Formulation | 4 | 0 | 0 | 4 | 0% |
| Provenance | 3 | 0 | 1 | 2 | 17% |
| **TOTAL** | **36** | **1** | **4** | **31** | **~7%** |

---

## Critical Gaps for waterFRAME Use Case

The following capabilities are **essential** for agent-based optimization over water treatment networks and are **completely absent** from SAREF4WATER:

1. **Network topology representation**: No way to represent directed flow connections between assets
2. **Treatment process decomposition**: No unit process representation or treatment train composition
3. **Model metadata**: No computational model description, parameters, or invocation protocols
4. **Decision variable identification**: No distinction between fixed parameters and manipulable variables
5. **Agent capabilities**: No representation of optimization agents or their capabilities
6. **Fit-for-purpose classification**: No water reuse categories or quality requirements
7. **Regulatory compliance**: No standards, limits, or compliance checking support
8. **Mass balance constraints**: No representation of conservation equations or inter-node dependencies

---

## Recommendation

**Do NOT use SAREF4WATER as the primary ontology for waterFRAME.**

### Strengths
- Good IoT sensor/actuator taxonomy for water infrastructure
- Solid measurement pattern (inherited from SAREF)
- Basic water quality parameter classification
- Device metadata management

### Weaknesses
- **No network topology representation** (fatal flaw for catchment-scale optimization)
- **No treatment process modeling support** (fatal flaw for process optimization)
- **No computational model metadata** (fatal flaw for agent invocation)
- **No water reuse/fit-for-purpose concepts** (critical gap for water reuse scenarios)
- Missing imports for referenced ontologies (GeoSPARQL, SAREF, SAREF4CITY)
- Focused on smart city IoT monitoring, not water system engineering

### Bridging Strategy

SAREF4WATER could serve as a **component** in a larger ontology ecosystem:

1. **Reuse the sensor/measurement layer**: Import SAREF4WATER's device and property classes
2. **Extend for topology**: Add properties for flow connectivity (e.g., `hasInflow`, `hasOutflow`)
3. **Add treatment process layer**: Create unit process classes with composition relationships
4. **Add model metadata layer**: Describe computational models, parameters, and invocation
5. **Add water reuse layer**: Define fit-for-purpose categories and quality requirements
6. **Consider alternatives**: Investigate WaWO (Wastewater Ontology) for treatment processes, OntoAgent for agent metadata

### Next Steps

1. Search for complementary ontologies (WaWO, OntoAgent, water reuse ontologies)
2. Design custom extensions for missing capabilities
3. Develop alignment/bridging module between SAREF4WATER and waterFRAME core
