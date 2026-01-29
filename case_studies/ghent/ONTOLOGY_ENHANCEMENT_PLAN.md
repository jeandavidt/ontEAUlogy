# waterFRAME Ontology Enhancement Plan

**Author:** Planning Document for Ontology Refinement
**Date:** 2026-01-27
**Status:** Draft - Awaiting Approval
**Version:** 1.1

---

## Executive Summary

This document outlines a comprehensive plan to enhance the waterFRAME ontology based on the findings from the ONTOLOGY_CLASS_ORIGINS_ANALYSIS. The plan addresses:

1. ✅ Quality-based water classification (WaWO+ approach) with jurisdictional awareness
2. ✅ Process water flow types (with industry variability)
3. ✅ Water type harmonization (waterFRAME ↔ ENVO)
4. ✅ ENVO facility alignment decisions
5. ✅ WaWO-to-waterFRAME mapping strategy
6. ✅ Scenario modeling integration (J-Park/OntoCAPE concepts) with proper time ontology
7. ✅ Systematic rdfs:seeAlso references for ALL bridged ontologies (WaWO+, OntoCAPE, etc.)
8. ✅ PROV-O integration for provenance tracking

**IMPORTANT:** This is a PLANNING document. No ontology changes will be made until this plan is approved.

---

## Part 1: Research Findings

### 1.1 Scenario/Alternate Universe Modeling

#### Background: J-Park Simulator (Markus Kraft et al.)

**Source:** Zhou et al. (2019) - "An agent composition framework for the J-Park Simulator"

**Key Concepts from OntoAgent/J-Park:**

The J-Park Simulator framework includes scenario modeling for process simulation:

```turtle
# Scenario types (from OntoAgent EXTENSION_DESIGN.md)
ontosim:SimulationScenario a owl:Class ;
    rdfs:subClassOf ontoagent:TaskSpecification .

ontosim:HistoricalScenario a owl:Class ;
    rdfs:subClassOf ontosim:SimulationScenario ;
    rdfs:comment "Simulation based on historical data" .

ontosim:ProspectiveScenario a owl:Class ;
    rdfs:subClassOf ontosim:SimulationScenario ;
    rdfs:comment "Future-looking 'what-if' scenario" .

ontosim:AlternateScenario a owl:Class ;
    rdfs:subClassOf ontosim:SimulationScenario ;
    rdfs:comment "Alternative configuration or operating condition" .

# Scenario properties
ontosim:hasPurpose a owl:ObjectProperty ;
    rdfs:domain ontosim:SimulationScenario ;
    rdfs:range [owl:oneOf (ontosim:Calibration
                          ontosim:Optimization
                          ontosim:Computation)] .

ontosim:hasInitialCondition a owl:ObjectProperty ;
    rdfs:domain ontosim:SimulationScenario ;
    rdfs:range ontosim:Parameter .

ontosim:timePeriod a owl:DatatypeProperty ;
    rdfs:domain ontosim:SimulationScenario ;
    rdfs:range xsd:duration .
```

#### OntoCAPE Model Consistency Notes

**Finding:** OntoCAPE has logical inconsistencies (see [research/ontologies/ontoCAPE/FINDINGS.md](research/ontologies/ontoCAPE/FINDINGS.md))
- Cannot be directly imported due to transitivity+cardinality conflicts
- Scenario modeling patterns may exist but need extraction, not direct import

#### Application to waterFRAME

**Use Case:** Ghent case study needs to represent:
- **Baseline scenario** - Current state of the water system
- **Optimization scenarios** - "What if we add MBR?" "What if we increase capacity?"
- **Historical scenarios** - Past configurations for comparison
- **Regulatory scenarios** - Meeting different discharge standards

**Recommendation:** Adopt lightweight scenario framework inspired by J-Park but adapted for water systems.

---

### 1.2 ENVO Facility Class Definitions

#### ENVO:00002043 - Wastewater Treatment Plant

```obo
id: ENVO:00002043
name: wastewater treatment plant
xref: EcoLexicon:wastewater_treatment_plant
xref: https://en.wikipedia.org/wiki/Wastewater_treatment_plant
is_a: ENVO:00002272 ! waste treatment plant
```

**Note:** No formal definition provided, only cross-references.
**Parent Class:** ENVO:00002272 (waste treatment plant)

#### ENVO:01001886 - Drinking Water Treatment Plant

```obo
id: ENVO:01001886
name: drinking water treatment plant
def: "An industrial building in which water undergoes a
      purification process to make it fit for human consumption."
is_a: ENVO:00003861 ! industrial building
```

**Parent Class:** ENVO:00003861 (industrial building)
**Status:** Has formal definition

#### waterFRAME Current Definitions

```turtle
wf:DrinkingWaterPlant rdfs:subClassOf bfo:BFO_0000040 ;
    rdfs:label "Drinking water plant" ;
    rdfs:comment "A facility that treats source water to produce potable water." .

wf:WastewaterTreatmentPlant rdfs:subClassOf bfo:BFO_0000040 ;
    rdfs:label "Wastewater treatment plant" ;
    rdfs:comment "A facility that treats wastewater to produce effluent meeting discharge standards." .
```

#### Current Alignment (from envo_alignment.ttl)

```turtle
wf:WastewaterTreatmentPlant rdfs:subClassOf wf:WaterSystemComponent ;
    rdfs:comment "Aligned with ENVO:00002043" ;
    rdfs:seeAlso envo:00002043 .

wf:DrinkingWaterTreatmentPlant rdfs:subClassOf wf:WaterSystemComponent ;
    rdfs:comment "Aligned with ENVO:01001886" ;
    rdfs:seeAlso envo:01001886 .
```

#### DECISION: Keep rdfs:seeAlso Approach ✅

**Rationale:**
- waterFRAME models engineering infrastructure; ENVO models environmental features
- waterFRAME's WWTP includes ports, process units, control systems (not in ENVO)
- ENVO's WWTP focuses on environmental/spatial aspects (not needed in waterFRAME)
- Bridge pattern maintains flexibility without import dependencies

---

## Part 2: WaWO-to-waterFRAME Mapping Strategy

### 2.1 Fundamental Modeling Difference

#### WaWO+ Approach: Process-Oriented

```turtle
# WaWO+ focuses on PROCESSES and their relationships
wawo:WastewaterTreatment a owl:Class .
wawo:SecondaryTreatment rdfs:subClassOf wawo:WastewaterTreatment .
wawo:Disinfection rdfs:subClassOf wawo:WastewaterTreatment .

# Processes are connected by flow relationships
wawo:produces a owl:ObjectProperty .
wawo:receives a owl:ObjectProperty .
```

**Characteristics:**
- Models the ACTIVITY (treatment process)
- Flow-based topology (X produces Y which receives Z)
- Quality parameters as data properties (BOD, COD as attributes)
- Suitable for regulatory compliance and quality tracking

#### waterFRAME Approach: Infrastructure-Oriented

```turtle
# waterFRAME focuses on PHYSICAL UNITS and their topology
wf:AerationTank rdfs:subClassOf wf:SecondaryTreatment .
wf:SecondarySettler rdfs:subClassOf wf:SecondaryTreatment .

# Units connected via ports
wf:hasInputPort a owl:ObjectProperty .
wf:hasOutputPort a owl:ObjectProperty .
wf:flowsTo a owl:ObjectProperty .
```

**Characteristics:**
- Models the EQUIPMENT (physical tank, unit, infrastructure)
- Port-based topology (Unit1.out → Unit2.in)
- Quality parameters as classes (wf:BOD is an ObservableProperty)
- Suitable for system design and operational modeling

### 2.2 Mapping Strategy: Complementary Perspectives

**Key Insight:** These are NOT competing models - they're complementary views!

```
Physical Infrastructure (waterFRAME)    Process Activity (WaWO+)
=====================================    ========================
wf:AerationTank                    ←→   wawo:BiologicalOxidation
  - has physical properties              - has process parameters
  - has ports (in/out)                   - has inputs/outputs (materials)
  - has capacity (m³)                    - has kinetic rates
  - located in space                     - occurs in time
```

### 2.3 Proposed Integration Approach

#### Strategy: "Process Realizes Physical Unit"

```turtle
# New property to link infrastructure to processes
wf:realizes a owl:ObjectProperty ;
    rdfs:label "realizes" ;
    rdfs:comment "Links a physical unit to the process it enables" ;
    rdfs:domain wf:WaterSystemComponent ;
    rdfs:range wf:TreatmentProcess .

# Example usage
ex:Ghent_AerationTank_1 a wf:AerationTank ;
    wf:hasInputPort ex:Ghent_AT1_In ;
    wf:hasOutputPort ex:Ghent_AT1_Out ;
    wf:hasVolume "1000"^^xsd:double ;
    qudt:unit unit:M3 ;
    wf:realizes ex:Ghent_BiologicalOxidation_Process .

ex:Ghent_BiologicalOxidation_Process a wf:BiologicalOxidationProcess ;
    rdfs:comment "Inspired by wawo:BiologicalOxidation" ;
    wf:hasKineticParameter ex:MaxGrowthRate ;
    wf:operatingTemperature "20"^^xsd:double .
```

### 2.4 Systematic rdfs:seeAlso References

**CRITICAL REQUIREMENT:** Add `rdfs:seeAlso` for ALL classes inspired by external ontologies

This applies to:
1. **WaWO+** - Process units and water quality concepts
2. **OntoCAPE** - Port/Terminal concept
3. **ENVO** - Environmental features and water bodies
4. **SOSA** - Already done via rdfs:subClassOf

```turtle
# In material_entities.ttl

# WaWO+ inspired classes
wf:Screening rdfs:subClassOf wf:PrimaryTreatment ;
    rdfs:label "Screening" ;
    rdfs:comment "Physical unit for removing large solids" ;
    rdfs:seeAlso <http://www.semanticweb.org/wawo/Screening> ;
    rdfs:comment "Inspired by WaWO+ Screening process concept" .

wf:AerationTank rdfs:subClassOf wf:SecondaryTreatment ;
    rdfs:label "Aeration tank" ;
    rdfs:comment "Tank providing oxygen for biological treatment" ;
    rdfs:seeAlso <http://www.semanticweb.org/wawo/BiologicalOxidation> ;
    rdfs:comment "Physical infrastructure for WaWO+ BiologicalOxidation process" .

wf:SecondarySettler rdfs:subClassOf wf:SecondaryTreatment ;
    rdfs:label "Secondary settler" ;
    rdfs:comment "Clarification tank for biomass separation" ;
    rdfs:seeAlso <http://www.semanticweb.org/wawo/Clarification> ;
    rdfs:comment "Infrastructure for WaWO+ Clarification process" .

wf:DisinfectionUnit rdfs:subClassOf wf:TertiaryTreatment ;
    rdfs:label "Disinfection unit" ;
    rdfs:comment "Unit for pathogen inactivation" ;
    rdfs:seeAlso <http://www.semanticweb.org/wawo/Disinfection> ;
    rdfs:comment "Physical unit for WaWO+ Disinfection process" .

wf:NitrificationTank rdfs:subClassOf wf:TertiaryTreatment ;
    rdfs:label "Nitrification tank" ;
    rdfs:comment "Tank for ammonia oxidation to nitrate" ;
    rdfs:seeAlso <http://www.semanticweb.org/wawo/Nitrification> ;
    rdfs:comment "Infrastructure for WaWO+ Nitrification process" .

wf:DenitrificationTank rdfs:subClassOf wf:TertiaryTreatment ;
    rdfs:label "Denitrification tank" ;
    rdfs:comment "Tank for nitrate reduction to nitrogen gas" ;
    rdfs:seeAlso <http://www.semanticweb.org/wawo/Denitrification> ;
    rdfs:comment "Infrastructure for WaWO+ Denitrification process" .

wf:PhosphorusRemovalTank rdfs:subClassOf wf:TertiaryTreatment ;
    rdfs:label "Phosphorus removal tank" ;
    rdfs:comment "Tank for chemical or biological phosphorus removal" ;
    rdfs:seeAlso <http://www.semanticweb.org/wawo/PhosphorusRemoval> ;
    rdfs:comment "Infrastructure for WaWO+ PhosphorusRemoval process" .

wf:GritRemoval rdfs:subClassOf wf:PrimaryTreatment ;
    rdfs:label "Grit removal" ;
    rdfs:comment "Unit for removing heavy inorganic particles" ;
    rdfs:seeAlso <http://www.semanticweb.org/wawo/GritRemoval> ;
    rdfs:comment "Physical unit for WaWO+ GritRemoval process" .

wf:PrimarySettler rdfs:subClassOf wf:PrimaryTreatment ;
    rdfs:label "Primary settler" ;
    rdfs:comment "Sedimentation tank for primary clarification" ;
    rdfs:seeAlso <http://www.semanticweb.org/wawo/PrimaryClarification> ;
    rdfs:comment "Infrastructure for WaWO+ PrimaryClarification process" .

wf:MembraneBioreactor rdfs:subClassOf wf:SecondaryTreatment ;
    rdfs:label "Membrane bioreactor" ;
    rdfs:comment "Combined biological treatment and membrane filtration" ;
    rdfs:seeAlso <http://www.semanticweb.org/wawo/MembraneFiltration> ;
    rdfs:comment "Physical unit combining biological treatment with membrane separation" .

wf:ReverseOsmosisUnit rdfs:subClassOf wf:TreatmentUnit ;
    rdfs:label "Reverse osmosis unit" ;
    rdfs:comment "Membrane unit for high-level water purification" ;
    rdfs:seeAlso <http://www.semanticweb.org/wawo/ReverseOsmosis> ;
    rdfs:comment "Physical unit for WaWO+ ReverseOsmosis process" .

# OntoCAPE inspired classes
wf:Port a owl:Class ;
    rdfs:label "Port" ;
    rdfs:comment "Connection point on a water system component for input or output" ;
    rdfs:seeAlso <http://www.theworldavatar.com/ontology/ontocape/chemical_process_system/CPS_realization/plant.owl#Terminal> ;
    rdfs:comment "Inspired by OntoCAPE Terminal concept (Marquardt et al. 2010)" .

wf:InputPort rdfs:subClassOf wf:Port ;
    rdfs:seeAlso <http://www.theworldavatar.com/ontology/ontocape/chemical_process_system/CPS_realization/plant.owl#Terminal> .

wf:OutputPort rdfs:subClassOf wf:Port ;
    rdfs:seeAlso <http://www.theworldavatar.com/ontology/ontocape/chemical_process_system/CPS_realization/plant.owl#Terminal> .
```

**Note:** Since WaWO+ may have license restrictions and is an abandoned project, we:
1. Do NOT import WaWO+ ontology
2. DO reference WaWO+ concepts as inspiration via rdfs:seeAlso
3. DO define our own classes in waterFRAME namespace
4. Document the conceptual relationship but maintain independence

---

## Part 3: Quality-Based Water Classification with Jurisdictional Awareness

### 3.1 Challenge: Quality Thresholds Vary by Jurisdiction

**CRITICAL INSIGHT:** The same water quality can be classified differently depending on jurisdiction!

Examples:
- EU Drinking Water Directive: BOD ≤ 5 mg/L
- WHO Guidelines: BOD ≤ 3 mg/L
- US EPA: Different parameters emphasized (MCLs for specific contaminants)
- Local regulations: May be more or less stringent

**Solution:** Water composition classes must be linked to regulatory frameworks and jurisdictions.

### 3.2 Proposed Design: Jurisdiction-Aware Classification

```turtle
# Add to qualities.ttl

@prefix gn: <http://www.geonames.org/ontology#> .

# ========== WATER COMPOSITION CLASSIFICATION ==========

wf:WaterComposition a owl:Class ;
    rdfs:label "Water composition" ;
    rdfs:comment """Classification of water based on quality characteristics.

    IMPORTANT: Quality thresholds are JURISDICTION-DEPENDENT. The same measured values
    may be classified as 'drinking water' in one regulatory framework but not another.""" ;
    rdfs:subClassOf bfo:BFO_0000019 .  # quality

# Regulatory Framework class
wf:RegulatoryFramework a owl:Class ;
    rdfs:label "Regulatory framework" ;
    rdfs:comment "A set of water quality regulations, standards, or guidelines from a specific authority" .

wf:appliesInJurisdiction a owl:ObjectProperty ;
    rdfs:label "applies in jurisdiction" ;
    rdfs:comment "Links a regulatory framework to the geographic jurisdiction where it applies" ;
    rdfs:domain wf:RegulatoryFramework ;
    rdfs:range gn:Feature .  # GeoNames location

wf:definingFramework a owl:ObjectProperty ;
    rdfs:label "defining framework" ;
    rdfs:comment "Links a water composition classification to the regulatory framework that defines its thresholds" ;
    rdfs:domain wf:WaterComposition ;
    rdfs:range wf:RegulatoryFramework .

# Generic composition classes (framework-independent)
wf:DrinkingWaterQuality rdfs:subClassOf wf:WaterComposition ;
    rdfs:label "Drinking water quality" ;
    rdfs:comment """Water meeting drinking water standards.

    Specific thresholds depend on regulatory framework. Common parameters:
    - BOD (typically ≤ 3-5 mg/L)
    - COD (typically ≤ 10-20 mg/L)
    - TSS (typically ≤ 5-10 mg/L)
    - TN (typically ≤ 1-2 mg/L)
    - TP (typically ≤ 0.1-0.5 mg/L)
    - Microbiological parameters (E. coli, coliforms)

    Always check definingFramework to know which specific thresholds apply.""" ;
    rdfs:seeAlso <http://www.semanticweb.org/wawo/DrinkingWaterComposition> ;
    rdfs:comment "Concept inspired by WaWO+ DrinkingWaterComposition" .

wf:WastewaterQuality rdfs:subClassOf wf:WaterComposition ;
    rdfs:label "Wastewater quality" ;
    rdfs:comment """Water with untreated wastewater characteristics.

    Typical raw sewage (framework-independent indicators):
    - BOD > 200-400 mg/L
    - COD > 400-800 mg/L
    - TSS > 200-400 mg/L

    Discharge limits for treated wastewater are jurisdiction-specific.""" ;
    rdfs:seeAlso <http://www.semanticweb.org/wawo/WastewaterComposition> ;
    rdfs:comment "Concept inspired by WaWO+ WastewaterComposition" .

wf:ReclaimedWaterQuality rdfs:subClassOf wf:WaterComposition ;
    rdfs:label "Reclaimed water quality" ;
    rdfs:comment """Treated water suitable for non-potable reuse.

    Quality depends on intended use AND jurisdiction:
    - Irrigation: Different crops have different tolerance
    - Industrial cooling: Varies by process
    - Urban non-potable: Toilet flushing, landscaping

    EU Regulation 2020/741 defines classes A, B, C, D for different uses.
    US EPA Guidelines distinguish urban, industrial, agricultural reuse.""" .

wf:GreywaterQuality rdfs:subClassOf wf:WaterComposition ;
    rdfs:label "Greywater quality" ;
    rdfs:comment """Lightly contaminated water from domestic sources (excluding toilet).

    Characteristics (generally consistent across jurisdictions):
    - BOD: 100-200 mg/L
    - COD: 200-500 mg/L
    - Lower pathogen load than blackwater

    Reuse regulations vary widely by jurisdiction.""" .

wf:BlackwaterQuality rdfs:subClassOf wf:WaterComposition ;
    rdfs:label "Blackwater quality" ;
    rdfs:comment """Toilet wastewater with high contamination.

    Characteristics (generally consistent):
    - BOD: 300-400 mg/L
    - COD: 500-800 mg/L
    - High pathogen and nutrient content""" .

# Link composition to water entities
wf:hasWaterComposition a owl:ObjectProperty ;
    rdfs:label "has water composition" ;
    rdfs:comment "Links a water sample or port to its quality-based composition class" ;
    rdfs:domain [owl:unionOf (wf:WaterSample wf:Port)] ;
    rdfs:range wf:WaterComposition .

# Example framework instances
ex:EU_WaterFrameworkDirective a wf:RegulatoryFramework ;
    rdfs:label "EU Water Framework Directive" ;
    wf:appliesInJurisdiction gn:6695072 ;  # European Union
    rdfs:seeAlso <https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02000L0060> .

ex:WHO_DrinkingWaterGuidelines a wf:RegulatoryFramework ;
    rdfs:label "WHO Guidelines for Drinking-water Quality" ;
    rdfs:comment "Global guidelines, often adapted by countries" ;
    rdfs:seeAlso <https://www.who.int/publications/i/item/9789240045064> .

ex:EU_WaterReuseRegulation a wf:RegulatoryFramework ;
    rdfs:label "EU Water Reuse Regulation 2020/741" ;
    wf:appliesInJurisdiction gn:6695072 ;  # European Union
    rdfs:seeAlso <https://eur-lex.europa.eu/eli/reg/2020/741> .
```

### 3.3 Example Usage with Jurisdiction

```turtle
# Sample classified under EU framework
ex:Ghent_WWTP_Effluent_Sample_001 a wf:WaterSample ;
    wf:hasWaterComposition ex:Ghent_Effluent_Composition .

ex:Ghent_Effluent_Composition a wf:ReclaimedWaterQuality ;
    wf:definingFramework ex:EU_WaterReuseRegulation ;
    rdfs:comment "Classified as Class A reclaimed water under EU Regulation 2020/741" ;
    wf:meetsRequirementClass ex:EU_ReclaimedWater_ClassA .

# The same water might be classified differently under different framework
ex:Ghent_Effluent_Composition_US a wf:ReclaimedWaterQuality ;
    wf:definingFramework ex:US_EPA_ReuseGuidelines ;
    rdfs:comment "Under US EPA guidelines, would be 'unrestricted urban reuse' quality" .
```

### 3.4 Link to Regulatory Requirements

```turtle
# Extend WaterQualityRequirement to be framework-specific
wf:WaterQualityRequirement rdfs:subClassOf wf:RegulatoryFramework .

wf:definesComposition a owl:ObjectProperty ;
    rdfs:label "defines composition" ;
    rdfs:comment "Links a regulatory requirement to the water composition class it defines" ;
    rdfs:domain wf:WaterQualityRequirement ;
    rdfs:range wf:WaterComposition .

# Example: EU drinking water regulation DEFINES what counts as drinking water quality
ex:EU_DrinkingWater_BOD_Limit a wf:WaterQualityRequirement ;
    wf:hasWaterQualityParameter wf:BOD ;
    wf:hasLimitValue "5.0"^^xsd:double ;
    wf:hasLimitType wf:MaximumLimit ;
    wf:appliesInJurisdiction gn:6695072 ;  # EU
    rdfs:subClassOf ex:EU_WaterFrameworkDirective ;
    wf:definesComposition wf:DrinkingWaterQuality .
```

---

## Part 4: Process Water Flow Type

### 4.1 Challenge: Industry-Specific Definitions

**Issue:** "Process water" means different things in different industries:

- **Brewery:** Water used in mashing, lautering, boiling (high-quality needed)
- **Textile:** Water for dyeing, washing fabrics (contaminated with dyes/chemicals)
- **Electronics:** Ultra-pure water for chip manufacturing (deionized)
- **Food processing:** Water contacting food products (must meet food safety standards)

**Cannot use a single quality threshold like drinking water or wastewater!**

### 4.2 Solution: Industry-Contextualized Flow Type

```turtle
# Add to properties.ttl

wf:ProcessWaterFlow rdfs:subClassOf wf:WaterFlow ;
    rdfs:label "Process water flow" ;
    rdfs:comment """Water used in industrial manufacturing processes.

    Quality requirements are INDUSTRY-SPECIFIC and must be defined per facility type.
    This is a general classification - specific quality is determined by the industrial process.""" .

wf:IndustrialWastewaterFlow rdfs:subClassOf wf:WaterFlow ;
    rdfs:label "Industrial wastewater flow" ;
    rdfs:comment """Wastewater from industrial processes.

    Characteristics vary by industry:
    - Brewery: high BOD/COD, organic matter
    - Textile: dyes, chemicals, variable pH
    - Electronics: low contaminants but high volume
    - Food processing: organic load, fats/oils/grease""" .

# Link flow type to facility type for context
wf:fromFacilityType a owl:ObjectProperty ;
    rdfs:label "from facility type" ;
    rdfs:comment "Indicates which type of industrial facility produced this water flow" ;
    rdfs:domain wf:ProcessWaterFlow ;
    rdfs:range wf:IndustrialFacility .

# Example usage
ex:BrewCo_ProcessWater_Out a wf:OutputPort ;
    wf:hasFlowType ex:BrewCo_ProcessWater .

ex:BrewCo_ProcessWater a wf:ProcessWaterFlow ;
    wf:fromFacilityType wf:Brewery ;
    rdfs:comment "Process water from brewery - contains sugars, yeast, organic matter" ;
    wf:hasWaterComposition ex:BrewCo_ProcessWater_Composition .

ex:BrewCo_ProcessWater_Composition a wf:WaterComposition ;
    # Custom composition, not matching standard classes
    rdfs:comment "Brewery process water composition - not drinking water, not typical wastewater" .
```

---

## Part 5: Water Type Harmonization (waterFRAME ↔ ENVO)

### 5.1 Current Situation

**waterFRAME Flow Types:**
```turtle
wf:GreywaterFlow rdfs:subClassOf wf:WaterFlow .
wf:BlackwaterFlow rdfs:subClassOf wf:WaterFlow .
wf:PotableWaterFlow rdfs:subClassOf wf:WaterFlow .
wf:ReclaimedWaterFlow rdfs:subClassOf wf:WaterFlow .
wf:RainwaterFlow rdfs:subClassOf wf:WaterFlow .
```

**ENVO Water Material Types:**
```turtle
envo:00002006 - water (material entity)
├── envo:00002018 - sewage
├── envo:00003097 - drinking water
├── envo:00002042 - surface water
├── envo:00002001 - groundwater
├── envo:00002223 - grey water
└── envo:00002044 - wastewater
```

### 5.2 Harmonization Strategy

**Principle:** Use BOTH - they serve different purposes!
- **ENVO classes:** What the water IS (material composition, environmental context)
- **waterFRAME flow types:** How water is CLASSIFIED in the engineered system

### 5.3 Explicit Mappings with rdfs:seeAlso

```turtle
# Add to envo_alignment.ttl

# ========== WATER FLOW TO ENVO MATERIAL MAPPINGS ==========

# All flow types reference their ENVO material counterparts
wf:PotableWaterFlow rdfs:seeAlso envo:00003097 ;  # drinking water
    rdfs:comment "Flow classification for drinking water material (envo:00003097)" .

wf:BlackwaterFlow rdfs:seeAlso envo:00002018 ;  # sewage
    rdfs:comment "Flow classification for sewage material (envo:00002018)" .

wf:GreywaterFlow rdfs:seeAlso envo:00002223 ;  # grey water
    rdfs:comment "Flow classification for grey water material (envo:00002223)" .

wf:ReclaimedWaterFlow rdfs:seeAlso envo:00002044 ;  # wastewater (treated)
    rdfs:comment "Flow classification for treated wastewater material (envo:00002044)" .

wf:RainwaterFlow rdfs:seeAlso <http://purl.obolibrary.org/obo/ENVO_01001564> ;  # rain
    rdfs:comment "Rainwater collected from precipitation (envo:01001564)" .

# Formal relationship via restrictions (for reasoning)
wf:PotableWaterFlow owl:equivalentClass [
    a owl:Restriction ;
    owl:onProperty wf:containsWaterType ;
    owl:someValuesFrom envo:00003097  # drinking water
] .

wf:BlackwaterFlow owl:equivalentClass [
    a owl:Restriction ;
    owl:onProperty wf:containsWaterType ;
    owl:someValuesFrom envo:00002018  # sewage
] .

wf:GreywaterFlow owl:equivalentClass [
    a owl:Restriction ;
    owl:onProperty wf:containsWaterType ;
    owl:someValuesFrom envo:00002223  # grey water
] .

wf:ReclaimedWaterFlow rdfs:subClassOf [
    a owl:Restriction ;
    owl:onProperty wf:containsWaterType ;
    owl:someValuesFrom envo:00002044  # wastewater (treated)
] .

# New property to link flows to material types
wf:containsWaterType a owl:ObjectProperty ;
    rdfs:label "contains water type" ;
    rdfs:comment "Links a water flow to the ENVO water material type it contains" ;
    rdfs:domain wf:WaterFlow ;
    rdfs:range envo:00002006 .  # water (material entity)
```

### 5.4 Documentation Clarification

```turtle
# Add clear documentation in envo_alignment.ttl

# ========== MODELING DISTINCTION: FLOW vs MATERIAL ==========

# waterFRAME Flow Types (Engineering Classification)
# - Purpose: Classify water in engineered systems by SOURCE/USE
# - Examples: "This pipe carries greywater" "This tank stores potable water"
# - Domain: Water infrastructure, system design
# - Reasoning: What role does this water play in the system?

# ENVO Material Types (Environmental/Chemical Classification)
# - Purpose: Classify water by ENVIRONMENTAL CONTEXT and COMPOSITION
# - Examples: "This is surface water" "This is drinking water (material)"
# - Domain: Environmental science, ecology
# - Reasoning: What IS this water from an environmental perspective?

# Both Are Needed:
# - A port might carry "GreywaterFlow" (engineering) containing "grey water" (material)
# - A treatment plant processes "WastewaterFlow" containing "sewage" (material)
# - The flow type tells you the system role; material type tells you composition
```

---

## Part 6: Scenario Modeling Integration with OWL-Time

### 6.1 Requirements for Ghent Case Study

**Needed Capabilities:**
1. Define baseline configuration (current system state)
2. Model alternative configurations ("what if we add component X?")
3. Compare scenarios (cost, efficiency, compliance)
4. Track scenario metadata (purpose, assumptions, time period)
5. **Use proper temporal representation (OWL-Time)**

### 6.2 OWL-Time Integration

**W3C Time Ontology:** https://www.w3.org/TR/owl-time/

```turtle
@prefix time: <http://www.w3.org/2006/time#> .

# Key time classes:
time:Instant - A point in time
time:Interval - A period with start and end
time:TemporalEntity - Abstract superclass
```

### 6.3 Proposed Scenario Module

```turtle
# Create new file: data/ontology/modules/scenarios.ttl

@prefix wf: <http://example.org/waterframe#> .
@prefix bfo: <http://purl.obolibrary.org/obo/BFO_> .
@prefix time: <http://www.w3.org/2006/time#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# ========== SCENARIO FRAMEWORK ==========
# Inspired by J-Park Simulator (Zhou et al. 2019) and OntoCAPE
# Adapted for water system modeling

wf:Scenario a owl:Class ;
    rdfs:label "Scenario" ;
    rdfs:comment """A defined configuration of a water system representing a specific state,
    time period, or hypothetical alternative. Scenarios enable comparison of different system designs,
    operating conditions, or regulatory requirements.""" ;
    rdfs:subClassOf bfo:BFO_0000031 .  # generically dependent continuant

wf:BaselineScenario rdfs:subClassOf wf:Scenario ;
    rdfs:label "Baseline scenario" ;
    rdfs:comment """The current or reference state of the water system.
    All alternative scenarios are compared against the baseline.""" .

wf:AlternativeScenario rdfs:subClassOf wf:Scenario ;
    rdfs:label "Alternative scenario" ;
    rdfs:comment """A hypothetical configuration differing from the baseline.
    Examples: Adding new treatment units, changing operating parameters, meeting new regulations.""" .

wf:HistoricalScenario rdfs:subClassOf wf:Scenario ;
    rdfs:label "Historical scenario" ;
    rdfs:comment """A scenario representing a past state of the system.
    Used for calibration, validation, or trend analysis.""" .

wf:OptimizationScenario rdfs:subClassOf wf:AlternativeScenario ;
    rdfs:label "Optimization scenario" ;
    rdfs:comment """A scenario generated through optimization to maximize/minimize objectives.
    Example: Minimizing energy consumption while meeting discharge standards.""" .

# ========== SCENARIO PROPERTIES ==========

wf:scenarioName a owl:DatatypeProperty ;
    rdfs:label "scenario name" ;
    rdfs:domain wf:Scenario ;
    rdfs:range xsd:string .

wf:scenarioPurpose a owl:DatatypeProperty ;
    rdfs:label "scenario purpose" ;
    rdfs:comment "Describes why this scenario exists and what question it answers" ;
    rdfs:domain wf:Scenario ;
    rdfs:range xsd:string .

wf:scenarioDescription a owl:DatatypeProperty ;
    rdfs:label "scenario description" ;
    rdfs:domain wf:Scenario ;
    rdfs:range xsd:string .

# Use OWL-Time for temporal representation
wf:hasTemporalExtent a owl:ObjectProperty ;
    rdfs:label "has temporal extent" ;
    rdfs:comment "Links a scenario to its time period using OWL-Time" ;
    rdfs:domain wf:Scenario ;
    rdfs:range time:TemporalEntity .

wf:scenarioCreationDate a owl:DatatypeProperty ;
    rdfs:label "scenario creation date" ;
    rdfs:domain wf:Scenario ;
    rdfs:range xsd:dateTime .

wf:baselineFor a owl:ObjectProperty ;
    rdfs:label "baseline for" ;
    rdfs:comment "Links a baseline scenario to alternative scenarios compared against it" ;
    rdfs:domain wf:BaselineScenario ;
    rdfs:range wf:AlternativeScenario .

wf:alternativeTo a owl:ObjectProperty ;
    rdfs:label "alternative to" ;
    rdfs:comment "Links an alternative scenario to its baseline" ;
    rdfs:domain wf:AlternativeScenario ;
    rdfs:range wf:BaselineScenario ;
    owl:inverseOf wf:baselineFor .

# ========== SCENARIO MEMBERSHIP ==========

wf:inScenario a owl:ObjectProperty ;
    rdfs:label "in scenario" ;
    rdfs:comment "Indicates that an entity exists or is active in a particular scenario" ;
    rdfs:range wf:Scenario .

wf:scenarioComponent a owl:ObjectProperty ;
    rdfs:label "scenario component" ;
    rdfs:comment "Links a scenario to the water system components that exist in it" ;
    rdfs:domain wf:Scenario ;
    rdfs:range wf:WaterSystemComponent .

wf:scenarioParameter a owl:ObjectProperty ;
    rdfs:label "scenario parameter" ;
    rdfs:comment "Links a scenario to specific parameter values (flow rates, quality limits, etc.)" ;
    rdfs:domain wf:Scenario .

# ========== SCENARIO COMPARISON ==========

wf:ScenarioComparison a owl:Class ;
    rdfs:label "Scenario comparison" ;
    rdfs:comment "Represents a comparison between two or more scenarios" .

wf:comparesScenarios a owl:ObjectProperty ;
    rdfs:label "compares scenarios" ;
    rdfs:domain wf:ScenarioComparison ;
    rdfs:range wf:Scenario .

wf:comparisonCriterion a owl:DatatypeProperty ;
    rdfs:label "comparison criterion" ;
    rdfs:comment "The metric used to compare scenarios (e.g., cost, energy, compliance)" ;
    rdfs:domain wf:ScenarioComparison ;
    rdfs:range xsd:string .

# ========== FUTURE EXPANSION HOOKS ==========
# These classes are defined but not fully implemented in Phase 1
# They indicate future capabilities that will be needed

wf:OptimizationObjective a owl:Class ;
    rdfs:label "Optimization objective" ;
    rdfs:comment """Objective function for scenario optimization.

    FUTURE: Will be expanded to include target parameters, weights, constraints.
    Inspired by OntoAgent optimization framework.""" ;
    rdfs:seeAlso <http://www.theworldavatar.com/ontology/ontoagent/OntoAgent.owl#OptimizationObjective> .

wf:ScenarioConstraint a owl:Class ;
    rdfs:label "Scenario constraint" ;
    rdfs:comment """Constraint on scenario variables (regulatory, physical, economic).

    FUTURE: Will include constraint types, bounds, relationships.""" .

wf:SimulationParameter a owl:Class ;
    rdfs:label "Simulation parameter" ;
    rdfs:comment """Parameters for scenario simulation (solver config, time steps, etc.).

    FUTURE: Will support numerical solver configuration, computational resources.""" .

# Placeholder properties for future development
wf:hasObjective a owl:ObjectProperty ;
    rdfs:label "has objective" ;
    rdfs:comment "FUTURE: Links optimization scenario to objectives" ;
    rdfs:domain wf:OptimizationScenario ;
    rdfs:range wf:OptimizationObjective .

wf:hasConstraint a owl:ObjectProperty ;
    rdfs:label "has constraint" ;
    rdfs:comment "FUTURE: Links scenario to constraints" ;
    rdfs:domain wf:Scenario ;
    rdfs:range wf:ScenarioConstraint .
```

### 6.4 Example Usage with OWL-Time

```turtle
# Import OWL-Time
owl:imports <http://www.w3.org/2006/time#> .

# Baseline: Current Ghent water system (using OWL-Time Interval)
ghent:BaselineScenario_2026 a wf:BaselineScenario ;
    wf:scenarioName "Ghent Baseline 2026" ;
    wf:scenarioPurpose "Current state of Ghent water infrastructure" ;
    wf:hasTemporalExtent ghent:Year2026 ;
    wf:scenarioCreationDate "2026-01-27T14:00:00Z"^^xsd:dateTime ;
    wf:scenarioComponent ghent:AquaFin_WWTP ;
    wf:scenarioComponent ghent:BrewCo_Facility .

# Temporal extent using OWL-Time
ghent:Year2026 a time:Interval ;
    time:hasBeginning ghent:Start2026 ;
    time:hasEnd ghent:End2026 .

ghent:Start2026 a time:Instant ;
    time:inXSDDateTimeStamp "2026-01-01T00:00:00Z"^^xsd:dateTimeStamp .

ghent:End2026 a time:Instant ;
    time:inXSDDateTimeStamp "2026-12-31T23:59:59Z"^^xsd:dateTimeStamp .

# Alternative: Add MBR to brewery
ghent:MBR_Alternative a wf:AlternativeScenario ;
    wf:scenarioName "BrewCo MBR Addition" ;
    wf:scenarioPurpose "Evaluate impact of adding MBR for greywater reuse" ;
    wf:alternativeTo ghent:BaselineScenario_2026 ;
    wf:hasTemporalExtent ghent:FutureProjection2027 ;
    wf:scenarioComponent ghent:AquaFin_WWTP ;
    wf:scenarioComponent ghent:BrewCo_Facility ;
    wf:scenarioComponent ghent:BrewCo_New_MBR .  # New component in this scenario

ghent:FutureProjection2027 a time:Interval ;
    time:hasBeginning [ a time:Instant ; time:inXSDDateTimeStamp "2027-01-01T00:00:00Z"^^xsd:dateTimeStamp ] ;
    time:hasEnd [ a time:Instant ; time:inXSDDateTimeStamp "2027-12-31T23:59:59Z"^^xsd:dateTimeStamp ] .

ghent:BrewCo_New_MBR a wf:MembraneBioreactorUnit ;
    wf:inScenario ghent:MBR_Alternative ;
    rdfs:comment "This MBR only exists in the alternative scenario" .

# Historical scenario example
ghent:Historical2020 a wf:HistoricalScenario ;
    wf:scenarioName "Ghent System 2020" ;
    wf:scenarioPurpose "Historical baseline for trend analysis" ;
    wf:hasTemporalExtent [
        a time:Interval ;
        time:hasBeginning [ a time:Instant ; time:inXSDDateTimeStamp "2020-01-01T00:00:00Z"^^xsd:dateTimeStamp ] ;
        time:hasEnd [ a time:Instant ; time:inXSDDateTimeStamp "2020-12-31T23:59:59Z"^^xsd:dateTimeStamp ]
    ] .

# Comparison
ghent:BaselineVsMBR a wf:ScenarioComparison ;
    wf:comparesScenarios ghent:BaselineScenario_2026 ;
    wf:comparesScenarios ghent:MBR_Alternative ;
    wf:comparisonCriterion "Capital cost" ;
    wf:comparisonCriterion "Operating cost" ;
    wf:comparisonCriterion "Water reuse percentage" ;
    wf:comparisonCriterion "Regulatory compliance" .
```

### 6.5 Scope: Medium with Future Expansion

**Current Implementation (Phase 1):**
- ✅ Basic scenario types (Baseline, Alternative, Historical, Optimization)
- ✅ Temporal representation with OWL-Time
- ✅ Scenario membership and comparison
- ✅ Scenario metadata (name, purpose, creation date)

**Future Expansion (Documented but not fully implemented):**
- 📋 Optimization objectives and weights
- 📋 Constraint modeling (regulatory, physical, economic)
- 📋 Numerical solver configuration
- 📋 Multi-objective optimization framework
- 📋 Sensitivity analysis support

**Rationale:**
- Medium scope supports immediate Ghent case study needs
- Future hooks signal planned capabilities
- Can extend incrementally as requirements emerge
- Avoids over-engineering while maintaining extensibility

---

## Part 7: PROV-O Integration

### 7.1 Purpose

Track provenance of:
- **Observations:** Which sensor? When? Who collected?
- **Model results:** Which simulation? Which parameters?
- **Scenarios:** Who created? Based on what assumptions?
- **Regulatory requirements:** Which directive? Version? Date?

### 7.2 PROV-O Core Concepts

```turtle
# PROV-O namespace (W3C standard)
@prefix prov: <http://www.w3.org/ns/prov#> .

# Core classes:
prov:Entity - Something (observation, dataset, document)
prov:Activity - Something happening (sampling, simulation, analysis)
prov:Agent - Someone/something responsible (person, organization, sensor)

# Core properties:
prov:wasGeneratedBy - Entity ← Activity (how was it created?)
prov:used - Activity → Entity (what did it use?)
prov:wasAttributedTo - Entity → Agent (who is responsible?)
prov:wasAssociatedWith - Activity → Agent (who did it?)
```

### 7.3 Integration with waterFRAME

```turtle
# Add to appropriate modules (sampling.ttl, qualities.ttl)

# Make observations PROV entities
wf:WaterQualityObservation rdfs:subClassOf prov:Entity .
wf:WaterSample rdfs:subClassOf prov:Entity .

# Sampling is an activity
wf:SamplingActivity a owl:Class ;
    rdfs:subClassOf prov:Activity ;
    rdfs:label "Sampling activity" ;
    rdfs:comment "The act of collecting a water sample" .

# Sensors and samplers are agents
wf:SamplingEquipment rdfs:subClassOf prov:Agent .
wf:OnlineSensor rdfs:subClassOf prov:Agent .

# Example relationships
wf:collectedBy a owl:ObjectProperty ;
    rdfs:subPropertyOf prov:wasAttributedTo ;
    rdfs:domain wf:WaterSample ;
    rdfs:range prov:Agent .

wf:observedBy a owl:ObjectProperty ;
    rdfs:subPropertyOf prov:wasAttributedTo ;
    rdfs:domain wf:WaterQualityObservation ;
    rdfs:range wf:SamplingEquipment .

wf:samplingTime a owl:DatatypeProperty ;
    rdfs:subPropertyOf prov:generatedAtTime ;
    rdfs:domain wf:SamplingActivity ;
    rdfs:range xsd:dateTime .
```

### 7.4 Example: Provenance-Tracked Observation

```turtle
# The observation (Entity)
ghent:WWTP_Effluent_BOD_20260127 a wf:WaterQualityObservation ;
    sosa:hasFeatureOfInterest ghent:WWTP_Effluent_Sample_001 ;
    sosa:observedProperty wf:BOD ;
    sosa:hasResult [ qudt:numericValue "8.5"^^xsd:double ; qudt:unit unit:MilliGM-PER-L ] ;
    sosa:resultTime "2026-01-27T10:30:00Z"^^xsd:dateTime ;
    prov:wasGeneratedBy ghent:Sampling_Activity_20260127 ;
    prov:wasAttributedTo ghent:Lab_Technician_Alice .

# The sampling activity
ghent:Sampling_Activity_20260127 a wf:SamplingActivity ;
    prov:startedAtTime "2026-01-27T10:00:00Z"^^xsd:dateTime ;
    prov:endedAtTime "2026-01-27T10:35:00Z"^^xsd:dateTime ;
    prov:used ghent:WWTP_Effluent_Sample_001 ;
    prov:wasAssociatedWith ghent:Autosampler_Unit_3 .

# The responsible agents
ghent:Lab_Technician_Alice a prov:Person ;
    rdfs:label "Alice Johnson" ;
    prov:actedOnBehalfOf ghent:AquaFin_Laboratory .

ghent:Autosampler_Unit_3 a wf:Autosampler ;
    rdfs:label "Autosampler #3" ;
    wf:manufacturer "Hach" ;
    wf:model "AS950" .
```

---

## Part 8: Implementation Plan

### Phase 1: Core Quality Classification (High Priority)

**Files to modify:**
1. `data/ontology/modules/core/qualities.ttl`
   - Add WaterComposition classes with jurisdictional awareness
   - Add RegulatoryFramework class
   - Add definingFramework property
   - Add hasWaterComposition property
   - Add appliesInJurisdiction property (using GeoNames)

2. `data/ontology/modules/core/properties.ttl`
   - Add ProcessWaterFlow class
   - Add IndustrialWastewaterFlow class
   - Add fromFacilityType property

3. `data/ontology/bridges/envo_alignment.ttl`
   - Add containsWaterType property
   - Add rdfs:seeAlso for all flow→material mappings
   - Add flow→material restrictions (owl:Restriction)
   - Add documentation clarifying flow vs material distinction

**Expected outcome:** Can classify water by quality (jurisdiction-aware) AND by system role

### Phase 2: Systematic rdfs:seeAlso References (High Priority)

**Files to modify:**
1. `data/ontology/modules/core/material_entities.ttl`
   - Add `rdfs:seeAlso` for ALL WaWO+ inspired process units
   - Add `rdfs:seeAlso` for Port/Terminal (OntoCAPE reference)
   - Add comments documenting relationship to source ontologies

2. `data/ontology/bridges/envo_alignment.ttl`
   - Add `rdfs:seeAlso` for natural water bodies (River→envo:river, etc.)

**Expected outcome:** Clear documentation of ALL external ontology relationships

### Phase 3: Scenario Module with OWL-Time (Medium Priority)

**Files to create:**
1. `data/ontology/modules/scenarios.ttl`
   - Import OWL-Time ontology
   - Scenario classes (Baseline, Alternative, Historical, Optimization)
   - Scenario properties (name, purpose, hasTemporalExtent)
   - Scenario membership (inScenario, scenarioComponent)
   - Scenario comparison framework
   - Future expansion hooks (OptimizationObjective, ScenarioConstraint)

2. Update `data/ontology/waterframe.ttl` to import scenarios module and OWL-Time

**Expected outcome:** Can model alternative configurations with proper temporal representation, comparison framework, and hooks for future optimization features

### Phase 4: PROV-O Integration (Low Priority - Can be deferred)

**Files to modify:**
1. `data/ontology/modules/sampling.ttl`
   - Make WaterSample subclass of prov:Entity
   - Add SamplingActivity as prov:Activity
   - Make SamplingEquipment subclass of prov:Agent

2. `data/ontology/modules/core/qualities.ttl`
   - Make WaterQualityObservation subclass of prov:Entity
   - Add provenance properties (collectedBy, observedBy)

3. `data/ontology/waterframe.ttl`
   - Import PROV-O: `owl:imports <http://www.w3.org/ns/prov#>`

**Expected outcome:** Full provenance tracking for observations and samples

---

## Part 9: Testing and Validation

### 9.1 Competency Questions to Validate

After implementation, ensure these queries work:

**CQ1: Find all water with drinking water quality under EU framework**
```sparql
SELECT ?water ?framework WHERE {
    ?water wf:hasWaterComposition ?composition .
    ?composition a wf:DrinkingWaterQuality ;
                wf:definingFramework ?framework .
    ?framework wf:appliesInJurisdiction gn:6695072 .  # EU
}
```

**CQ2: What water material type is in this greywater flow?**
```sparql
SELECT ?material WHERE {
    ?port wf:hasFlowType wf:GreywaterFlow .
    ?port wf:containsWaterType ?material .
}
```

**CQ3: Which process units reference WaWO+ or OntoCAPE?**
```sparql
SELECT ?unit ?externalClass ?externalOntology WHERE {
    ?unit rdfs:subClassOf wf:WWTPTreatmentProcess .
    ?unit rdfs:seeAlso ?externalClass .
    BIND(
        IF(CONTAINS(STR(?externalClass), "wawo"), "WaWO+",
        IF(CONTAINS(STR(?externalClass), "ontocape"), "OntoCAPE",
        "Other"))
        AS ?externalOntology
    )
}
```

**CQ4: List all components in scenarios and their time periods**
```sparql
SELECT ?scenario ?component ?start ?end WHERE {
    ?scenario wf:scenarioComponent ?component ;
             wf:hasTemporalExtent ?interval .
    ?interval time:hasBeginning ?startInstant ;
             time:hasEnd ?endInstant .
    ?startInstant time:inXSDDateTimeStamp ?start .
    ?endInstant time:inXSDDateTimeStamp ?end .
}
```

**CQ5: What is the provenance of this observation?**
```sparql
SELECT ?activity ?agent ?time WHERE {
    ghent:WWTP_Effluent_BOD_20260127 prov:wasGeneratedBy ?activity .
    ?activity prov:wasAssociatedWith ?agent ;
             prov:startedAtTime ?time .
}
```

**CQ6: Which regulatory frameworks apply in Belgium?**
```sparql
SELECT ?framework ?label WHERE {
    ?framework a wf:RegulatoryFramework ;
              rdfs:label ?label ;
              wf:appliesInJurisdiction ?jurisdiction .
    ?jurisdiction gn:countryCode "BE" .
}
```

### 9.2 Reasoner Validation

- Run HermiT/Pellet to ensure no inconsistencies
- Verify subsumption inferences work correctly
- Check that restriction-based mappings classify properly
- Validate OWL-Time temporal relationships

---

## Part 10: Decisions Summary

### Decision 1: ENVO Facility Alignment ✅ APPROVED

**Decision:** Use `rdfs:seeAlso` (Option C)

**Rationale:**
- waterFRAME models engineering infrastructure; ENVO models environmental features
- Different modeling purposes justify separate classes
- Bridge pattern maintains flexibility

### Decision 2: WaWO+ Import vs. Reference ✅ APPROVED

**Decision:** Reference only via rdfs:seeAlso (Option B)

**Rationale:**
- License restrictions may prevent import
- WaWO+ is abandoned project
- Replicating functionality ensures sustainability

### Decision 3: Scenario Module Scope ✅ APPROVED WITH MODIFICATION

**Decision:** Medium scope (Option B) WITH future expansion hooks

**Implementation:**
- Phase 1: Basic scenarios, OWL-Time temporal representation, comparison framework
- Future: Optimization objectives, constraints, solver config (documented but not fully implemented)
- Explicit hooks in code indicate planned capabilities

### Decision 4: Implementation Priority ✅ APPROVED

**Priority Order:**
1. Phase 1: Quality classification with jurisdiction awareness (HIGH - needed for Ghent data)
2. Phase 2: Systematic rdfs:seeAlso references (HIGH - documentation improvement)
3. Phase 3: Scenario module with OWL-Time (MEDIUM - enables comparisons)
4. Phase 4: PROV-O (LOW - nice-to-have, can defer)

---

## Appendix A: WaWO+ Class Reference Table

| waterFRAME Physical Unit | WaWO+ Process Concept | URI Reference (Placeholder) |
|--------------------------|----------------------|-----------------------------|
| wf:Screening | wawo:Screening | http://www.semanticweb.org/wawo/Screening |
| wf:GritRemoval | wawo:GritRemoval | http://www.semanticweb.org/wawo/GritRemoval |
| wf:PrimarySettler | wawo:PrimaryClarification | http://www.semanticweb.org/wawo/PrimaryClarification |
| wf:AerationTank | wawo:BiologicalOxidation | http://www.semanticweb.org/wawo/BiologicalOxidation |
| wf:SecondarySettler | wawo:Clarification | http://www.semanticweb.org/wawo/Clarification |
| wf:MembraneBioreactor | wawo:MembraneFiltration | http://www.semanticweb.org/wawo/MembraneFiltration |
| wf:NitrificationTank | wawo:Nitrification | http://www.semanticweb.org/wawo/Nitrification |
| wf:DenitrificationTank | wawo:Denitrification | http://www.semanticweb.org/wawo/Denitrification |
| wf:PhosphorusRemovalTank | wawo:PhosphorusRemoval | http://www.semanticweb.org/wawo/PhosphorusRemoval |
| wf:DisinfectionUnit | wawo:Disinfection | http://www.semanticweb.org/wawo/Disinfection |
| wf:ReverseOsmosisUnit | wawo:ReverseOsmosis | http://www.semanticweb.org/wawo/ReverseOsmosis |

**Note:** These URIs are placeholders. Actual WaWO+ URIs would need verification from source.

---

## Appendix B: OntoCAPE Reference Table

| waterFRAME Class | OntoCAPE Concept | URI Reference |
|-----------------|------------------|---------------|
| wf:Port | ontocape:Terminal | http://www.theworldavatar.com/ontology/ontocape/chemical_process_system/CPS_realization/plant.owl#Terminal |
| wf:InputPort | ontocape:Terminal | http://www.theworldavatar.com/ontology/ontocape/chemical_process_system/CPS_realization/plant.owl#Terminal |
| wf:OutputPort | ontocape:Terminal | http://www.theworldavatar.com/ontology/ontocape/chemical_process_system/CPS_realization/plant.owl#Terminal |

**Source:** Marquardt et al. (2010) - OntoCAPE process modeling ontology

---

## Appendix C: Regulatory Framework Examples

| Framework | Jurisdiction | GeoNames ID | URL |
|-----------|-------------|-------------|-----|
| EU Water Framework Directive | European Union | gn:6695072 | https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02000L0060 |
| EU Drinking Water Directive (2020/2184) | European Union | gn:6695072 | https://eur-lex.europa.eu/eli/dir/2020/2184 |
| EU Water Reuse Regulation (2020/741) | European Union | gn:6695072 | https://eur-lex.europa.eu/eli/reg/2020/741 |
| WHO Drinking Water Guidelines | Global | - | https://www.who.int/publications/i/item/9789240045064 |
| US EPA Safe Drinking Water Act | United States | gn:6252001 | https://www.epa.gov/sdwa |
| Belgian Water Decree (Vlarem) | Belgium (Flanders) | gn:2800866 | https://navigator.emis.vito.be/milnav-consult/ |

---

## Appendix D: References

1. **Zhou, X., et al. (2019).** "An agent composition framework for the J-Park Simulator." *Computers & Chemical Engineering*, 130, 106577.

2. **OntoAgent Analysis:** `research/ontologies/OntoAgent/COMPREHENSIVE_ANALYSIS.md`

3. **OntoCAPE Findings:** `research/ontologies/ontoCAPE/FINDINGS.md`

4. **WaWO+ Evaluation:** `research/ontologies/WaWO/WaWO_Plus_Evaluation_Report.md`

5. **ENVO Ontology:** http://purl.obolibrary.org/obo/envo.owl

6. **PROV-O:** https://www.w3.org/TR/prov-o/

7. **OWL-Time:** https://www.w3.org/TR/owl-time/

8. **BFO:** http://purl.obolibrary.org/obo/bfo.owl

9. **GeoNames Ontology:** http://www.geonames.org/ontology/documentation.html

---

**END OF PLANNING DOCUMENT**

**Status:** Ready for approval

**Next Steps:**
1. Review this document (v1.1)
2. Approve all decisions
3. Upon approval, implement phases in priority order
4. Create implementation tracking document
