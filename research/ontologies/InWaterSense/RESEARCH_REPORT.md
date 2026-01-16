# InWaterSense Ontology Research Report

**Ontology Name:** InWaterSense (INWS)
**Project URL:** https://github.com/lule-ahmedi/InWaterSense
**Last Updated:** October 7, 2018 (last commit)
**Publication:** "An Ontology Framework for Water Quality Management" - SSN 2013 (CEUR-WS Vol-1063)

---

## Summary

InWaterSense is an OWL 2 ontology framework for water quality management through wireless sensor networks (WSNs). It is built on the W3C Semantic Sensor Network (SSN) ontology and aims to provide a "pure Semantic Web framework" for effective water quality monitoring and management. The project addresses limitations of hybrid ontology-based systems by proposing a semantic approach to sensor data interoperability.

The ontology consists of modular components designed for different aspects of water quality monitoring.

---

## Ontology Architecture

The InWaterSense framework comprises **five ontology modules**:

### 1. **Core Ontology** (`inws-core.owl`)
- **Size:** 121KB
- **Classes:** 33
- **Object Properties:** 151
- **Data Properties:** 199
- **Purpose:** Handles real-time observational water quality data from sensors and lab measurements

### 2. **Regulations Ontology** (`inws-regulations.owl`)
- **Size:** 54KB
- **Classes:** 188
- **Object Properties:** 9
- **Data Properties:** 5
- **Purpose:** Manages permitted water parameter thresholds from regulatory authorities (e.g., Water Framework Directive)

### 3. **Pollutants Ontology** (`inws-pollutants.owl`)
- **Size:** 12KB
- **Classes:** 2
- **Object Properties:** 2
- **Data Properties:** 2
- **Purpose:** Represents pollution entities and their attributes

### 4. **Polluters Ontology** (`inws-polluters.owl`)
- **Size:** 12KB
- **Classes:** 2
- **Object Properties:** 2
- **Data Properties:** 2
- **Purpose:** Represents facilities discharging waste into water bodies
- **Note:** Contains identical content to pollutants ontology (appears to be duplicate)

### 5. **LMINWS - Lightweight Mobile Version** (`lminws.owl`)
- **Size:** 11KB
- **Classes:** 40
- **Object Properties:** 9
- **Data Properties:** 10
- **Purpose:** Mobile sensor support with context-aware capabilities (day/night, location, personnel)
- **Publication:** MTSR 2016

---

## Core Concepts

### Water Quality Classes
- `WaterQuality` - base quality class
- `RiversWaterQuality` - river-specific quality subclass
- `DrinkingWaterQuality` - drinking water quality subclass
- Status classifications: Good, Moderate, Poor, High, Bad
- Parameter types: pH, Turbidity, BOD, Dissolved Oxygen, Conductivity, Ammonium, etc.

### Sensor System Classes
- `SensingNode` - individual sensor units
- `CentralMonitoringNode` - base station/gateway
- `Gateway` - data aggregation point
- Specific sensor types: `pHSensor`, `SulphateSensor`, `TotalNitrogenSensor`, `SuspendedSolidsSensor`, etc.

### Spatial Concepts
- `WaterFeature` - general water entity
- `RiversWaterFeature` - river-specific features
- `Municipality`, `hasBasin`, `hasRiver` - geographic hierarchy
- `observationResultLocation` - WGS84 point coordinates

### Water Framework Directive (WFD) Status
- `WFDEcoStatuses` - ecological status classifications
- `WFDChemStatuses` - chemical status classifications
- `WFDWaterHardnessStatus` - water hardness categories
- Regulatory thresholds encoded as measurement classes (e.g., `GoodBODMeasurement`, `HighTemperatureMeasurement`)

### Pollutants & Pollution Sources
- `Pollutant` categories: Ammonia, HeavyMetals, Hydrocarbons, Organic_chemicals, Pathogens, etc.
- `PollutionSources`: Industrial_effluent, Sewage, Agricultural_fertilisers, Oil, Mining, etc.
- Properties: `pollutionSourceName`, `pollutionType`, `potentialPollutant`, `hasSourcesOfPollution`

### Mobile Sensor Context (LMINWS)
- Activities: `Monitoring`, `Reporting`, `Calibration`, `Maintanance`, `Evaluation`
- Personnel: `internalPerson`, `externalPerson`
- Properties: `hasActivity`, `hasCamera`, `hasCoordinates`, `hasDeviceStatus`, `hasTimestamp`

---

## External Dependencies

Based on namespace declarations, the ontology imports/references:

- **SSN** (`http://purl.oclc.org/NET/ssnx/ssn#`) - W3C Semantic Sensor Network ontology
- **DUL** (`http://www.loa-cnr.it/ontologies/DUL.owl#`) - DOLCE Ultralite
- **Time** (`http://www.w3.org/2006/time#`) - W3C Time ontology
- **Geo** (`http://www.w3.org/2003/01/geo/wgs84_pos#`) - W3C Geo WGS84
- **QU** (`http://www.purl.oclc.org/NET/ssnx/qu/qu#`) - Quantity Units ontology
- **SWEET** (`http://sweet.jpl.nasa.gov/2.1/`) - NASA SWEET ontologies (hydro, elements)
- **Event** (`http://www.csiro.au/EventOntology#`) - CSIRO Event ontology
- **Other domain imports:** Pollution ontology, EPA ontology

---

## Design Patterns

### SSN Observation Pattern
The core ontology follows the SSN pattern:
- Sensors `observes` Properties
- Sensors `detects` Stimuli
- Features `hasProperty` Properties
- Observations `hasFeatureOfInterest` Features

### Regulation Encoding
Regulations are encoded as measurement value classes rather than axioms or rules:
```
GoodBODMeasurement → hasMeasurementCapability → WaterBOD5_MeasurementCapability
HighTemperatureMeasurement → specific threshold class
```
This is **not standard OWL practice** - typically regulations would be encoded as:
- Data property restrictions on observation values
- SWRL rules for threshold checking
- SPARQL queries for compliance checking

### Spatial Hierarchy
```
Municipality → hasRiver → River → hasBasin → Basin
Municipality → hasSensingNode → SensingNode
```

---

## Analysis: Claims vs. Reality

### What the Paper Claims
1. **"Pure Semantic Web framework"** - No hybrid system components
2. **Enables intelligent decision-making** - Through semantic inference
3. **Supports real-time data collection** - From WSNs
4. **Provides semantic interoperability** - Via SSN alignment

### What the OWL Files Contain
| Claim | OWL Implementation | Assessment |
|-------|-------------------|------------|
| Water quality monitoring | Classes for water quality, sensors, measurements | ✓ Implemented |
| Regulatory compliance | Regulation classes, threshold measurement classes | ⚠️ Inadequate - rules missing |
| Intelligent inference | No SWRL rules found | ✗ Missing |
| SSN integration | Uses SSN namespaces, extends SSN classes | ✓ Implemented |
| Mobile sensor support | LMINWS has context classes | ✓ Implemented |
| Semantic interoperability | Uses standard ontologies (SSN, DUL, Time, Geo) | ✓ Implemented |

### Quality Issues

1. **Regulation Modeling Deficiency:**
   - Regulations are encoded as static classes (e.g., `GoodBODMeasurement`) rather than executable rules
   - No threshold validation axioms (e.g., "if BOD > 5mg/L then status is Poor")
   - No SWRL rules for status classification despite paper claiming "water expert rules"

2. **Duplicate Content:**
   - `inws-pollutants.owl` and `inws-polluters.owl` are identical
   - Both contain only `Pollutant`, `PollutionSources` classes with same properties

3. **No Explicit Imports:**
   - Ontologies reference external namespaces but use no `owl:imports` statements
   - Dependencies are implicit, making ontology fragile

4. **Outdated Dependencies:**
   - Uses old SSN version (`purl.oclc.org/NET/ssnx/ssn#`) - SSN was replaced by SOSA in 2017
   - SWEET 2.1 is outdated (current is 3.x)

5. **Underdeveloped Mobile Version:**
   - LMINWS has basic context classes but no integration with core ontology
   - No mapping between mobile and static sensor observations

6. **Maintenance Status:**
   - Last commit: October 2018 (6+ years ago)
   - No issues addressed, no pull requests
   - Project website (`inwatersense.uni-pr.edu`) returns 403 error

---

## Coverage Analysis Against Competency Questions

Based on `/data/competency_questions/competency_questions.md` (reference needed):

| Requirement | InWaterSense Support | Notes |
|-------------|---------------------|-------|
| Represent water bodies | ✓ Partial | Has `WaterFeature`, `RiversWaterFeature` but limited water body types |
| Represent water quality parameters | ✓ Full | Extensive parameter classes (pH, DO, BOD, turbidity, etc.) |
| Represent sensors/observations | ✓ Full | Full SSN integration with specific sensor classes |
| Sensor deployment | ✓ Partial | `SensingNode`, `Gateway`, `CentralMonitoringNode` exist |
| Regulatory thresholds | ⚠️ Partial | Classes exist but no executable threshold rules |
| Pollution sources | ✓ Full | `PollutionSources`, `Pollutant` classes with types |
| Quality status classification | ⚠️ Partial | Status classes exist but classification logic missing |
| Spatial relationships | ✓ Full | Municipality-River-Basin hierarchy, WGS84 points |
| Temporal modeling | ✓ Full | Time ontology integration |
| Mobile sensor context | ✓ Full (LMINWS) | Context classes for mobile scenarios |
| Model invocation metadata | ✗ None | No representation of computational models |
| Agent capabilities | ✗ None | No agent concepts |
| Optimization problem formulation | ✗ None | Not applicable |

---

## Minimal Working Example

```turtle
@prefix inws: <http://inwatersense.uni-pr.edu/ontologies/inws-core.owl#> .
@prefix ssn: <http://purl.oclc.org/NET/ssnx/ssn#> .
@prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#> .
@prefix time: <http://www.w3.org/2006/time#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Define a river feature
:WhiteDrift a inws:RiversWaterFeature ;
    inws:hasRiverName "White Drift River" .

# Define a sensing node
:SensorStation1 a inws:SensingNode ;
    geo:lat 42.67 ;
    geo:long 21.17 ;
    inws:isMeasurementSiteOf :WhiteDrift ;
    inws:hasDeviceType "pH Sensor" .

# Define a pH sensor
:pHSensor1 a inws:pHSensor ;
    ssn:observes inws:WaterPH ;
    ssn:hasMeasurementCapability inws:WaterPH_MeasurementCapability .

# Define observation
:Obs1 a ssn:Observation ;
    ssn:observationResultTime "2024-01-15T10:30:00"^^xsd:dateTime ;
    ssn:hasFeatureOfInterest :WhiteDrift ;
    ssn:observedProperty inws:WaterPH ;
    ssn:observationResult :Result1 .

# Observation result
:Result1 a ssn:SensorOutput ;
    ssn:hasValue 7.2 ;
    ssn:isProducedBy :pHSensor1 .
```

### SPARQL Query: Find pH measurements for a river

```sparql
PREFIX inws: <http://inwatersense.uni-pr.edu/ontologies/inws-core.owl#>
PREFIX ssn: <http://purl.oclc.org/NET/ssnx/ssn#>
PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>

SELECT ?sensor ?river ?value ?time
WHERE {
  ?sensor a inws:pHSensor .
  ?obs ssn:madeObservation ?sensor ;
        ssn:observationResultTime ?time ;
        ssn:hasFeatureOfInterest ?river ;
        ssn:observationResult/ssn:hasValue ?value .
  ?river a inws:RiversWaterFeature ;
        inws:hasRiverName ?riverName .
}
```

---

## SWRL Rules Gap

The paper claims "water expert rules" but **no SWRL rules exist** in the ontologies. A typical status classification rule would be:

```xml
<!-- Example of what SHOULD exist but doesn't -->
<swrl:Imp>
  <swrl:head>
    <rdf:Description>
      <swrl:classPredicate rdf:resource="http://inwatersense.uni-pr.edu/ontologies/inws-regulations.owl#Poor"/>
      <swrl:argument1 rdf:resource="#observation"/>
    </rdf:Description>
  </swrl:head>
  <swrl:body>
    <rdf:Description>
      <swrl:propertyPredicate rdf:resource="http://purl.oclc.org/NET/ssnx/ssn#hasValue"/>
      <swrl:argument1 rdf:resource="#observation"/>
      <swrl:argument2>
        <swrl:Variable rdf:about="#v"/>
      </swrl:argument2>
    </rdf:Description>
    <rdf:Description>
      <swrl:propertyPredicate rdf:resource="http://inwatersense.uni-pr.edu/ontologies/inws-core.owl#measures"/>
      <swrl:argument1 rdf:resource="#observation"/>
      <swrl:argument2 rdf:resource="http://inwatersense.uni-pr.edu/ontologies/inws-core.owl#WaterPH"/>
    </rdf:Description>
    <rdf:Description>
      <swrl:builtin rdf:resource="http://www.w3.org/2003/11/swrlb#greaterThan"/>
      <swrl:arguments>
        <swrl:Variable rdf:about="#v"/>
        <rdf:Description>
          <swrl:argument2>9.0</swrl:argument2>
        </rdf:Description>
      </swrl:arguments>
    </rdf:Description>
  </swrl:body>
</swrl:Imp>
```

---

## Strengths

1. **Strong SSN Foundation** - Properly extends W3C SSN ontology
2. **Modular Design** - Separate modules for core, regulations, pollutants
3. **WFD Compliance** - Includes Water Framework Directive status classes
4. **Sensor Types** - Specific sensor classes for common water parameters
5. **Geospatial Support** - WGS84 integration for location
6. **Mobile Context** - LMINWS addresses mobile sensor scenarios

---

## Gaps

1. **No Executable Regulation Rules** - Regulations are descriptive, not prescriptive
2. **Outdated SSN** - Uses deprecated SSN instead of SOSA (current W3C standard)
3. **Missing Model Integration** - No representation of process models or computational agents
4. **No Quality Assurance** - No consistency checks, no test data
5. **Limited Water Body Types** - Only rivers addressed, no lakes, reservoirs, groundwater
6. **No Treatment Processes** - No representation of wastewater treatment units
7. **No Optimization Concepts** - No decision variables, constraints, objectives
8. **No Alignment to SOSA** - SOSA released 2017, ontology predates it

---

## Bridging Potential

| Gap | Potential Bridge | Approach |
|------|----------------|----------|
| Outdated SSN | SOSA (http://www.w3.org/ns/sosa/) | Map SSN classes to SOSA equivalents |
| No treatment processes | OntoCAPE, WaWO+ | Add `TreatmentProcess` classes |
| No model metadata | PROV-O, OntoDerivation | Describe model inputs/outputs |
| No optimization | Custom extension | Add `DecisionVariable`, `ObjectiveFunction` |
| Limited water bodies | HY_Features, INSPIRE | Import and align hydrography terms |

---

## Recommendation

**Status: NOT RECOMMENDED for direct use**

**Rationale:**
- Outdated dependencies (SSN, not SOSA)
- Non-executable regulation modeling (no SWRL rules)
- No maintenance since 2018
- Significant gaps for modern water resource optimization use cases

**Use Cases for Reference:**
1. Study SSN-based observation pattern implementation
2. Reference WFD status class modeling
3. Mobile sensor context modeling (LMINWS)
4. Water quality parameter taxonomy

**Recommended Alternatives:**
1. **SOSA/SSN** - Direct use of current W3C standards
2. **WaWO+** - For wastewater treatment representation
3. **HyFO** - For hydrological features
4. **SAREF4WATR** - For smart water IoT integration

---

## Implementation Assessment

### Phase 1: Load and Inspect
```python
from owlready2 import get_ontology
onto = get_ontology("file://inws-core.owl").load()
# ✓ Loads successfully
# No import statements - dependencies must be loaded separately
```

### Phase 2: Instantiate Example Data
- ✓ All major classes can be instantiated
- ✓ Properties applicable (domain/range restrictions sensible)
- ⚠️ No cardinality restrictions found

### Phase 3: Query Testing
```python
# ✓ Can query sensors, observations, water features
# ✓ SPARQL works for data retrieval
# ⚠️ Cannot query regulatory compliance (no rules to execute)
# ✗ Cannot infer status classifications (no SWRL rules)
```

### Phase 4: Reasoning Consistency Check
```python
from owlready2 import sync_reasoner_pellet
# ✓ Ontology is consistent (no contradictions found)
# ⚠️ Minimal inferences (no property chains, no equivalent classes)
```

---

## License

No explicit license information found in repository files.

---

## Summary Assessment

| Criterion | Rating | Notes |
|-----------|---------|-------|
| Domain Coverage | ⚠️ Partial | Good for monitoring, missing treatment/optimization |
| OWL Quality | ⚠️ Moderate | Valid OWL but minimal use of expressivity |
| Documentation | ⚠️ Poor | README exists but no formal ontology documentation |
| Maintenance | ✗ Low | No updates since 2018 |
| Alignment with Standards | ⚠️ Partial | Uses old SSN, not SOSA |
| Suitability for Agent-Based Optimization | ✗ None | Missing model/agent concepts |

**Overall: Useful reference, not suitable for production use in modern water resource optimization systems.**
