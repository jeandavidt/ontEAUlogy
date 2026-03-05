# waterFRAME Ontology Summary

## Overview

**waterFRAME** (Water Framework for Reuse and Aquatic Modeling Enhancement) is a modular, BFO-grounded ontology for water reuse systems. It follows Alan Rector normalization principles and provides comprehensive support for agent-based optimization queries, regulatory compliance checking, and computational service discovery.

- **Version**: 0.1.0
- **Creator**: Jean-David Therrien
- **Namespace**: `https://ugentbiomath.github.io/waterframe#`
- **Repository**: https://github.com/jeandavidt/ontEAUlogy

---

## Domain Coverage

waterFRAME covers the following water system domains:

### 1. Physical Infrastructure
- **Water System Components**: Storage tanks, treatment units, usage points
- **Conveyance Systems**: Pipes (pressurized, gravity, sewer), canals, flow dividers, junctions
- **Facilities**: Treatment plants (drinking water, wastewater), pumping stations, reservoirs, monitoring points
- **Industrial Facilities**: Textile, food processing, electronics, pharmaceutical, brewery facilities
- **Natural Water Bodies**: Rivers, lakes, groundwater, catchments

### 2. Treatment Processes
- Physical treatment: Screening, grit removal, primary clarification
- Biological treatment: Biological oxidation, secondary clarification, membrane filtration
- Nutrient removal: Nitrification, denitrification, phosphorus removal
- Disinfection: UV, chlorination, ozonation

### 3. Water Quality
- **Parameters**: BOD, COD, TSS, TDS, pH, temperature, turbidity, conductivity, dissolved oxygen
- **Nutrients**: Total nitrogen, total phosphorus, ammonia, nitrate, nitrite, orthophosphate
- **Microbiological**: Coliform, chlorine residual, alkalinity
- **Classifications**: Drinking water, wastewater, reclaimed water, greywater, blackwater

### 4. Water Usage
- Human welfare: Bathing fixtures, cleaning fixtures, toilets, drinking water points
- Appliances: Laundry, dishwashing
- Industrial: Process water, cooling water, boiler feed
- Agricultural: Irrigation, livestock watering

---

## Module Structure

waterFRAME is organized into **13 modules** across four categories:

### Core Modules
| Module | File | Purpose |
|--------|------|---------|
| Material Entities | `modules/core/material_entities.ttl` | Physical objects (BFO:0000040) |
| Processes | `modules/core/processes.ttl` | Treatment processes (BFO:0000015) |
| Properties | `modules/core/properties.ttl` | Port-based topology, flow relationships |

### Information Modules
| Module | File | Purpose |
|--------|------|---------|
| Information | `modules/information.ttl` | Model metadata, inputs/outputs, variables |
| Capabilities | `modules/capabilities.ttl` | Simulation capabilities taxonomy |
| Agents | `modules/agents.ttl` | Computational agents and operations |
| Scenarios | `modules/scenarios.ttl` | Scenario modeling with OWL-Time |

### Regulatory Modules
| Module | File | Purpose |
|--------|------|---------|
| Qualities | `modules/qualities.ttl` | Water quality parameters and requirements |
| Sampling | `modules/sampling.ttl` | Sample metadata, methods, chain of custody |
| Compliance | `modules/compliance.ttl` | Compliance checking, violation tracking |

### Bridge Modules
| Module | File | Purpose |
|--------|------|---------|
| SOSA Alignment | `modules/bridges/sosa_alignment.ttl` | Sensor/observation alignment |
| ENVO Alignment | `modules/bridges/envo_alignment.ttl` | Environmental context alignment |

---

## Main Capabilities

### 1. System Topology Modeling
- **Port-based architecture**: Following OntoCAPE pattern with InputPort/OutputPort
- **Flow connections**: `flowsTo`, `receivesFlowFrom`, `hasDownstreamComponent`
- **Flow types**: Greywater, blackwater, rainwater, potable, reclaimed, process water
- **Component relationships**: Upstream/downstream tracking for network analysis

### 2. Model Metadata Management
- **Process Models**: Mathematical and simulation models (ASM, ADM, BSM, etc.)
- **Model Variables**: State variables, input/output variables, parameters
- **Decision Variables**: Markers for optimization parameters
- **Software Systems**: API endpoints and version tracking
- **Submodel Relationships**: Composite model composition

### 3. Computational Agent Framework
- **Agent Types**: Simulation agents, optimization agents, data transform agents, reasoning agents
- **Operations**: Predefined computational services with inputs/outputs
- **Execution Conditions**: Preconditions and postconditions for operations
- **HTTP Grounding**: RESTful API invocation specifications
- **Workflow Composition**: Automatic operation sequencing via `dataFlowsTo` property chains

### 4. Capability Taxonomy
- **Simulation**: Steady-state, dynamic simulation
- **Analysis**: Sensitivity analysis, uncertainty quantification, optimization
- **Balances**: Mass balance, energy balance
- **Predictions**: Water quality prediction, cost estimation
- **Specialized**: Hydraulic modeling, biokinetic modeling, nutrient removal, sludge production

### 5. Water Quality & Compliance
- **Fit-for-Purpose**: Quality constraint sets for different reuse applications
- **Regulatory Standards**: EU Water Framework Directive, USEPA, WHO guidelines
- **Compliance Checking**: Multi-jurisdiction compliance verification
- **Violation Tracking**: Exceedance, deficiency, range, sampling, reporting violations
- **Severity Classification**: Minor, moderate, serious, critical violations

### 6. Sampling & Provenance
- **Sample Types**: Grab, composite (time/flow-weighted), automated, continuous
- **Sampling Points**: Influent, effluent, process, ambient, discharge points
- **Chain of Custody**: PROV-O integration for full provenance tracking
- **Flow Direction**: Influent, effluent, process, bypass classification

### 7. Scenario Modeling
- **Scenario Types**: Baseline, alternative, historical, optimization scenarios
- **OWL-Time Integration**: Proper temporal representation with intervals
- **Scenario Comparison**: Multi-criteria comparison framework
- **Expansion Hooks**: Optimization objectives, constraints, simulation parameters

### 8. Sensor Integration (SOSA/SSN)
- **Sensor Types**: Water quality sensors, flow sensors, weather sensors
- **Observable Properties**: All water quality parameters aligned with SOSA
- **Weather Forecasts**: Nowcasts, short-term forecasts with confidence levels
- **Port Monitoring**: Sensor-to-port linking following OntoCAPE pattern

---

## Key Competency Questions Answered

### System Topology (CQ1-5)
- What components are in a water system?
- How are components connected (upstream/downstream)?
- What is the flow path between two components?
- What treatment units are in a facility?

### Water Quality (CQ10-11, CQ15-17)
- What are the water quality parameters for a given sample?
- What are the regulatory limits for a specific parameter?
- What is the fit-for-purpose classification of water?
- Is water quality compliant with regulations?

### Model Metadata (CQ18-20)
- What inputs does a model require?
- What outputs does a model produce?
- Which variables are decision variables for optimization?
- What software system implements a model?

### Agent Composition (CQ-AG1 to CQ-AG5)
- Which agents can simulate entity X?
- Which agents provide capability Y?
- Given available data {α, β}, which operations can execute?
- What sequence of operations transforms data α into information β?
- How do I invoke operation O? (HTTP endpoint + method)

### Regulatory Compliance
- Does this observation comply with regulatory requirements?
- What violations have occurred in the past month?
- What is the severity of a violation?
- What are the technology-based vs. water quality-based limits?

### Scenario Analysis
- What are the differences between baseline and alternative scenarios?
- Which components exist only in specific scenarios?
- How do costs compare across scenarios?
- What is the temporal extent of a historical scenario?

---

## External Ontology Alignments

| Ontology | Purpose | Integration |
|----------|---------|-------------|
| **BFO** | Upper ontology foundation | All classes grounded in BFO (material entities, processes, qualities) |
| **OWL-Time** | Temporal representation | Scenario time periods, observation timestamps |
| **PROV-O** | Provenance tracking | Observations, samples, model results |
| **SOSA/SSN** | Sensor observations | Water quality sensors, observable properties |
| **ENVO** | Environmental context | Aquatic features, discharge recipients |
| **QUDT** | Units of measurement | Water quality parameter units |
| **GeoNames** | Geographic jurisdictions | Regulatory framework locations |

---

## Design Patterns

### 1. BFO Compliance
- Material entities (continuants) vs. processes (occurrents) strictly separated
- `performsProcess` property bridges the distinction
- All classes have explicit BFO parent classes

### 2. Port-Based Topology (OntoCAPE)
- Components have ports (input/output)
- Flow occurs between ports, not components directly
- Enables precise network topology modeling

### 3. Entity-Feature-Value Pattern
- Water quality observations → parameters → values
- Supports regulatory compliance checking
- PROV-O integration for provenance

### 4. Alan Rector Normalization
- Quality constraint sets separate from classifications
- Enables multi-jurisdictional compliance
- Same water can have different fitness for different purposes

### 5. Capability-Based Discovery
- Agents advertise capabilities
- Operations specify preconditions/postconditions
- Automatic workflow composition via property chains

---

## Example Use Cases

1. **Agent Discovery**: Find all simulation agents that can model WWTPs with nutrient removal capabilities
2. **Workflow Composition**: Automatically chain operations where output of A matches input of B
3. **Compliance Monitoring**: Check if discharge observations meet EU Water Framework Directive limits
4. **Scenario Comparison**: Compare baseline vs. MBR addition alternative on cost and water reuse percentage
5. **Fit-for-Purpose Analysis**: Determine if treated effluent can be reused for toilet flushing based on quality constraints

---

## File Structure

```
data/ontology_enhanced/
├── waterframe.ttl              # Main ontology file (imports all modules)
├── ONTOLOGY_SUMMARY.md         # This summary document
├── modules/
│   ├── core/
│   │   ├── material_entities.ttl
│   │   ├── processes.ttl
│   │   └── properties.ttl
│   ├── agents.ttl
│   ├── capabilities.ttl
│   ├── compliance.ttl
│   ├── information.ttl
│   ├── qualities.ttl
│   ├── sampling.ttl
│   └── scenarios.ttl
│   └── bridges/
│       ├── sosa_alignment.ttl
│       └── envo_alignment.ttl
├── instances/                  # Instance data (optional)
└── examples/
    └── fit_for_purpose_example.ttl
```

---

## Future Expansion Areas

- Full optimization framework with objectives and constraints
- Economic modeling (cost functions, lifecycle analysis)
- Machine learning model integration
- Real-time sensor data streaming
- Climate scenario integration
- Extended industry-specific water quality profiles
