# waterFRAME Ontology Refinement Issues

**Date Created**: 2026-01-28
**Related Plan**: /Users/jeandavidt/.claude/plans/lucky-doodling-dongarra.md
**Priority**: CRITICAL

---

## Phase 1: ENVO Concept Verification and Correction

**Status**: COMPLETED
**Date**: 2026-01-28
**ENVO Version**: 2025-10-20

### Verification Summary

Verified 9 ENVO concept mappings against the ENVO 2025-10-20 release. **6 out of 9 mappings were INCORRECT**.

### Critical Mismatches Found

| WF Concept | Incorrect IRI | Claimed As | Actual Label | Correct IRI | Action |
|------------|---------------|------------|--------------|-------------|--------|
| wf:Greywater | envo:00002223 | "grey water" | **oligotrophic water** | NOT IN ENVO | Convert to rdfs:comment |
| wf:PotableWaterFlow | envo:00003097 | "drinking water" | **bore hole water** | envo:00003064 | Update IRI |
| wf:ReclaimedWaterFlow | envo:00002044 | "treated wastewater" | **sludge** | envo:06105268 | Update IRI |
| wf:Groundwater | envo:00002001 | "groundwater" | **waste water** | envo:01001004 | Update IRI |
| wf:DrinkingWaterTreatmentPlant | envo:01001886 | "drinking water treatment plant" | **landform** | envo:03600004 | Update IRI |

### Correct Mappings (No Change Needed)

| WF Concept | ENVO IRI | Label | Status |
|------------|----------|-------|--------|
| wf:River | envo:00000022 | river | ✓ CORRECT |
| wf:Lake | envo:00000020 | lake | ✓ CORRECT |
| wf:WastewaterTreatmentPlant | envo:00002043 | wastewater treatment plant | ✓ CORRECT |
| wf:Blackwater | envo:00002018 | sewage | ✓ CORRECT |

### Detailed Findings

#### 1. Greywater - NOT IN ENVO
- **Current mapping**: envo:00002223 (claimed as "grey water")
- **Actual ENVO:00002223**: "oligotrophic water" - Water which has very low concentrations of nutrients
- **Search results**: No "greywater" or "grey water" concept exists in ENVO 2025-10-20
- **Action**: Remove rdfs:seeAlso reference, add textual rdfs:comment explaining greywater concept

#### 2. Drinking Water - WRONG IRI
- **Current mapping**: envo:00003097 (claimed as "drinking water")
- **Actual ENVO:00003097**: "bore hole water"
- **Correct IRI**: envo:00003064
- **Correct definition**: "Drinking water is water which may be consumed by humans with no adverse effects on their health."
- **Synonym**: "potable water" EXACT
- **Action**: Update all references from envo:00003097 to envo:00003064

#### 3. Treated Wastewater/Reclaimed Water - WRONG IRI
- **Current mapping**: envo:00002044 (claimed as "treated wastewater")
- **Actual ENVO:00002044**: "sludge" - The residual semi-solid material left from domestic or industrial processes, or wastewater treatment processes
- **Correct IRI**: envo:06105268
- **Correct label**: "treated wastewater"
- **Action**: Update all references from envo:00002044 to envo:06105268

#### 4. Groundwater - WRONG IRI
- **Current mapping**: envo:00002001 (claimed as "groundwater")
- **Actual ENVO:00002001**: "waste water" - Water that has been adversely affected in quality by anthropogenic influence
- **Correct IRI**: envo:01001004
- **Correct definition**: "Underground water which is located in pore spaces found in rock or unconsolidated deposits such as soil, clay, or gravel."
- **Action**: Update all references from envo:00002001 to envo:01001004

#### 5. Drinking Water Treatment Plant - WRONG IRI
- **Current mapping**: envo:01001886 (claimed as "drinking water treatment plant")
- **Actual ENVO:01001886**: "landform" - A solid astronomical body part which has been formed from and is composed primarily of the matter of that astronomical body
- **Correct IRI**: envo:03600004
- **Correct label**: "drinking water treatment plant"
- **Action**: Update reference from envo:01001886 to envo:03600004

### Impact Analysis

These incorrect mappings would cause:
1. **Semantic reasoning errors**: Queries asking for "drinking water" would return bore hole water concepts
2. **Data integration failures**: External systems using ENVO would misinterpret waterFRAME concepts
3. **Incorrect inferences**: OWL reasoners would classify entities incorrectly based on wrong ENVO alignments
4. **Confusion for users**: Documentation claims don't match actual linked concepts

### References
- ENVO GitHub: https://github.com/EnvironmentOntology/envo
- ENVO OBO Foundry: http://obofoundry.org/ontology/envo.html
- Local ENVO version: /Users/jeandavidt/Developer/jeandavidt/ontEAUlogy/research/ontologies/envo-2025-10-20/

---

## Phase 2: Placeholder
*To be populated with Phase 2 issues*

---

## Phase 3: Placeholder
*To be populated with Phase 3 issues*

---

## Phase 4: Placeholder
*To be populated with Phase 4 issues*

---

## Phase 5: Conveyance System Expansion for Sewer Modeling

**Status**: COMPLETED
**Date**: 2026-01-28

### Implementation Summary

Expanded the generic `wf:Conveyance` class into a comprehensive hierarchy supporting detailed sewer system modeling, including CSOs, pipes, splitters, junctions, and pumping infrastructure.

### Classes Added (17 total)

#### Pipes and Conduits (7 classes)
1. `wf:Pipe` - Enclosed conduit for water transport
2. `wf:PressurizedPipe` - Pipe operating under positive pressure (e.g., water mains)
3. `wf:GravityPipe` - Pipe where water flows by gravity
4. `wf:SewerPipe` - Underground pipe for wastewater or stormwater collection
5. `wf:CombinedSewer` - Sewer carrying both sanitary wastewater and stormwater
6. `wf:SanitarySewer` - Sewer carrying only domestic and industrial wastewater
7. `wf:StormSewer` - Sewer carrying only stormwater runoff
8. `wf:Canal` - Open channel for water transport

#### Flow Dividers (6 classes)
9. `wf:FlowDivider` - Structure that splits one inflow into multiple outflows
10. `wf:Splitter` - Controlled flow division with specified split ratios
11. `wf:OverflowStructure` - Structure that diverts excess flow when capacity threshold exceeded
12. `wf:CombinedSewerOverflow` (CSO) - Critical for urban wet weather modeling
13. `wf:StormwaterOutfall` - Controlled stormwater discharge structure
14. `wf:EmergencyOverflow` - Safety overflow for extreme events

#### Flow Mergers (2 classes)
15. `wf:FlowMerger` - Structure that combines multiple inflows into one outflow
16. `wf:Junction` - Meeting point of multiple pipes (e.g., manhole)

#### Pumping (2 classes)
17. `wf:PumpStation` - Facility to move water against gravity or increase pressure
18. `wf:LiftStation` - Pump station in wastewater systems to lift sewage

### Properties Added (5 total)

#### Geometric Properties (3 datatype properties)
1. `wf:hasDiameter` - Internal diameter of pipe in meters (domain: wf:Pipe, range: xsd:double)
2. `wf:hasLength` - Length of conveyance element in meters (domain: wf:Conveyance, range: xsd:double)
3. `wf:hasSlope` - Slope of pipe, dimensionless (domain: wf:Pipe, range: xsd:double)

#### Overflow Properties (2 object properties)
4. `wf:overflowsTo` - Links overflow structure to discharge destination (domain: wf:OverflowStructure, range: wf:WaterSystemComponent)
5. `wf:activationThreshold` - Flow rate or level that triggers overflow (domain: wf:OverflowStructure, range: wf:QuantityValue)

### Design Decisions

#### CSO Placement Rationale
Placed `wf:CombinedSewerOverflow` under `wf:OverflowStructure` (rather than directly under conveyance) because:
- CSOs are fundamentally threshold-activated flow dividers
- Inherit `activationThreshold` and `overflowsTo` properties naturally
- Aligns with hydraulic modeling patterns (activation-based behavior)
- Consistent with other overflow structures (stormwater outfalls, emergency overflows)

#### Sewer Type Hierarchy
Three sewer types inherit from `wf:SewerPipe` which inherits from `wf:GravityPipe`:
- **Combined sewers**: Handle both wastewater and stormwater (older urban systems)
- **Sanitary sewers**: Wastewater only (modern separated systems)
- **Storm sewers**: Stormwater only (modern separated systems)

This supports modeling both legacy combined systems (with CSO issues) and modern separated systems.

#### Hydraulic Modeling Support
Properties enable computational hydraulic modeling:
- `hasDiameter` + `hasSlope` → Manning's equation for flow capacity
- `hasLength` → flow travel time calculations
- `activationThreshold` → CSO activation during wet weather events
- Geometry properties use SI units (meters) for consistency

### Impact on Ghent Case Study

This expansion directly enables:
1. **CSO modeling** - Can now represent the 135 CSO structures in Ghent's combined sewer system
2. **Pipe network topology** - Distinguish gravity vs pressurized pipes, sewer types
3. **Overflow events** - Model wet weather CSO activations and discharge volumes
4. **Hydraulic calculations** - Diameter, slope, length support flow capacity calculations

### Files Modified

1. `data/ontology_enhanced/modules/core/material_entities.ttl` (lines 94-177)
   - Replaced minimal 4-line `wf:Conveyance` definition with comprehensive 84-line hierarchy

2. `data/ontology_enhanced/modules/core/properties.ttl` (lines 225-261)
   - Added xsd namespace prefix
   - Added 5 conveyance-specific properties

3. `validation/phase5_conveyance_validation.sparql` (NEW)
   - SPARQL query to verify hierarchy completeness

### Validation

SPARQL query created to verify:
- All conveyance classes have proper rdfs:subClassOf relationships
- All classes have labels and comments
- Hierarchy is properly rooted under wf:Conveyance

Query location: `/Users/jeandavidt/Developer/jeandavidt/ontEAUlogy/validation/phase5_conveyance_validation.sparql`

---

## Notes
- This issue log tracks problems discovered during ontology refinement
- Each phase should document issues found and actions taken
- Priority levels: CRITICAL, HIGH, MEDIUM, LOW
