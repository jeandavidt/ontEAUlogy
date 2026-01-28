# waterFRAME Ontology: Class Origins and Integration Analysis

**Author:** Analysis for Ghent Case Study Alignment
**Date:** 2026-01-27
**Purpose:** Clarify which classes come from which ontologies and identify potential conflicts

---

## Executive Summary

This document traces the origins of all classes in the waterFRAME ontology and answers key questions about imports, local definitions, and potential conflicts between integrated ontologies.

**Key Findings:**
- ✅ Most classes are **locally defined** with `wf:` prefix (not imported from WaWO+)
- ✅ Only **BFO, ENVO, and SOSA** are actually imported
- ⚠️ **WaWO+ is NOT imported** - it's used as *inspiration* only (documented as future work)
- ⚠️ **Competing water type classifications** exist between ENVO and waterFRAME
- 📋 **Action items** identified for ontology enhancement

---

## 1. Class Origin Breakdown

### 1.1 Imported Ontologies (Actually Used)

| Ontology | Prefix | Import Status | Usage |
|----------|--------|---------------|-------|
| **BFO** (Basic Formal Ontology) | `bfo:` | ✅ Imported | Upper ontology foundation |
| **ENVO** (Environment Ontology) | `envo:` | ✅ Imported | Environmental context, water bodies, biomes |
| **SOSA** (Sensor, Observation, Sample, Actuator) | `sosa:` | ✅ Imported | Observation and sensor patterns |
| **QUDT** (Quantities, Units, Dimensions, Types) | `qudt:`, `unit:` | ⚠️ Referenced but not formally imported | Units and quantities |

### 1.2 Referenced But NOT Imported

| Ontology | Status | Notes |
|----------|--------|-------|
| **WaWO+** | 📋 Future work | Evaluated but not integrated. Used as inspiration for process units. See `envo_alignment.ttl` line 312: "Layer 4: Domain-specific - WaWO+ for detailed treatment processes (future)" |
| **PROV-O** | 📋 Commented out | Provenance tracking (planned) |
| **CHEBI** | ⚠️ Indirect via ENVO | Chemical entities accessible through ENVO import |

### 1.3 Locally Defined (waterFRAME - `wf:` prefix)

**All of these are defined IN waterframe, not imported:**

#### Material Entities (`material_entities.ttl`)
```
wf:WaterSystemComponent (base class)
├── Storage Tanks
│   ├── wf:StorageTank
│   ├── wf:RainwaterStorageTank
│   ├── wf:PotableWaterStorageTank
│   ├── wf:PurifiedGreywaterStorageTank
│   └── wf:BlackwaterStorageTank
├── Treatment Infrastructure
│   ├── wf:TreatmentUnit
│   ├── wf:MembraneBioreactorUnit
│   ├── wf:ReverseOsmosisUnit
│   └── wf:InfiltrationUnit
├── Usage Points
│   ├── wf:WaterUsagePoint
│   ├── wf:BathingFixture
│   ├── wf:CleaningFixture
│   ├── wf:Appliance
│   └── wf:Toilet
└── Conveyance
    └── wf:Conveyance

wf:Port (OntoCAPE-inspired, but locally defined)
├── wf:InputPort
└── wf:OutputPort

Treatment Facilities
├── wf:DrinkingWaterPlant
└── wf:WastewaterTreatmentPlant

WWTP Process Units (LOCALLY DEFINED, inspired by WaWO+ but NOT imported)
├── wf:WWTPTreatmentProcess
│   ├── wf:PrimaryTreatment
│   │   ├── wf:Screening
│   │   ├── wf:GritRemoval
│   │   └── wf:PrimarySettler
│   ├── wf:SecondaryTreatment
│   │   ├── wf:AerationTank
│   │   ├── wf:SecondarySettler
│   │   └── wf:MembraneBioreactor
│   └── wf:TertiaryTreatment
│       ├── wf:NitrificationTank
│       ├── wf:DenitrificationTank
│       ├── wf:PhosphorusRemovalTank
│       └── wf:DisinfectionUnit

Industrial Facilities (LOCALLY DEFINED)
├── wf:IndustrialFacility
│   ├── wf:TextileIndustry
│   ├── wf:FoodProcessingIndustry
│   ├── wf:ElectronicsManufacturing
│   ├── wf:PharmaceuticalIndustry
│   └── wf:Brewery

Natural Water Bodies (LOCALLY DEFINED, with ENVO alignments)
├── wf:River (rdfs:seeAlso envo:00000022)
├── wf:RiverSegment
├── wf:Lake (rdfs:seeAlso envo:00000020)
├── wf:Groundwater
└── wf:Catchment (rdfs:seeAlso envo:00000292)

Residential/Urban
├── wf:ResidentialDistrict
└── wf:Household
```

#### Water Quality Parameters (`qualities.ttl`)
**ALL locally defined as `wf:` classes:**

```
wf:WaterQualityParameter (base class, also rdfs:subClassOf sosa:ObservableProperty)
├── Physical Parameters
│   ├── wf:Temperature
│   ├── wf:Turbidity
│   ├── wf:Conductivity
│   ├── wf:TSS (Total Suspended Solids)
│   ├── wf:TDS (Total Dissolved Solids)
│   └── wf:pH
├── Chemical Parameters
│   ├── wf:BOD (Biochemical Oxygen Demand)
│   ├── wf:COD (Chemical Oxygen Demand)
│   ├── wf:DissolvedOxygen
│   ├── wf:Alkalinity
│   └── wf:Chlorine
├── Nutrients
│   ├── wf:TotalNitrogen
│   ├── wf:TotalPhosphorus
│   ├── wf:Ammonia
│   ├── wf:Nitrate
│   ├── wf:Nitrite
│   └── wf:Orthophosphate
└── Biological
    └── wf:Coliform
```

**Source:** These are **locally defined** in waterFRAME. WaWO+ has similar concepts (BOD, COD, SS, TN, TP as data properties), but waterFRAME models them as classes following the Entity-Feature-Value pattern. This is a **deliberate design difference**.

#### Sampling Module (`sampling.ttl`)
**ALL locally defined as `wf:` classes:**

```
wf:WaterSample
wf:SamplingPoint
├── wf:InfluentSamplingPoint
├── wf:EffluentSamplingPoint
├── wf:ProcessSamplingPoint
├── wf:AmbientSamplingPoint
└── wf:DischargePoint

wf:SamplingMethod
├── wf:GrabSampling
├── wf:CompositeSampling
│   ├── wf:TimeCompositeSampling
│   └── wf:FlowCompositeSampling
├── wf:AutomatedSampling
└── wf:ContinuousSampling

wf:SamplingEquipment
├── wf:Autosampler
├── wf:OnlineSensor
└── wf:ManualSampler

wf:FlowDirection
├── wf:InfluentFlow
├── wf:EffluentFlow
├── wf:ProcessFlow
└── wf:BypassFlow
```

**Source:** These classes were added to waterFRAME based on **WHOKG (WHO Knowledge Graph) patterns** as mentioned in the `sampling.ttl` header comment. They are **NOT from SOSA** (though they integrate with SOSA Observation).

**Evidence:** `sampling.ttl` line 19: "Adapted from WHOKG WaterSample pattern"

---

## 2. Why Most Classes are `wf:` Prefixed

**Answer:** waterFRAME follows a **"bridge pattern" integration strategy** rather than direct import:

1. **Local Definition:** Define classes locally in waterFRAME with `wf:` prefix
2. **Alignment:** Use `rdfs:seeAlso` and `rdfs:comment` to reference equivalent classes in external ontologies
3. **Bridge Modules:** Create explicit bridge files (`envo_alignment.ttl`, `sosa_alignment.ttl`) that define mappings

**Rationale:**
- Maintains **control** over class definitions and axioms
- Avoids **import bloat** (e.g., ENVO has 9000+ classes we don't all need)
- Allows **customization** for water reuse engineering domain
- Enables **selective integration** - take what's needed, leave what's not

**Example:**
```turtle
# waterFRAME defines its own River class
wf:River rdfs:subClassOf bfo:BFO_0000040 ;
    rdfs:label "River" ;
    rdfs:comment "A natural flowing watercourse." .

# But acknowledges ENVO's equivalent class
wf:River rdfs:seeAlso envo:00000022 ;  # ENVO's river class
    rdfs:comment "Aligned with ENVO river concept for environmental context" .
```

---

## 3. Water Flow Types: Current vs. Needed Approach

### 3.1 Current Implementation (Simple Classification)

**File:** `properties.ttl` lines 78-114

```turtle
# Current: Simple class-based classification
wf:WaterFlow a owl:Class .

wf:GreywaterFlow rdfs:subClassOf wf:WaterFlow .
wf:BlackwaterFlow rdfs:subClassOf wf:WaterFlow .
wf:RainwaterFlow rdfs:subClassOf wf:WaterFlow .
wf:PotableWaterFlow rdfs:subClassOf wf:WaterFlow .
wf:ReclaimedWaterFlow rdfs:subClassOf wf:WaterFlow .

# Used at ports:
wf:hasFlowType a owl:ObjectProperty ;
    rdfs:domain wf:Port ;
    rdfs:range wf:WaterFlow .
```

### 3.2 WaWO+ Approach (Quality-Based Classification)

**WaWO+ defines water composition based on concentration thresholds:**

```sparql
# From WaWO+ specification
# DrinkingWaterComposition is classified when:
#   BOD <= 5 mg/L
#   COD <= 10 mg/L
#   SS <= 5 mg/L
#   TN <= 1 mg/L
#   TP <= 0.1 mg/L

# WastewaterComposition is classified when:
#   BOD > 300 mg/L OR
#   COD > 500 mg/L
```

### 3.3 RECOMMENDED: Adopt WaWO+ Quality-Based Approach

**Action Item 1: Add quality-based water classification rules to waterFRAME**

This should be added to `qualities.ttl`:

```turtle
# Define water composition classes based on quality thresholds
wf:WaterComposition a owl:Class ;
    rdfs:label "Water composition" ;
    rdfs:comment "Classification of water based on quality characteristics" .

wf:DrinkingWaterQuality rdfs:subClassOf wf:WaterComposition ;
    rdfs:label "Drinking water quality" ;
    rdfs:comment """Water meeting drinking water standards:
    - BOD ≤ 5 mg/L
    - COD ≤ 10 mg/L
    - TSS ≤ 5 mg/L
    - TN ≤ 1 mg/L
    - TP ≤ 0.1 mg/L""" .

wf:WastewaterQuality rdfs:subClassOf wf:WaterComposition ;
    rdfs:label "Wastewater quality" ;
    rdfs:comment """Water with wastewater characteristics:
    - BOD > 300 mg/L OR
    - COD > 500 mg/L""" .

wf:ReclaimedWaterQuality rdfs:subClassOf wf:WaterComposition ;
    rdfs:label "Reclaimed water quality" ;
    rdfs:comment """Treated water suitable for non-potable reuse:
    - Intermediate quality between drinking water and wastewater""" .

# Link composition to flow types
wf:hasWaterComposition a owl:ObjectProperty ;
    rdfs:domain wf:Port ;
    rdfs:range wf:WaterComposition .
```

**Then add SPARQL or SWRL rules to automatically classify water based on observed quality parameters.**

---

## 4. Treatment Process Units: Origins

### 4.1 Current State

**Answer:** Process units like `wf:Screening`, `wf:AerationTank`, etc. are **LOCALLY DEFINED** in waterFRAME.

**File:** `material_entities.ttl` lines 128-183

**Evidence:**
```turtle
wf:WWTPTreatmentProcess rdfs:subClassOf wf:WaterSystemComponent ;
    rdfs:label "WWTP treatment process" .

wf:PrimaryTreatment rdfs:subClassOf wf:WWTPTreatmentProcess .
wf:Screening rdfs:subClassOf wf:PrimaryTreatment .
wf:AerationTank rdfs:subClassOf wf:SecondaryTreatment .
# ... etc
```

### 4.2 Relationship to WaWO+

**WaWO+ has similar classes:**
- `wawo:WastewaterTreatment`
- `wawo:SecondaryTreatment`
- `wawo:Disinfection`
- `wawo:Coagulation`

**But waterFRAME is NOT importing them.**

**Rationale (from code comments):**
- WaWO+ evaluation (see `research/ontologies/WaWO/WaWO_Plus_Evaluation_Report.md`) recommended **EXTEND** approach
- Issues with WaWO+ imports (broken URIs, incomplete implementation)
- WaWO+ uses different modeling approach (processes vs. physical units)

### 4.3 Design Decision

**waterFRAME models:**
- **Physical infrastructure** (the tank, the screen unit)
- **Port-based topology** (how they connect)

**WaWO+ models:**
- **Processes** (the treatment activity)
- **Flow relationships** (what produces/receives what)

**These are complementary but different perspectives.**

---

## 5. Regulatory Limits: Current vs. Needed Approach

### 5.1 Current Implementation

**File:** `qualities.ttl` lines 156-209

```turtle
wf:WaterQualityRequirement a owl:Class .

wf:hasWaterQualityParameter a owl:ObjectProperty .
wf:hasLimitValue a owl:DatatypeProperty .
wf:hasLimitType a owl:ObjectProperty .

# Limit types:
wf:MaximumLimit rdfs:subClassOf wf:LimitType .
wf:MinimumLimit rdfs:subClassOf wf:LimitType .
wf:RangeLimit rdfs:subClassOf wf:LimitType .
wf:AverageLimit rdfs:subClassOf wf:LimitType .
```

### 5.2 RECOMMENDED: Align with Water Composition Classification

**Action Item 2: Link regulatory requirements to composition classification**

Maximum/minimum limits should be **connected to** the quality-based water classification:

```turtle
# Example: EU drinking water standard
wf:EU_DrinkingWater_BOD a wf:WaterQualityRequirement ;
    wf:hasWaterQualityParameter wf:BOD ;
    wf:hasLimitValue "5.0"^^xsd:double ;
    wf:hasLimitType wf:MaximumLimit ;
    wf:hasRegulatoryStandard wf:EUWaterFrameworkDirective ;
    # NEW: Link to composition class
    wf:definesComposition wf:DrinkingWaterQuality .
```

This creates a **consistent framework**: regulatory limits DEFINE what counts as drinking water vs. wastewater quality.

---

## 6. Competing/Conflicting Classifications

### 6.1 Water Type Classifications: ENVO vs. waterFRAME

**CONFLICT IDENTIFIED:** Two competing taxonomies for water types

#### ENVO Water Types (Material Entities)
From `envo_alignment.ttl`:
```
envo:00002006 - water (material entity)
├── envo:00002018 - sewage
├── envo:00003097 - drinking water
├── envo:00002042 - surface water
├── envo:00002001 - groundwater
├── envo:00002223 - grey water
└── envo:00002044 - wastewater
```

#### waterFRAME Water Types (Flow Classifications)
From `properties.ttl`:
```
wf:WaterFlow (class for flow classification)
├── wf:GreywaterFlow
├── wf:BlackwaterFlow
├── wf:RainwaterFlow
├── wf:PotableWaterFlow
└── wf:ReclaimedWaterFlow
```

**Analysis:**
- **ENVO:** Material-based (what IS the water substance)
- **waterFRAME:** Flow-based (how is water classified in the system)

**Current Alignment:**
```turtle
# From envo_alignment.ttl lines 107-111
wf:Greywater rdfs:seeAlso envo:00002223 ;
    rdfs:comment "waterFRAME uses more specific greywater classification" .

wf:Blackwater rdfs:seeAlso envo:00002018 ;
    rdfs:comment "Blackwater is a type of sewage (ENVO:00002018)" .
```

**RECOMMENDATION:**

**Action Item 3: Harmonize water type classifications**

1. **Keep both** - they serve different purposes:
   - Use `envo:` for material composition (what the water IS chemically/biologically)
   - Use `wf:` for flow classification (how it's classified in the engineered system)

2. **Add explicit mappings:**
```turtle
wf:PotableWaterFlow owl:equivalentClass [
    a owl:Restriction ;
    owl:onProperty wf:hasWaterType ;
    owl:someValuesFrom envo:00003097  # drinking water
] .

wf:BlackwaterFlow owl:equivalentClass [
    a owl:Restriction ;
    owl:onProperty wf:hasWaterType ;
    owl:someValuesFrom envo:00002018  # sewage
] .
```

3. **Document the distinction clearly** in comments

### 6.2 Observation Patterns: SOSA vs. waterFRAME

**NO CONFLICT** - Clean integration via `rdfs:subClassOf`:

```turtle
# From sosa_alignment.ttl
wf:WaterQualityParameter rdfs:subClassOf sosa:ObservableProperty .
wf:WaterQualityObservation rdfs:subClassOf sosa:Observation .
```

This is **correct integration** - waterFRAME specializes SOSA, doesn't compete with it.

### 6.3 Treatment Facilities: ENVO vs. waterFRAME

**MINOR ALIGNMENT ISSUE** - Currently uses `rdfs:seeAlso`:

```turtle
# From envo_alignment.ttl lines 82-88
wf:WastewaterTreatmentPlant rdfs:subClassOf wf:WaterSystemComponent ;
    rdfs:comment "Aligned with ENVO:00002043" ;
    rdfs:seeAlso envo:00002043 .
```

**RECOMMENDATION:**

**Action Item 4: Consider stronger alignment**

Could use `owl:equivalentClass` or make `wf:WastewaterTreatmentPlant` a subclass of the ENVO class:

```turtle
# Option 1: Equivalent (if truly the same concept)
wf:WastewaterTreatmentPlant owl:equivalentClass envo:00002043 .

# Option 2: Subclass (if waterFRAME adds engineering detail)
wf:WastewaterTreatmentPlant rdfs:subClassOf envo:00002043 ;
    rdfs:subClassOf wf:WaterSystemComponent .
```

---

## 7. Missing from Current Ontology

### 7.1 Process Water Flow Type

**IDENTIFIED IN USE CASE DATA** but **NOT IN ONTOLOGY:**

In `brewco.ttl` line 42:
```turtle
ghent:BrewCo_ProcessWater_Out a wf:OutputPort ;
    wf:hasFlowType wf:ProcessWaterFlow .  # ← This class doesn't exist!
```

**Action Item 5: Add missing flow types to properties.ttl**

```turtle
wf:ProcessWaterFlow rdfs:subClassOf wf:WaterFlow ;
    rdfs:label "Process water flow" ;
    rdfs:comment "Water used in industrial processes" .

wf:IndustrialWastewaterFlow rdfs:subClassOf wf:WaterFlow ;
    rdfs:label "Industrial wastewater flow" ;
    rdfs:comment "Wastewater from industrial facilities" .
```

### 7.2 Optimum Limit Type

**IDENTIFIED IN USE CASE DATA** but **NOT IN ONTOLOGY:**

In `brewco.ttl` line 78:
```turtle
ghent:BrewCo_Water_pH a wf:WaterQualityRequirement ;
    wf:hasLimitType wf:OptimumLimit .  # ← This class exists in qualities.ttl line 202!
```

**Actually this DOES exist** - false alarm. It's defined in `qualities.ttl`.

---

## 8. Summary: Action Items for Ontology Enhancement

### High Priority

1. **Add quality-based water classification** (adopt WaWO+ approach)
   - File: `qualities.ttl`
   - Add `wf:WaterComposition` classes with threshold rules
   - Connect to flow types

2. **Add missing flow types**
   - File: `properties.ttl`
   - Add `wf:ProcessWaterFlow`, `wf:IndustrialWastewaterFlow`

3. **Harmonize water type classifications**
   - File: `envo_alignment.ttl`
   - Add explicit mappings between `wf:` flows and `envo:` materials
   - Document the distinction (material vs. flow classification)

### Medium Priority

4. **Add treatment train topology**
   - File: Use case data files
   - Connect process unit ports to show flow through treatment trains
   - Example: `WWTP1_Screening_Out wf:flowsTo WWTP1_GritRemoval_In`

5. **Strengthen ENVO facility alignments**
   - File: `envo_alignment.ttl`
   - Consider `owl:equivalentClass` or stronger subclass relations

### Low Priority (Future Work)

6. **Consider WaWO+ import for normative reasoning**
   - Currently referenced but not imported
   - Could add value for regulatory compliance checking

7. **Add PROV-O for provenance**
   - Currently commented out
   - Useful for tracking data sources and transformations

---

## 9. Recommendations for Use Case Data Revision

Given this analysis, when revising the Ghent case study data:

### DO:
✅ Use `wf:` prefix for all locally-defined waterFRAME classes
✅ Use `envo:` when referencing environmental features (biomes, water bodies)
✅ Use `sosa:` for sensor and observation infrastructure
✅ Define ports with `wf:hasInputPort` and `wf:hasOutputPort`
✅ Connect ports with `wf:flowsTo` to show topology
✅ Use quality parameter **classes** (`wf:BOD`) not strings
✅ Add QUDT units to all observations
✅ Link regulatory requirements to standards

### DON'T:
❌ Don't use `wawo:` prefix (WaWO+ not imported)
❌ Don't assume classes exist without checking the ontology files
❌ Don't use flow types that aren't defined (add them first if needed)
❌ Don't mix ENVO material types with waterFRAME flow classifications

### TUTORIAL APPROACH:
1. Start with **material entities** - define what physical things exist
2. Add **ports** - define connection points on components
3. Connect **ports** with `wf:flowsTo` - build the network topology
4. Add **water quality observations** - measure what's happening
5. Add **regulatory requirements** - define compliance standards
6. (Optional) Add **sampling metadata** - track how data was collected

---

## 10. References

- **BFO**: http://purl.obolibrary.org/obo/bfo.owl
- **ENVO**: http://purl.obolibrary.org/obo/envo.owl
- **SOSA**: http://www.w3.org/ns/sosa/
- **WaWO+ Evaluation**: `research/ontologies/WaWO/WaWO_Plus_Evaluation_Report.md`
- **OntoCAPE**: Marquardt et al. (2010) - Terminal/Port concept for process modeling

---

**End of Analysis**
