# Water Health Open Knowledge Graph (WHOW-KG) Research Report

**Date:** 2025-01-15
**Researcher:** OpenCode Agent
**Source:** WHOW Project - EU CEF Open Data Project

---

## Executive Summary

The Water Health Open Knowledge Graph (WHOW-KG) is a distributed, open knowledge graph developed under the EU-funded WHOW (Water Health Open Knowledge) project. It links environmental water quality data with health parameters (infectious disease rates, drug distribution) to support analysis and decision-making in water and health domains.

**Status:** ✅ **LOCATED AND ANALYZABLE** - All ontology files are available, well-documented, and actively maintained.

---

## 1. Source Identification

| Attribute | Value |
|-----------|-------|
| **Project Name** | WHOW (Water Health Open Knowledge) |
| **Funding** | EU Connecting Europe Facility (CEF) - Grant Agreement INEA/CEF/ICT/A2019/2063229 |
| **Main Publication** | "The Water Health Open Knowledge Graph" - Scientific Data (2025), DOI: 10.1038/s41597-025-04537-4 |
| **arXiv Preprint** | arXiv:2305.11051 |
| **Project Website** | https://whowproject.eu/ |
| **GitHub Repository** | https://github.com/whow-project/semantic-assets |
| **Zenodo DOI** | https://doi.org/10.5281/zenodo.7916179 |
| **License** | CC-BY 4.0 International |
| **Maintenance Status** | ✅ Active (last commit recent, versioned releases) |

---

## 2. Domain Coverage

### What WHOW-KG Represents

The WHOW-KG models data across three primary use cases:

#### UC1: Contaminants in Marine Waters
- Bioaccumulation of chemicals in marine waters
- Human exposure via contaminated fish products
- Airborne exposure (e.g., *Ostreopsis ovata* algae blooms)
- Links to infectious disease data

#### UC2: Water Quality for Human Consumption
- Drinking water quality parameters
- Surface water and groundwater quality
- Compliance with EU Directive 2020/2184 (drinking water)
- EU Directive 2009/90/EC (surface waters)
- Chemical, microbiological, physical parameters

#### UC3: Meteorological Extreme Events
- Weather observations (rainfall, snow, temperature)
- Floods, sea storms, storm surges, droughts
- Impact on hydrological cycle
- Agricultural industry impacts

**Scale:** 100+ million triples from 19 datasets (ISPRA, ARIA/Lombardy Region)

---

## 3. Ontology Network Architecture

### Structure
The WHOW-KG consists of a **modular ontology network** with 8 modules (5 novel + 3 imported):

```
┌─────────────────────────────────────────────────────────────┐
│           WHOW Ontology Network                     │
├─────────────────────────────────────────────────────────────┤
│                                                    │
│  ┌────────────────────────────────────────┐             │
│  │   External (Imported)              │             │
│  │   • TOP (Upper-level)              │             │
│  │   • INSPIRE-MF (Monitoring)       │             │
│  │   • PLACE (Geographic)             │             │
│  └────────────────────────────────────────┘             │
│                                                    │
│  ┌────────────────────────────────────────┐             │
│  │   Novel Modules                      │             │
│  ├────────────────────────────────────────┤             │
│  │ 1. Hydrography                      │             │
│  │    - Water bodies, basins             │             │
│  │                                    │             │
│  │ 2. Water Monitoring                 │             │
│  │    - Observations, parameters         │             │
│  │    - Samples, sampling points         │             │
│  │                                    │             │
│  │ 3. Water Indicator                 │             │
│  │    - Quality indicators             │             │
│  │                                    │             │
│  │ 4. Weather Monitoring               │             │
│  │    - Weather observations           │             │
│  │    - Stations, sensors            │             │
│  │                                    │             │
│  │ 5. Health Monitoring               │             │
│  │    - Disease rates, drug dist.      │             │
│  │    - Clinical cohorts              │             │
│  └────────────────────────────────────────┘             │
│                                                    │
│  Plus 3 Controlled Vocabularies:                    │
│  • Chemical substances (linked to Wikidata)           │
│  • Diseases (linked to SNOMED)                   │
│  • Water indicators                                │
└─────────────────────────────────────────────────────────────┘
```

### Base Namespace
- **Prefix:** `https://w3id.org/whow/onto/`
- **Versioning:** Semantic versioning (e.g., `https://w3id.org/whow/onto/hydrography/0.2`)

---

## 4. Module Analysis

### 4.1 Hydrography Ontology (`hydro:`)

**Purpose:** General-purpose hydrological taxonomy following EU Water Framework Directive 2000/60/EC

**Core Classes:**
- `WaterFeature` (top-level, extends `inspire-emf:FeatureOfInterest`)
  - `WaterBasin` (with sub-basin hierarchy via `isSubWaterBasin`)
  - `WaterBody` (abstract)
    - `TransitionalWaterBody`
    - `MarineWaterBody`
    - `RiverWaterBody`
    - `LakeWaterBody`
    - `GroundwaterBody`
    - `CoastalWaterBody`

**Key Properties:**
- `belongsToWaterBasin` (WaterBody → WaterBasin)
- `isSubWaterBasin` (WaterBasin → WaterBasin) - **PartOf ODP**

**Alignment:** INSPIRE Hydrography concepts (`prov:wasDerivedFrom` references)

**Strengths:**
✅ Clean, well-structured taxonomy
✅ Direct alignment with EU directives
✅ Supports hierarchical basin relationships

**Gaps for Our Use Case:**
❌ No treatment plants / processes
❌ No flow relationships between infrastructure
❌ No representation of water reuse / greywater separation

---

### 4.2 Water Monitoring Ontology (`w-mon:`)

**Purpose:** Represent observations of water quality, pollution, and physical parameters

**Core Hierarchy:**
```
WaterObservation
├── DrinkingWaterObservation
│   ├── WaterChemicalParameterObservation
│   ├── WaterMicrobiologicalParameterObservation
│   ├── WaterIndicatorParameterObservation
│   └── WaterEmergingParametersObservation
└── SurfaceOrGroundwaterObservation
    ├── WaterBiologicalQualityParameterObservation
    ├── WaterPhysicoChemicalParameterObservation
    └── WaterHydromorphologicalParameterObservation
```

**Key Classes:**
- `WaterObservableProperty` - extends `inspire-mf:ObservationParameter`
- `WaterObservablePropertyObject` - what is being measured
  - `ChemicalSubstance`
  - `BiologicalAgent`
  - `RadioactivityObject`
- `WaterSample` - with `isSampleOf` and `isObtainedBy`
- `SamplingPoint` - location of sample collection
- `ObservationValue` - can be single value or Range

**Key Properties:**
- `hasWaterFeature` (subproperty of `inspire-mf:hasFeatureOfInterest`)
- `hasWaterObservableProperty`
- `hasWaterObservablePropertyObject`
- `hasChemicalSubstance`, `hasBiologicalAgent`
- `hasResult` → `ObservationValue`
- `hasObservationSample` → `WaterSample`
- `withRespectToReferenceParam` - for hydrometric zero, etc.

**Pattern:** Follows SSN/SOSA and ISO 19156 Specimen model

**Strengths:**
✅ Comprehensive parameter classification
✅ Supports both point values and ranges
✅ Good separation of drinking vs surface/groundwater
✅ Includes sampling process metadata

**Gaps for Our Use Case:**
❌ No treatment process monitoring
❌ No operational parameters (flow rates, tank levels, etc.)
❌ No linkages to treatment units
❌ No fit-for-purpose classification

---

### 4.3 Water Indicator Ontology (`w-ind:`)

**Purpose:** Represent water quality indicators (e.g., LTLeco, LIMeco)

**Reuses:** Italian OntoPiA Indicator pattern

**Key Classes:**
- `Indicator` - extends `inspire-mf:Indicator`
- Indicator calculations for water body status

**Examples from Paper:**
- LTLeco: integrates phosphorus, transparency, hypolimnic oxygen
- LIMeco: synthetic index for stream water nutrients/oxygenation

**Strengths:**
✅ Reuses established indicator pattern
✅ Supports EU WFD indicator requirements

**Gaps:**
❌ Limited to water quality indices (not treatment performance)
❌ No optimization/reuse suitability indicators

---

### 4.4 Weather Monitoring Ontology (`wh-mon:`)

**Purpose:** Support extreme event use case with meteorological observations

**Core Structure:**
- `WeatherObservation`
- `WeatherFeatureOfInterest` (ground soil, air, wind, snow, rainfall)
- `WeatherObservableProperty`
- `WeatherSensor`
- `WeatherStation`

**Alignment:** ISPRA EMF for observations

**Strengths:**
✅ General-purpose weather observation model
✅ Supports extreme event detection

**Relevance to Our Use Case:**
⚠️ Indirect - weather impacts water availability but not core to treatment optimization

---

### 4.5 Health Monitoring Ontology (`hm:`)

**Purpose:** Represent health indicators (disease rates, drug distribution, hospital access)

**Core Classes:**
- `HealthcareIndicator` - controlled vocabulary of indicators
- `HealthcareIndicatorCalculation` - computed values
  - `HealthConditionIndicatorCalculation`
  - `DrugDistributionIndicatorCalculation`
  - `InfectiousDiseaseRateCalculation`
- `ClinicalCohort` - population segment for indicator
  - With `CohortCriteriaDescription` (age, gender, etc.)
- `HealthcareAuthority` (e.g., ATS/ASL)
- `InpatientFacility`
- `Disease`, `DrugType`, `CauseOfDeath`

**Key Properties:**
- `ofClinicalCohort` - calculation applies to population segment
- `affectedBy` - cohort linked to disease
- `assumed` - cohort linked to drug type
- `diedFrom` - cohort linked to cause of death
- `isResponsibleFor` - authority jurisdiction
- `subIndicator` - indicator composition hierarchy

**Strengths:**
✅ Rich cohort modeling
✅ Flexible indicator calculation framework
✅ Links to geographic jurisdiction

**Gaps for Our Use Case:**
❌ Focused on public health epidemiology, not water treatment operations

---

## 5. Data Production Architecture

### Methodology
1. **Requirement Collection** - via competency questions from domain experts
2. **Ontology Development** - using eXtreme Design (XD) with Ontology Design Patterns (ODPs)
3. **RML Mapping** - declarative mappings using RDF Mapping Language
4. **Decentralized Publishing** - each data provider maintains their own SPARQL endpoint

### Data Providers
| Provider | Data | Triples | License | SPARQL Endpoint |
|----------|-------|----------|----------|------------------|
| ISPRA | Water quality, soil use, mitigation measures | 52.9M | CC-BY 4.0 | https://dati.isprambiente.it/sparql |
| ARIA/Lombardy | River/lake/groundwater, diseases, lake heights, weather | 47.6M | CC0 (Public Domain) | http://18.102.46.55:18890/sparql |
| Controlled Vocabularies | Chemicals, diseases, indicators | 16K | CC-BY 4.0 | https://semscout.istc.cnr.it/sparql/ |

### Quality Assurance
- Competency questions converted to SPARQL unit tests (TESTaLOD approach)
- Validation runs on both toy data (ontology testing) and real data (LOD testing)

---

## 6. Technical Characteristics

### Statistics (from paper)
| Metric | Value |
|--------|-------|
| Axioms | 2,672 |
| Classes | 120 |
| Object Properties | 161 |
| Datatype Properties | 21 |
| SubObjectPropertyOf | 137 |
| Inverse Properties | 61 |
| Transitive Properties | 10 |
| Property Chains | 6 |
| DL Expressivity | SRIQ(D) |
| Disjoint Classes | 22 |

### OWL Profile
- **Expressivity:** SRIQ(D) - supports qualified cardinality, inverse, transitive, property chains
- **Imports:** 3 external ontologies (TOP, INSPIRE-MF, PLACE)
- **Pattern Usage:** SSN/SOSA, PartOf ODP, Indicator ODP, Description ODP

---

## 7. Comparison with Competency Questions

Per `/data/competency_questions/competency_questions.md` - the WHOKG was evaluated against:

| CQ Category | WHOKG Support | Notes |
|-------------|----------------|--------|
| **[O] Ontology-only queries** | ✅ Strong | Excellent for querying observations, samples, indicators, water bodies |
| **[R] Reasoning queries** | ⚠️ Partial | Has OWL DL restrictions but reasoning is not primary focus |
| **[M] Model invocation** | ❌ None | No treatment process models or optimization agent metadata |

### Coverage Matrix

| Requirement | Support | Assessment |
|-------------|-----------|-------------|
| Represent water bodies (lakes, rivers, groundwater) | ✅ Full | Hydrography module provides complete taxonomy |
| Represent water quality observations | ✅ Full | Water Monitoring has comprehensive observation hierarchy |
| Represent sampling process | ✅ Full | WaterSample, SamplingPoint, isObtainedBy properties |
| Represent indicators | ✅ Full | Water Indicator module extends OntoPiA Indicator pattern |
| Represent health indicators | ✅ Full | Health Monitoring with cohort modeling |
| Link water quality to health | ✅ Full | Via shared geographic location and temporal alignment |
| Represent treatment plants | ❌ None | No treatment infrastructure classes |
| Represent treatment processes | ❌ None | No process modeling (biological, chemical, physical ops) |
| Represent process parameters | ❌ None | No operational parameters (DO, pH, flow, retention time) |
| Represent model metadata | ❌ None | No model descriptions, APIs, or agent invocation protocols |
| Represent decision variables | ❌ None | No optimization-specific constructs |
| Represent agent capabilities | ❌ None | No agent representation |

---

## 8. Strengths

1. **Well-Designed Modular Architecture**
   - Clear separation of concerns (hydrography, monitoring, indicators, health, weather)
   - Minimal coupling, high cohesion
   - Follows ODP methodology

2. **Strong Standards Alignment**
   - INSPIRE compliance (EU spatial data infrastructure)
   - SSN/SOSA for observations
   - ISO 19156 specimen model

3. **Comprehensive Water Quality Coverage**
   - Detailed parameter classification (chemical, microbiological, biological, physico-chemical, hydromorphological)
   - Supports EU Water Framework Directive requirements

4. **Active Maintenance**
   - Versioned releases on GitHub
   - Persistent URIs via w3id.org
   - Regular updates (last modified Nov 2023)

5. **Real-World Deployment**
   - 100+ million triples in production
   - Multiple SPARQL endpoints
   - Used by Italian public agencies

6. **Quality Methodology**
   - eXtreme Design (collaborative ontology engineering)
   - TESTaLOD for automated testing
   - Competency question validation

---

## 9. Gaps for Our Use Case

### Critical Missing Capabilities

1. **Treatment Infrastructure**
   - No representation of wastewater treatment plants
   - No unit operations (clarifiers, biological reactors, filters)
   - No pumps, valves, sensors (process control)

2. **Process Modeling**
   - No ASM/ADM1 model metadata
   - No kinetic parameters
   - No mass/energy balance descriptions

3. **Operational Monitoring**
   - No real-time sensor data structure (DO probes, flow meters)
   - No control loop representation
   - No alarm/event modeling

4. **Optimization-Specific Constructs**
   - No decision variables (setpoints, dosing rates)
   - No objective function representations
   - No constraints (regulatory limits, capacity)
   - No solver/model agent metadata

5. **Water Reuse Framework**
   - No fit-for-purpose classification
   - No greywater/blackwater separation
   - No treatment train composition

6. **Process Flows**
   - No directed graph of material flows
   - No sludge/chemical/energy inputs/outputs
   - No recirculation loops

### Why This Gap Exists

WHOKG was designed for **regulatory monitoring and public health correlation**, not for:
- Process control and optimization
- Engineering design of treatment systems
- Agent-based decision support

This is a fundamental difference in purpose, not a design flaw.

---

## 10. Reuse Strategy

### Recommended Approach: **BRIDGE + EXTEND**

WHOKG provides excellent foundation layers we should reuse:

#### **Direct Reuse** (import):
```
ontEAUlogy
├── imports hydrography (water body taxonomy)
├── imports water-monitoring (observation patterns)
└── imports water-indicator (indicator framework)
```

#### **Bridge to WHOKG Concepts:**
```turtle
# Our treatment plants are features in the hydrography context
ontea:WastewaterTreatmentPlant  rdfs:subClassOf  hydro:WaterFeature .

# Our process observations align with water observations
ontea:ProcessObservation  rdfs:subClassOf  w-mon:WaterObservation .

# Our quality indicators extend the indicator pattern
ontea:TreatmentPerformanceIndicator  rdfs:subClassOf  w-ind:Indicator .
```

#### **Extensions Needed:**

1. **Treatment Infrastructure Module**
   - `TreatmentPlant` (extends `hydro:WaterFeature`)
   - `UnitOperation` (biological, chemical, physical)
   - `ProcessFlow` (connections between units)

2. **Model Metadata Module**
   - `Model` (ASM, ADM1, hydraulic)
   - `ModelParameter` (kinetic, stoichiometric)
   - `ModelInputVariable`, `ModelOutputVariable`

3. **Optimization Module**
   - `DecisionVariable` (manipulable parameters)
   - `ObjectiveFunction`
   - `OptimizationAgent` (capabilities, solvers)
   - `Constraint` (regulatory, physical)

#### **Alignment Properties:**
- For water bodies served: `servesWaterBody` → `hydro:WaterBody`
- For water quality: `hasWaterQualityObservation` → `w-mon:WaterObservation`
- For health impacts: `hasHealthImpactIndicator` → `hm:HealthcareIndicator`

---

## 11. Controlled Vocabularies

WHOKG provides three useful vocabularies:

1. **Chemical Substances** (`controlled-vocabularies/chemical-substances/`)
   - Linked to Wikidata
   - CAS numbering system
   - ✅ **REUSE** - for parameter classification

2. **Diseases** (`controlled-vocabularies/diseases/`)
   - Linked to SNOMED CT
   - Infectious disease taxonomy
   - ⚠️ **CONTEXTUAL** - relevant if we model health correlations

3. **Water Indicators** (`controlled-vocabularies/water-indicators/`)
   - EU WFD quality indicators
   - LTLeco, LIMeco, etc.
   - ✅ **REUSE** - for compliance monitoring

---

## 12. Potential Interoperability

### Direct Overlaps
| Domain | WHOKG Coverage | Our Gap |
|---------|----------------|----------|
| Water bodies | ✅ Full taxonomy | - |
| Water quality monitoring | ✅ Full | - |
| Sampling | ✅ Full | - |
| Treatment infrastructure | ❌ None | Must define |
| Process monitoring | ❌ None | Must define |
| Optimization | ❌ None | Must define |

### Indirect Overlaps
- **Weather Monitoring** - relevant for climate impacts but not core
- **Health Monitoring** - relevant for impact assessment but not process control

---

## 13. Licensing and Reuse Conditions

| Asset | License | Our Use |
|--------|----------|----------|
| Ontologies | CC-BY 4.0 | ✅ Can import and extend, must attribute |
| ISPRA Data | CC-BY 4.0 | ✅ Can link, must attribute |
| Lombardy Data | CC0 (Public Domain) | ✅ No attribution required |
| Controlled Vocabularies | CC-BY 4.0 | ✅ Can reuse, must attribute |

**Verdict:** ✅ **EXCELLENT LICENSE TERMS** - Compatible with our open-source goals

---

## 14. Quality Assessment

### Documentation
- ✅ Comprehensive paper (Scientific Data, Q1 journal)
- ✅ Graphical ontology diagrams (Graffoo PNGs)
- ✅ Inline Italian/English labels and comments
- ✅ GitHub README with module descriptions

### Code Quality
- ✅ Proper RDF/Turtle serialization
- ✅ Versioned IRIs
- ✅ Semantic annotations (rdfs:comment, rdfs:isDefinedBy)
- ✅ Provenance (prov:wasDerivedFrom)

### Consistency
- ⚠️ **NOT TESTED** - We did not run a reasoner
- Paper claims consistency but not independently verified
- Recommendation: Run HermiT/Pellet during integration testing

### Maintainability
- ✅ Modular structure
- ✅ Clear versioning
- ✅ Active repository (recent commits)
- ⚠️ Some properties marked "unstable"/"provvisoria" in health monitoring

---

## 15. Recommendations

### For Our Project

1. **DO IMPORT**:
   - `hydrography` - for water body taxonomy
   - `water-monitoring` - for observation patterns
   - `water-indicator` - for indicator framework

2. **DO NOT USE**:
   - Health monitoring (out of scope)
   - Weather monitoring (only if we need extreme event correlation)
   - Water quality parameter classes that don't match our treatment focus

3. **MUST CREATE**:
   - Treatment infrastructure module (plants, unit operations, flows)
   - Model metadata module (parameters, inputs, outputs, invocation)
   - Optimization module (agents, decision variables, objectives, constraints)

4. **DEFINE ALIGNMENTS**:
   - Map our treatment plants to `hydro:WaterFeature`
   - Map our quality observations to `w-mon:WaterObservation`
   - Reuse chemical substances vocabulary

5. **VALIDATION**:
   - Run Pellet reasoner on combined ontologies
   - Create TESTaLOD-style SPARQL unit tests
   - Verify no cycle in class hierarchy with our extensions

### For WHOKG Community

1. Consider adding treatment infrastructure module (they have use case for process optimization)
2. Model health impacts more explicitly (currently only indicator-level linkage)
3. Add process control observations (real-time sensor data)

---

## 16. Conclusion

**Assessment: STRONG FOUNDATION, INCOMPLETE FOR OUR USE CASE**

The WHOKG is a **high-quality, well-maintained ontology network** with excellent coverage of:
- Hydrography and water body taxonomy
- Water quality monitoring
- Regulatory indicators
- Health indicator calculation

However, it **does not support** our core requirements for:
- Wastewater treatment infrastructure
- Process modeling
- Optimization agent metadata

**Recommended Action:**
✅ **IMPORT AND EXTEND** - Use WHOKG's hydrography, monitoring, and indicator modules as foundation layers. Build new modules for treatment processes and optimization that align with WHOKG patterns.

**Expected Integration Effort:**
- Low - to import existing modules
- Medium - to create treatment infrastructure model
- High - to define optimization-specific constructs

**Value Added by WHOKG:**
- Regulatory compliance (EU Water Framework Directive)
- Standardized observation patterns
- Interoperability with European environmental data infrastructure

---

## 17. References

1. Carletti, G. et al. (2025). "The Water Health Open Knowledge Graph." *Scientific Data* 12(1), 274. DOI: 10.1038/s41597-025-04537-4
2. Carletti, G. et al. (2023). "The Water Health Open Knowledge Graph." arXiv:2305.11051
3. WHOW Project Website: https://whowproject.eu/
4. GitHub Repository: https://github.com/whow-project/semantic-assets
5. Zenodo DOI: https://doi.org/10.5281/zenodo.7916179
6. EU Water Framework Directive: 2000/60/EC
7. INSPIRE Directive: 2007/2/EC

---

**End of Report**
