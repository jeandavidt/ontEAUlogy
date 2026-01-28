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

## Notes
- This issue log tracks problems discovered during ontology refinement
- Each phase should document issues found and actions taken
- Priority levels: CRITICAL, HIGH, MEDIUM, LOW
