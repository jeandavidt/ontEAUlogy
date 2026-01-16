# waterFRAME Regulatory Extensibility Research

**Date:** 2025-01-15
**Researcher:** OpenCode Agent
**Scope:** Gap analysis between waterFRAME and WHOKG for general regulatory compliance

---

## Executive Summary

**Question:** Can waterFRAME be extended to describe water systems and their regulatory compliance across any jurisdiction?

**Answer:** ✅ **YES - waterFRAME has strong foundation** for general regulatory compliance, with targeted gaps that can be addressed through strategic extensions and WHOKG integration.

**Key Findings:**
- ✅ waterFRAME already has multi-jurisdiction support (EU, USEPA, WHO)
- ✅ Comprehensive water quality parameters and requirements
- ✅ Treatment infrastructure and process modeling
- ⚠️ Missing: Explicit sampling metadata, flow direction, compliance checking
- ✅ Strategy: Extend waterFRAME with WHOKG observation patterns, generalize regulatory framework

**Estimated Extension Effort:** 2-3 weeks for foundational generalizable framework

---

## 1. waterFRAME Current Capability Assessment

### 1.1 Water Quality Parameters ✅

| Parameter Category | Status | Examples |
|-----------------|---------|-----------|
| **Organic Matter** | ✅ Complete | BOD, COD, TSS, TDS |
| **Nutrients** | ✅ Complete | Total Nitrogen, Total Phosphorus, Ammonia, Nitrate, Nitrite |
| **Physical** | ✅ Complete | Temperature, Turbidity, Conductivity, pH |
| **Dissolved Gases** | ✅ Complete | Dissolved Oxygen |
| **Biological** | ✅ Complete | Coliform, E. coli |
| **Chemical** | ✅ Partial | Chlorine, Orthophosphate, Alkalinity |

**Assessment:** waterFRAME has **excellent coverage** of common regulatory parameters across EU, USEPA, and WHO frameworks.

**Source:** `/data/ontology/modules/qualities.ttl` (lines 20-151)

---

### 1.2 Regulatory Standards ✅

| Jurisdiction | Status | Classes Defined |
|-------------|---------|-----------------|
| **EU** | ✅ Present | `EUWaterFrameworkDirective` |
| **USEPA** | ✅ Present | `USEPAStandard` |
| **WHO** | ✅ Present | `WHOGuideline` |

**Base Class:** `RegulatoryStandard` (subClassOf `bfo:BFO_0000027` - Rule)

**Assessment:** waterFRAME **already supports multi-jurisdiction** standards. The framework is generalizable - new standards can be added as subclasses without changing core.

**Source:** `/data/ontology/modules/qualities.ttl` (lines 247-271)

---

### 1.3 Water Quality Requirements ✅

| Aspect | Status | Classes/Properties |
|--------|---------|-------------------|
| **Requirement Class** | ✅ Present | `WaterQualityRequirement` |
| **Parameter Linking** | ✅ Present | `hasWaterQualityParameter` |
| **Limit Values** | ✅ Present | `hasLimitValue` |
| **Limit Types** | ✅ Present | `MaximumLimit`, `MinimumLimit`, `RangeLimit`, `AverageLimit` |
| **Regulatory Link** | ✅ Present | `hasRegulatoryStandard` → `RegulatoryStandard` |

**Pattern:** Entity_Feature_Value from Manchester ODPs

**Assessment:** Strong, generalizable pattern for requirements. Can represent concentration-based limits.

**Gap:** **Load-based limits** (kg/day, lbs/day) not explicitly supported.

**Source:** `/data/ontology/modules/qualities.ttl` (lines 159-206)

---

### 1.4 Treatment Infrastructure ✅

| Infrastructure Type | Status | Classes |
|-------------------|---------|----------|
| **Facilities** | ✅ Complete | `WastewaterTreatmentPlant`, `DrinkingWaterPlant` |
| **Treatment Processes** | ✅ Complete | Primary, Secondary, Tertiary treatment classes |
| **Specific Units** | ✅ Complete | Screening, AerationTank, MembraneBioreactor, DisinfectionUnit, etc. |
| **Storage** | ✅ Complete | Potable, greywater, blackwater tanks |
| **Connections** | ✅ Complete | `InputPort`, `OutputPort`, `Conveyance` |
| **Natural Water Bodies** | ✅ Complete | River, Lake, Groundwater, Catchment |

**Assessment:** waterFRAME has **comprehensive infrastructure** modeling suitable for any jurisdiction.

**Source:** `/data/ontology/modules/core/material_entities.ttl` (lines 21-241)

---

### 1.5 Model Metadata ✅

| Aspect | Status | Classes |
|---------|---------|----------|
| **Process Models** | ✅ Present | `ProcessModel`, `SimulationModel` |
| **Variables** | ✅ Present | `ModelVariable`, `StateVariable`, `InputVariable`, `OutputVariable`, `Parameter` |
| **Inputs/Outputs** | ✅ Present | `ModelInput`, `ModelOutput` |
| **Decision Variables** | ✅ Present | `DecisionVariable`, `isDecisionVariable` property |
| **Capabilities** | ✅ Present | Optimization, Simulation, Mass Balance, etc. |
| **Implementation** | ✅ Present | `SoftwareSystem`, `apiEndpoint`, `apiVersion` |

**Assessment:** waterFRAME has **strong model metadata** for computational support and optimization.

**Source:** `/data/ontology/modules/information.ttl`, `/data/ontology/modules/capabilities.ttl`

---

### 1.6 Water Quality Observations ⚠️ PARTIAL

| Aspect | Status | Classes/Properties |
|---------|---------|-------------------|
| **Observation Class** | ✅ Present | `WaterQualityObservation` |
| **Parameter** | ✅ Present | `observedParameter` → `WaterQualityParameter` |
| **Value** | ✅ Present | `observedValue` (double) |
| **Location** | ⚠️ String | `observedAt` (string) |
| **Time** | ✅ Present | `observedOn` (dateTime) |
| **Sample** | ❌ Missing | No explicit sample class |
| **Sampling Point** | ❌ Missing | No explicit sampling point class |
| **Sampling Method** | ❌ Missing | No metadata on how sample was obtained |

**Assessment:** Basic observation pattern exists, but **lacks sampling metadata** critical for regulatory compliance (chain of custody, sampling protocols).

**Source:** `/data/ontology/modules/qualities.ttl` (lines 313-341)

---

## 2. WHOKG Concepts Not in waterFRAME

### 2.1 Observation Pattern Richness

| Concept | WHOKG | waterFRAME | Gap |
|---------|--------|-------------|------|
| **WaterSample** | ✅ | ❌ | No explicit sample class |
| **SamplingPoint** | ✅ | ❌ | No sampling point infrastructure |
| **WaterSampler** | ✅ | ❌ | No sampling equipment metadata |
| **isObtainedBy** | ✅ | ❌ | No link to sampling method |
| **isSampleOf** | ✅ | ⚠️ | Link via `observedAt` string, not explicit |
| **isTakenAt** | ✅ | ❌ | No explicit point location |

**Impact:**
- Cannot model chain of custody for regulatory samples
- Cannot distinguish between grab vs. composite samples
- Cannot model automated sampling equipment
- Cannot validate sampling location

---

### 2.2 Flow Direction Modeling

| Concept | WHOKG | waterFRAME | Gap |
|---------|--------|-------------|------|
| **Effluent vs. Influent** | ⚠️ Implicit in observation context | ⚠️ Implicit in port direction | No explicit regulatory flow direction |
| **Discharge Measurement** | ❌ | ❌ | No discharge rate modeling |
| **Flow Rate** | ❌ | ⚠️ Via model inputs | No explicit flow measurement class |

**Impact:**
- Regulations often distinguish influent (incoming) vs. effluent (outgoing) monitoring
- No explicit discharge point modeling for permits
- Flow rate measurements not linked to observations

---

### 2.3 Limit Types

| Limit Type | WHOKG | waterFRAME | Gap |
|------------|--------|-------------|------|
| **TBEL** (Technology-Based Effluent Limit) | ❌ | ❌ | No technology-based limit classification |
| **WQBEL** (Water Quality-Based Effluent Limit) | ❌ | ❌ | No water-quality-based limit classification |
| **Average vs. Maximum** | ✅ | ✅ | `AverageLimit`, `MaximumLimit` exist |
| **Range Limits** | ✅ | ✅ | `RangeLimit` exists |

**Impact:**
- USEPA permits distinguish between TBELs and WQBELs
- Cannot model technology-dependent vs. receiving-water-dependent limits

---

### 2.4 Compliance Status

| Concept | WHOKG | waterFRAME | Gap |
|---------|--------|-------------|------|
| **Compliance Status Class** | ❌ | ❌ | No explicit compliance representation |
| **Compliance Check** | ❌ | ❌ | No mechanism to check observed vs. limit |
| **Violation Flag** | ❌ | ❌ | No violation tracking |

**Impact:**
- Cannot explicitly represent "compliant" vs. "non-compliant"
- Compliance checks require external SPARQL queries (no ontology-level mechanism)
- No violation history tracking

---

### 2.5 Load-Based Measurements

| Concept | WHOKG | waterFRAME | Gap |
|---------|--------|-------------|------|
| **Load Calculation** | ❌ | ❌ | No flow × concentration pattern |
| **kg/day Limits** | ❌ | ❌ | Only concentration (mg/L) supported |
| **lbs/day Limits** | ❌ | ❌ | Imperial units not modeled |

**Impact:**
- Many jurisdictions (USEPA, Québec) specify load-based limits
- Cannot convert between concentration and load automatically
- No support for mass discharge rates

---

## 3. Gap Analysis Summary

### 3.1 Critical Gaps (Block Regulatory Compliance)

| Gap | Severity | Impact |
|------|-----------|---------|
| **Sampling Metadata** | 🔴 High | Cannot model regulatory sampling requirements |
| **Compliance Status** | 🔴 High | Cannot explicitly represent compliance state |
| **Flow Direction** | 🟡 Medium | Difficult to distinguish influent/effluent |
| **Load-based Limits** | 🟡 Medium | Cannot represent kg/day, lbs/day limits |

### 3.2 Moderate Gaps (Limit Expressiveness)

| Gap | Severity | Impact |
|------|-----------|---------|
| **TBEL/WQBEL Classification** | 🟡 Medium | Cannot represent USEPA permit structure |
| **Discharge Point Modeling** | 🟡 Medium | Cannot model effluent outfalls explicitly |
| **Chain of Custody** | 🟢 Low | Cannot track sample history |

### 3.3 Minor Gaps (Enhancement)

| Gap | Severity | Impact |
|------|-----------|---------|
| **Automated Sampling** | 🟢 Low | Cannot model continuous monitoring equipment |
| **Composite Samples** | 🟢 Low | Cannot distinguish grab vs. composite |

---

## 4. Integration Strategy

### 4.1 Guiding Principles

✅ **1. Generalizability Over Specificity**
- Create general patterns that can represent any jurisdiction
- Avoid hard-coding jurisdiction-specific rules in ontology
- Use controlled vocabularies for jurisdiction-specific concepts

✅ **2. Extend, Don't Replace**
- Keep waterFRAME's BFO alignment
- Add missing concepts as extensions
- Maintain compatibility with existing competency questions

✅ **3. Leverage WHOKG Patterns**
- Import or adapt WHOKG's observation/sampling patterns
- Use WHOKG's approach to water body representation
- Align with WHOKG's modular architecture

✅ **4. Data-Driven Framework**
- Make regulatory standards instances, not classes
- Allow new jurisdictions to be added without ontology changes
- Support user-defined limit types

### 4.2 Extension Architecture

```
waterFRAME (existing)
├── modules/core/material_entities
│   ├── WastewaterTreatmentPlant
│   ├── TreatmentUnit
│   ├── InputPort, OutputPort
│   └── River, Lake, Groundwater
│
├── modules/qualities
│   ├── WaterQualityParameter
│   ├── WaterQualityRequirement
│   ├── RegulatoryStandard (EU, USEPA, WHO)
│   └── WaterQualityObservation
│
├── modules/information
│   ├── ProcessModel
│   ├── ModelVariable, ModelInput, ModelOutput
│   └── DecisionVariable
│
└── modules/capabilities
    └── ModelCapability

EXTENSIONS NEEDED
├── NEW: sampling_metadata
│   ├── WaterSample (from WHOKG)
│   ├── SamplingPoint (from WHOKG)
│   ├── SamplingMethod (grab, composite, automatic)
│   └── isObtainedBy, isSampleOf, isTakenAt
│
├── NEW: flow_direction
│   ├── FlowDirection (Influent, Effluent)
│   ├── DischargeMeasurement
│   ├── FlowRate
│   └── DischargePoint
│
├── NEW: compliance_checking
│   ├── ComplianceStatus (Compliant, NonCompliant, Pending)
│   ├── ComplianceCheck
│   ├── ViolationRecord
│   └── complianceStatus, lastCheckedDate
│
└── NEW: regulatory_limit_types
    ├── LimitType (generalize existing)
    │   ├── TechnologyBasedLimit (TBEL)
    │   ├── WaterQualityBasedLimit (WQBEL)
    │   ├── ConcentrationLimit (mg/L, μg/L)
    │   └── LoadLimit (kg/day, lbs/day)
    └── LoadCalculation (flow × concentration)
```

### 4.3 Phased Extension Plan

**Phase 1: Sampling Metadata (3-5 days)**
- [ ] Import/adapt `WaterSample` from WHOKG
- [ ] Import/adapt `SamplingPoint` from WHOKG
- [ ] Add `SamplingMethod` enumeration
- [ ] Link `WaterQualityObservation` → `WaterSample`
- [ ] Add chain of custody properties

**Phase 2: Flow Direction (2-3 days)**
- [ ] Create `FlowDirection` enumeration (Influent, Effluent)
- [ ] Add `hasFlowDirection` to observation/sample
- [ ] Create `DischargeMeasurement` class
- [ ] Add `DischargePoint` class linked to treatment plant
- [ ] Link flow measurements to observations

**Phase 3: Compliance Checking (3-5 days)**
- [ ] Create `ComplianceStatus` class with states
- [ ] Add `complianceStatus` property to observation
- [ ] Create `ComplianceCheck` class
- [ ] Add `ViolationRecord` for non-compliance
- [ ] Model `lastCheckedDate` for compliance verification

**Phase 4: Regulatory Limit Generalization (2-3 days)**
- [ ] Generalize `LimitType` pattern
- [ ] Add `TechnologyBasedLimit` subclass
- [ ] Add `WaterQualityBasedLimit` subclass
- [ ] Add `ConcentrationLimit` subclass
- [ ] Add `LoadLimit` subclass
- [ ] Create `LoadCalculation` pattern

**Phase 5: Integration & Testing (3-5 days)**
- [ ] Create test data for different jurisdictions
- [ ] Write SPARQL compliance checking queries
- [ ] Test load calculations (flow × concentration)
- [ ] Validate chain of custody modeling
- [ ] Document extension patterns

**Total Effort:** 13-21 days (2-3 weeks)

---

## 5. Example Integration Pattern

### 5.1 Sampling Metadata

```turtle
# NEW: Sample class (from WHOKG pattern)
wf:WaterSample a owl:Class ;
    rdfs:subClassOf bfo:BFO_0000040 ;
    rdfs:label "Water sample" ;
    rdfs:comment "A sample of water taken for quality analysis." .

# Sampling method types
wf:SamplingMethod a owl:Class ;
    rdfs:label "Sampling method" ;
    rdfs:comment "The method used to collect a water sample." .

wf:GrabSample a owl:Class ;
    rdfs:subClassOf wf:SamplingMethod ;
    rdfs:label "Grab sample" ;
    rdfs:comment "A single sample taken at a specific time." .

wf:CompositeSample a owl:Class ;
    rdfs:subClassOf wf:SamplingMethod ;
    rdfs:label "Composite sample" ;
    rdfs:comment "A sample composed of multiple aliquots taken over time." .

wf:AutomaticSample a owl:Class ;
    rdfs:subClassOf wf:SamplingMethod ;
    rdfs:label "Automatic sample" ;
    rdfs:comment "A sample collected by automated equipment." .

# Properties
wf:usesSamplingMethod a owl:ObjectProperty ;
    rdfs:domain wf:WaterSample ;
    rdfs:range wf:SamplingMethod .

wf:isObtainedBy a owl:ObjectProperty ;
    rdfs:domain wf:WaterSample ;
    rdfs:range wf:WaterSampler .

wf:isSampleOf a owl:ObjectProperty ;
    rdfs:domain wf:WaterSample ;
    rdfs:range bfo:BFO_0000040 .  # Material entity

# Link observation to sample
wf:hasSample a owl:ObjectProperty ;
    rdfs:domain wf:WaterQualityObservation ;
    rdfs:range wf:WaterSample .
```

---

### 5.2 Flow Direction

```turtle
# Flow direction enumeration
wf:FlowDirection a owl:Class ;
    rdfs:label "Flow direction" ;
    rdfs:comment "Direction of water flow through system." .

wf:InfluentFlow a owl:Class ;
    rdfs:subClassOf wf:FlowDirection ;
    rdfs:label "Influent flow" ;
    rdfs:comment "Water flowing into a treatment system." .

wf:EffluentFlow a owl:Class ;
    rdfs:subClassOf wf:FlowDirection ;
    rdfs:label "Effluent flow" ;
    rdfs:comment "Water flowing out of a treatment system." .

# Add to observation
wf:hasFlowDirection a owl:ObjectProperty ;
    rdfs:domain wf:WaterSample ;
    rdfs:range wf:FlowDirection .

# Discharge point
wf:DischargePoint a owl:Class ;
    rdfs:subClassOf bfo:BFO_0000040 ;
    rdfs:label "Discharge point" ;
    rdfs:comment "The location where treated water is discharged." .

wf:hasDischargePoint a owl:ObjectProperty ;
    rdfs:domain wf:WaterSample ;
    rdfs:range wf:DischargePoint .

# Discharge measurement
wf:DischargeMeasurement a owl:Class ;
    rdfs:subClassOf bfo:BFO_0000052 ;  # Processual entity
    rdfs:label "Discharge measurement" ;
    rdfs:comment "Measurement of water discharge rate." .

wf:flowRate a owl:DatatypeProperty ;
    rdfs:domain wf:DischargeMeasurement ;
    rdfs:range xsd:double ;
    rdfs:comment "Discharge rate (e.g., m³/day, MGD)." .

wf:flowRateUnit a owl:ObjectProperty ;
    rdfs:domain wf:DischargeMeasurement ;
    rdfs:range qudt:Unit .
```

---

### 5.3 Compliance Checking

```turtle
# Compliance status
wf:ComplianceStatus a owl:Class ;
    rdfs:label "Compliance status" ;
    rdfs:comment "The compliance status of an observation with respect to requirements." .

wf:Compliant a owl:Class ;
    rdfs:subClassOf wf:ComplianceStatus ;
    rdfs:label "Compliant" ;
    rdfs:comment "Observation meets all applicable requirements." .

wf:NonCompliant a owl:Class ;
    rdfs:subClassOf wf:ComplianceStatus ;
    rdfs:label "Non-compliant" ;
    rdfs:comment "Observation exceeds one or more requirements." .

wf:PendingCompliance a owl:Class ;
    rdfs:subClassOf wf:ComplianceStatus ;
    rdfs:label "Pending compliance" ;
    rdfs:comment "Compliance status not yet determined." .

# Link observation to compliance
wf:hasComplianceStatus a owl:ObjectProperty ;
    rdfs:domain wf:WaterQualityObservation ;
    rdfs:range wf:ComplianceStatus .

# Compliance check
wf:ComplianceCheck a owl:Class ;
    rdfs:subClassOf bfo:BFO_0000052 ;  # Processual entity
    rdfs:label "Compliance check" ;
    rdfs:comment "An event where compliance is verified." .

wf:checksObservation a owl:ObjectProperty ;
    rdfs:domain wf:ComplianceCheck ;
    rdfs:range wf:WaterQualityObservation .

wf:checkedAgainstRequirement a owl:ObjectProperty ;
    rdfs:domain wf:ComplianceCheck ;
    rdfs:range wf:WaterQualityRequirement .

wf:lastCheckedDate a owl:DatatypeProperty ;
    rdfs:domain wf:WaterQualityObservation ;
    rdfs:range xsd:dateTime .

# Violation record
wf:ViolationRecord a owl:Class ;
    rdfs:subClassOf bfo:BFO_0000052 ;
    rdfs:label "Violation record" ;
    rdfs:comment "A record of a regulatory violation." .

wf:violationAmount a owl:DatatypeProperty ;
    rdfs:domain wf:ViolationRecord ;
    rdfs:range xsd:double ;
    rdfs:comment "The amount by which the limit was exceeded." .
```

---

### 5.4 Regulatory Limit Generalization

```turtle
# Generalize limit types
wf:TechnologyBasedLimit a owl:Class ;
    rdfs:subClassOf wf:LimitType ;
    rdfs:label "Technology-based effluent limit (TBEL)" ;
    rdfs:comment "Minimum level of effluent quality attainable by available technology." .

wf:WaterQualityBasedLimit a owl:Class ;
    rdfs:subClassOf wf:LimitType ;
    rdfs:label "Water quality-based effluent limit (WQBEL)" ;
    rdfs:comment "Limit required to protect receiving water quality." .

wf:ConcentrationLimit a owl:Class ;
    rdfs:subClassOf wf:LimitType ;
    rdfs:label "Concentration limit" ;
    rdfs:comment "Limit expressed as concentration (e.g., mg/L, μg/L)." .

wf:LoadLimit a owl:Class ;
    rdfs:subClassOf wf:LimitType ;
    rdfs:label "Load limit" ;
    rdfs:comment "Limit expressed as mass per unit time (e.g., kg/day, lbs/day)." .

# Load calculation
wf:LoadCalculation a owl:Class ;
    rdfs:subClassOf bfo:BFO_0000052 ;
    rdfs:label "Load calculation" ;
    rdfs:comment "Derivation of pollutant load from concentration and flow." .

wf:fromConcentration a owl:ObjectProperty ;
    rdfs:domain wf:LoadCalculation ;
    rdfs:range wf:WaterQualityObservation .

wf:fromFlowRate a owl:ObjectProperty ;
    rdfs:domain wf:LoadCalculation ;
    rdfs:range wf:DischargeMeasurement .

wf:calculatedLoad a owl:DatatypeProperty ;
    rdfs:domain wf:LoadCalculation ;
    rdfs:range xsd:double ;
    rdfs:comment "Calculated load (kg/day, lbs/day)." .
```

---

## 6. Example Usage Patterns

### 6.1 Compliance Checking SPARQL Query

```sparql
PREFIX wf: <https://ugentbiomath.github.io/waterframe#>

# Find observations exceeding requirements (any jurisdiction)
SELECT ?observation ?param ?observedValue ?limitValue ?standard
WHERE {
    # Get water quality observation
    ?observation a wf:WaterQualityObservation .
    ?observation wf:observedParameter ?param .
    ?observation wf:observedValue ?observedValue .

    # Get applicable requirement
    ?observation wf:hasComplianceStatus wf:NonCompliant .

    # Get requirement and limit
    ?requirement a wf:WaterQualityRequirement .
    ?requirement wf:hasWaterQualityParameter ?param .
    ?requirement wf:hasLimitValue ?limitValue .
    ?requirement wf:hasLimitType wf:MaximumLimit .

    # Get regulatory standard (generic, could be EU, USEPA, etc.)
    ?requirement wf:hasRegulatoryStandard ?standard .
}
```

---

### 6.2 Load Calculation SPARQL Query

```sparql
PREFIX wf: <https://ugentbiomath.github.io/waterframe#>

# Calculate load from concentration and flow (general)
SELECT ?loadCalc ?loadKgDay ?param ?flowDirection
WHERE {
    # Find concentration observation
    ?concObs a wf:WaterQualityObservation .
    ?concObs wf:observedParameter ?param .
    ?concObs wf:hasFlowDirection wf:EffluentFlow .
    ?concObs wf:observedValue ?concValueMgPerL .

    # Find flow measurement
    ?flowObs a wf:DischargeMeasurement .
    ?flowObs wf:flowRate ?flowValueM3PerDay .
    ?flowObs wf:flowRateUnit <http://qudt.org/vocab/unit/CubicMPerDay> .

    # Load calculation links them
    ?loadCalc wf:fromConcentration ?concObs .
    ?loadCalc wf:fromFlowRate ?flowObs .
    ?loadCalc wf:calculatedLoad ?loadKgDay .
}
```

---

### 6.3 Sample Chain of Custody SPARQL Query

```sparql
PREFIX wf: <https://ugentbiomath.github.io/waterframe#>

# Track sample from collection to analysis
SELECT ?sample ?samplingMethod ?samplingPoint ?dischargePoint ?observation ?analysisDate
WHERE {
    # Sample information
    ?sample a wf:WaterSample .
    ?sample wf:usesSamplingMethod ?samplingMethod .
    ?sample wf:isTakenAt ?samplingPoint .
    ?sample wf:hasDischargePoint ?dischargePoint .

    # Observation linked to sample
    ?observation a wf:WaterQualityObservation .
    ?observation wf:hasSample ?sample .
    ?observation wf:observedOn ?analysisDate .

    # Sampling point location
    ?samplingPoint rdfs:label ?pointName .
    ?dischargePoint rdfs:label ?dischargeName .
}
```

---

## 7. Assessment Summary

### 7.1 Can waterFRAME Support General Regulatory Compliance? ✅ YES

| Capability | Current Status | Extensibility | Assessment |
|------------|---------------|---------------|------------|
| **Multi-jurisdiction standards** | ✅ Yes | ✅ Easy | `RegulatoryStandard` pattern is generalizable |
| **Water quality parameters** | ✅ Complete | ✅ Easy | Parameter classes cover all major requirements |
| **Treatment infrastructure** | ✅ Complete | ✅ Easy | Sufficient for any jurisdiction's systems |
| **Compliance checking** | ⚠️ Partial | 🟡 Medium | Needs `ComplianceStatus` extension |
| **Sampling metadata** | ❌ Missing | 🟢 Easy | Can import WHOKG pattern |
| **Flow direction** | ⚠️ Implicit | 🟢 Easy | Add `FlowDirection` property |
| **Load-based limits** | ❌ Missing | 🟡 Medium | Add `LoadLimit` and calculation pattern |
| **Limit types (TBEL/WQBEL)** | ❌ Missing | 🟢 Easy | Add as subclasses of `LimitType` |

### 7.2 Strengths for Generalizability

✅ **1. Modular Architecture**
- Clear separation of concerns (materials, qualities, information, capabilities)
- New modules can be added without affecting existing structure

✅ **2. BFO Alignment**
- Philosophically grounded upper ontology
- Ensures consistency and interoperability

✅ **3. Pattern-Based Design**
- Uses established ODPs (Entity_Feature_Value)
- Patterns are reusable and generalizable

✅ **4. Regulatory Framework Independence**
- `RegulatoryStandard` is abstract base class
- Jurisdictions are instances/subclasses, not hard-coded

✅ **5. Unit Support**
- QUDT vocabulary integration
- Supports metric and imperial units (with extensions)

### 7.3 Extensions Required

| Module | Complexity | Dependencies | Impact |
|--------|-------------|---------------|---------|
| **Sampling Metadata** | 🟢 Low | None | Enables chain of custody, regulatory sampling |
| **Flow Direction** | 🟢 Low | None | Enables influent/effluent distinction |
| **Compliance Checking** | 🟡 Medium | Sampling, Flow | Enables explicit compliance status |
| **Load Calculations** | 🟡 Medium | Flow, Units | Enables load-based regulations |
| **Limit Type Generalization** | 🟢 Low | None | Enables TBEL/WQBEL modeling |

### 7.4 Effort Estimate

| Phase | Days | Complexity |
|-------|-------|------------|
| Sampling Metadata | 3-5 | 🟢 Low |
| Flow Direction | 2-3 | 🟢 Low |
| Compliance Checking | 3-5 | 🟡 Medium |
| Regulatory Limit Generalization | 2-3 | 🟢 Low |
| Load Calculations | 2-3 | 🟡 Medium |
| Integration & Testing | 3-5 | 🟡 Medium |
| **Total** | **15-24** | **Medium** |

---

## 8. Recommendations

### 8.1 Immediate Actions

1. ✅ **Add Sampling Metadata Module**
   - Import/adapt `WaterSample` and `SamplingPoint` from WHOKG
   - Add `SamplingMethod` enumeration
   - Link observations to samples

2. ✅ **Add Flow Direction Property**
   - Create `FlowDirection` enumeration
   - Add `hasFlowDirection` to samples/observations
   - Create `DischargePoint` class

3. ✅ **Create Compliance Status Class**
   - Define `ComplianceStatus` with states
   - Add `hasComplianceStatus` property
   - Enable compliance checking queries

### 8.2 Design Principles for Extensions

✅ **Generalizability First**
- Make regulatory patterns work for ANY jurisdiction
- Use controlled vocabularies, not hard-coded classes
- Allow user-defined limit types

✅ **Pattern Reuse**
- Leverage WHOKG's proven patterns
- Adapt to waterFRAME's BFO alignment
- Maintain consistency with existing ODPs

✅ **Data-Driven Framework**
- Standards as instances, not classes
- New jurisdictions add data, not code
- Support dynamic regulatory updates

✅ **Backwards Compatibility**
- Maintain existing waterFRAME structure
- Extensions are additive
- No breaking changes to current models

### 8.3 Future Enhancements

- Add `AutomatedSampler` class for continuous monitoring
- Add `CompositeSample` distinction from grab samples
- Create `RegulatoryPermit` class for permit-level management
- Add `ComplianceHistory` tracking over time
- Model permit conditions and special requirements

---

## 9. Conclusion

**Question Answered:** ✅ **YES, waterFRAME can support general regulatory compliance** with strategic extensions.

**Key Points:**

1. **Strong Foundation**
   - waterFRAME already has multi-jurisdiction support (EU, USEPA, WHO)
   - Comprehensive water quality parameters
   - Strong treatment infrastructure and model metadata

2. **Targeted Gaps**
   - Sampling metadata missing (critical for regulatory compliance)
   - Compliance checking not explicit
   - Flow direction and load-based limits need extension

3. **Generalizable Strategy**
   - Use WHOKG patterns for sampling/observations
   - Create general `RegulatoryStandard` pattern (not jurisdiction-specific)
   - Support data-driven regulatory frameworks

4. **Low Complexity**
   - Extensions are additive (no changes to core)
   - Most gaps are 🟢 Low to 🟡 Medium complexity
   - Estimated 2-3 weeks for foundational framework

5. **High Value**
   - Enables regulatory compliance in ANY jurisdiction
   - Supports compliance checking and violation tracking
   - Maintains BFO alignment and modular architecture

**Strategic Recommendation:**

Proceed with extension strategy in 5 phases:
1. Sampling metadata (WHOKG integration)
2. Flow direction modeling
3. Compliance checking infrastructure
4. Regulatory limit generalization
5. Integration and testing

This approach will enable waterFRAME to describe water systems and verify regulatory compliance across any jurisdiction (EU, USEPA, Québec, China, Australia, etc.) while maintaining generalizability and extensibility.

---

**End of Research Document**
