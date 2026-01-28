# Ontology Enhancement Implementation - Issue Tracker

**Project:** waterFRAME Ontology Enhancement
**Based on:** ONTOLOGY_ENHANCEMENT_PLAN.md v1.1
**Start Date:** 2026-01-27
**Status:** In Progress

---

## Implementation Progress

### Phase 1: Core Quality Classification ✅ COMPLETED
**Priority:** HIGH
**Status:** Completed on 2026-01-27
**Assigned Files:**
- `data/ontology_enhanced/modules/qualities.ttl`
- `data/ontology_enhanced/modules/core/properties.ttl`
- `data/ontology_enhanced/modules/bridges/envo_alignment.ttl`

**Tasks:**
- [x] Add WaterComposition classes with jurisdictional awareness
- [x] Add RegulatoryFramework class
- [x] Add definingFramework, hasWaterComposition, appliesInJurisdiction properties
- [x] Add ProcessWaterFlow and IndustrialWastewaterFlow classes
- [x] Add containsWaterType property and flow→material mappings
- [x] Add flow vs material documentation in envo_alignment.ttl
- [x] Add example framework instances (EU WFD, WHO Guidelines, EU Water Reuse)
- [x] Git commit

**Issues:** None

**Implementation Notes:**
- Added 5 WaterComposition classes: DrinkingWaterQuality, WastewaterQuality, ReclaimedWaterQuality, GreywaterQuality, BlackwaterQuality
- Added RegulatoryFramework class with jurisdiction awareness via GeoNames
- Added properties: definingFramework, hasWaterComposition, appliesInJurisdiction, fromFacilityType, containsWaterType
- Added ProcessWaterFlow and IndustrialWastewaterFlow for industry-specific flows
- Added explicit rdfs:seeAlso references to WaWO+ concepts
- Added owl:Restriction-based equivalences for flow→material mappings
- Added clear documentation distinguishing flow types (engineering) from material types (environmental)
- Added example instances: EU_WaterFrameworkDirective, WHO_DrinkingWaterGuidelines, EU_WaterReuseRegulation

---

### Phase 2: Systematic rdfs:seeAlso References ✅ COMPLETED
**Priority:** HIGH
**Status:** Completed
**Completed Date:** 2026-01-27
**Assigned Files:**
- `data/ontology_enhanced/modules/core/material_entities.ttl`
- `data/ontology_enhanced/modules/bridges/envo_alignment.ttl`

**Tasks:**
- [x] Add rdfs:seeAlso for ALL WaWO+ inspired process units
- [x] Add rdfs:seeAlso for Port/Terminal (OntoCAPE reference)
- [x] Add rdfs:seeAlso for natural water bodies (ENVO references)
- [x] Add documentation comments for all external relationships
- [ ] Run reasoner consistency check (deferred to validation phase)
- [x] Git commit

**Issues:** None

**Implementation Notes:**
- Added rdfs:seeAlso references to 11 WaWO+ process units: Screening, GritRemoval, PrimarySettler, AerationTank, SecondarySettler, MembraneBioreactor (2 locations), NitrificationTank, DenitrificationTank, PhosphorusRemovalTank, DisinfectionUnit, ReverseOsmosisUnit
- Added rdfs:seeAlso references to OntoCAPE Terminal for Port, InputPort, OutputPort
- Added rdfs:seeAlso references to ENVO features for River, RiverSegment, Lake, Groundwater
- Added explanatory rdfs:comment entries documenting relationships to external ontologies
- All references follow the pattern from ONTOLOGY_ENHANCEMENT_PLAN.md Appendix A and B

---

### Phase 3: Scenario Module with OWL-Time ✅ COMPLETED
**Priority:** MEDIUM
**Status:** Completed on 2026-01-27
**Files Created:**
- `data/ontology_enhanced/modules/scenarios.ttl`

**Files Modified:**
- `data/ontology_enhanced/waterframe.ttl`

**Tasks:**
- [x] Create scenarios.ttl with Scenario classes
- [x] Import OWL-Time ontology
- [x] Add scenario properties and relationships
- [x] Add scenario comparison framework
- [x] Add future expansion hooks (OptimizationObjective, ScenarioConstraint, SimulationParameter)
- [x] Update waterframe.ttl to import scenarios module and OWL-Time
- [ ] Run reasoner consistency check (deferred to validation phase)
- [x] Git commit

**Issues:** None

**Implementation Notes:**
- Created complete scenarios.ttl module with all required classes and properties
- Added 4 scenario types: BaselineScenario, AlternativeScenario, HistoricalScenario, OptimizationScenario
- Integrated OWL-Time for temporal representation (hasTemporalExtent property linking to time:TemporalEntity)
- Added scenario properties: scenarioName, scenarioPurpose, scenarioDescription, scenarioCreationDate
- Added scenario relationships: baselineFor, alternativeTo (with owl:inverseOf)
- Added scenario membership properties: inScenario, scenarioComponent, scenarioParameter
- Added ScenarioComparison class with comparesScenarios and comparisonCriterion properties
- Added future expansion hooks with clear "FUTURE:" comments:
  - OptimizationObjective class (with rdfs:seeAlso to OntoAgent)
  - ScenarioConstraint class
  - SimulationParameter class
  - hasObjective property
  - hasConstraint property
- Included comprehensive documentation with example usage patterns in comments
- All classes properly aligned with BFO (Scenario as bfo:BFO_0000031)
- Module follows existing waterFRAME conventions and structure

---

### Phase 4: PROV-O Integration ✅ COMPLETED
**Priority:** LOW
**Status:** Completed on 2026-01-27
**Assigned Files:**
- `data/ontology_enhanced/modules/sampling.ttl`
- `data/ontology_enhanced/modules/qualities.ttl`
- `data/ontology_enhanced/waterframe.ttl`

**Tasks:**
- [x] Make WaterSample subclass of prov:Entity
- [x] Add SamplingActivity as prov:Activity
- [x] Make SamplingEquipment subclass of prov:Agent
- [x] Make WaterQualityObservation subclass of prov:Entity
- [x] Add provenance properties (collectedBy, observedBy)
- [x] Import PROV-O in waterframe.ttl
- [ ] Run reasoner consistency check (deferred to validation phase)
- [x] Git commit

**Issues:** None

**Implementation Notes:**
- WaterSample is now rdfs:subClassOf prov:Entity with provenance tracking capabilities
- WaterQualityObservation is now rdfs:subClassOf prov:Entity for observation provenance
- SamplingActivity class created as rdfs:subClassOf prov:Activity
- SamplingEquipment and OnlineSensor are rdfs:subClassOf prov:Agent
- Added provenance properties:
  - collectedBy (rdfs:subPropertyOf prov:wasAttributedTo) for sample attribution
  - observedBy (rdfs:subPropertyOf prov:wasAttributedTo) for observation attribution
  - samplingTime (rdfs:subPropertyOf prov:generatedAtTime) for temporal tracking
- Direct import of PROV-O added to waterframe.ttl: owl:imports <http://www.w3.org/ns/prov#>
- All PROV-O alignments maintain compatibility with existing SOSA alignments
- Comprehensive documentation added explaining provenance tracking capabilities

---

## Known Issues

### Issue Log
*No issues reported yet*

---

## Reasoner Consistency Checks

### Check 1: Initial Baseline
**Date:** Pending
**Reasoner:** TBD (HermiT/Pellet)
**Status:** Not Run
**Result:** N/A

---

## Git Commits

### Commit Log
*No commits yet*

---

## Notes

- Working in `data/ontology_enhanced/` to avoid breaking existing ghent use case
- After ontology completion, will create updated Ghent data in new folder
- Each phase should be independently validated before proceeding to next

---

**Last Updated:** 2026-01-27
