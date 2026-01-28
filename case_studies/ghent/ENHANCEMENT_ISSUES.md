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

### Phase 3: Scenario Module with OWL-Time ⏳ PENDING
**Priority:** MEDIUM
**Status:** Not Started
**Files to Create:**
- `data/ontology_enhanced/modules/scenarios.ttl`

**Files to Modify:**
- `data/ontology_enhanced/waterframe.ttl`

**Tasks:**
- [ ] Create scenarios.ttl with Scenario classes
- [ ] Import OWL-Time ontology
- [ ] Add scenario properties and relationships
- [ ] Add scenario comparison framework
- [ ] Add future expansion hooks (OptimizationObjective, ScenarioConstraint)
- [ ] Update waterframe.ttl to import scenarios module and OWL-Time
- [ ] Run reasoner consistency check
- [ ] Git commit

**Issues:** None yet

---

### Phase 4: PROV-O Integration ⏳ PENDING
**Priority:** LOW
**Status:** Not Started
**Assigned Files:**
- `data/ontology_enhanced/modules/sampling.ttl`
- `data/ontology_enhanced/modules/qualities.ttl`
- `data/ontology_enhanced/waterframe.ttl`

**Tasks:**
- [ ] Make WaterSample subclass of prov:Entity
- [ ] Add SamplingActivity as prov:Activity
- [ ] Make SamplingEquipment subclass of prov:Agent
- [ ] Make WaterQualityObservation subclass of prov:Entity
- [ ] Add provenance properties
- [ ] Import PROV-O in waterframe.ttl
- [ ] Run reasoner consistency check
- [ ] Git commit

**Issues:** None yet

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
