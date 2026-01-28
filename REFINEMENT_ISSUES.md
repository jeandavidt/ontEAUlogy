# waterFRAME Ontology Refinement - Implementation Issues Tracker

**Project:** waterFRAME Ontology Revision
**Branch:** `feature/synthetic-case-study`
**Started:** 2026-01-28

## Purpose
This document tracks issues, blockers, and decisions encountered during the implementation of the waterFRAME ontology revision plan.

---

## Phase Status Summary

| Phase | Status | Issues | Notes |
|-------|--------|--------|-------|
| Phase 1: ENVO Verification | Not Started | - | CRITICAL PRIORITY |
| Phase 2: BFO Alignment | Completed | 0 | CRITICAL PRIORITY |
| Phase 3: WaWO+ Cleanup | Completed | 0 | - |
| Phase 4: Property Relationships | Completed | 0 | - |
| Phase 5: Conveyance System | Not Started | - | - |
| Phase 6: OWL-Time Simplification | Not Started | - | - |
| Phase 7: Usage Point Refinement | Not Started | - | - |
| Phase 8: Facility Definitions | Not Started | - | - |
| Phase 9: Fit-for-Purpose Framework | Not Started | - | - |
| Phase 10: Testing & Validation | Not Started | - | - |

---

## Issues Log

### Format
```
## Issue #N: [Title]
- **Phase:** [Phase number]
- **Severity:** [Critical/High/Medium/Low]
- **Status:** [Open/In Progress/Resolved/Blocked]
- **Description:** [Detailed description]
- **Resolution:** [How it was resolved, if applicable]
- **Date:** [YYYY-MM-DD]
```

---

## Phase 1: ENVO Concept Verification

*No issues logged yet*

---

## Phase 2: BFO Alignment - Separate Material Entities from Processes

### Summary
Phase 2 successfully fixed a fundamental BFO violation where treatment units were classified as material entities but named as "processes". The refactoring separated material entities (physical infrastructure) from processes (occurrents) in accordance with BFO's continuant/occurrent distinction.

### Implementation Details

**Files Created:**
- `data/ontology_enhanced/modules/core/processes.ttl` - New module defining BFO-compliant process hierarchy
- `case_studies/ghent_enhanced/validation/bfo_compliance_check.sparql` - SPARQL validation query

**Files Modified:**
- `data/ontology_enhanced/modules/core/material_entities.ttl` (lines 136-210) - Replaced process-named classes with proper physical unit names
- `data/ontology_enhanced/waterframe.ttl` - Added import for processes module
- `case_studies/ghent_enhanced/data/instances/wwtp1.ttl` - Updated class names and added wf:performsProcess links
- `case_studies/ghent_enhanced/data/instances/wwtp2.ttl` - Updated class names and added wf:performsProcess links

**Classes Removed/Renamed:**
- Removed: `wf:WWTPTreatmentProcess`, `wf:PrimaryTreatment`, `wf:SecondaryTreatment`, `wf:TertiaryTreatment` (conceptually incorrect)
- Renamed: Treatment unit classes now use physical infrastructure names (e.g., ScreeningUnit, GritChamber, PrimaryClarifier, AerationBasin, etc.)
- Added backward-compatible aliases for old names used in case studies

**New Process Hierarchy Created (BFO:0000015 - Occurrent):**
- `wf:WaterTreatmentProcess` (root process class, subclass of BFO:0000015)
  - `wf:ScreeningProcess`
  - `wf:GritRemovalProcess`
  - `wf:PrimaryClarificationProcess`
  - `wf:BiologicalOxidationProcess`
  - `wf:SecondaryClarificationProcess`
  - `wf:MembraneFiltrationProcess`
  - `wf:NitrificationProcess`
  - `wf:DenitrificationProcess`
  - `wf:PhosphorusRemovalProcess`
  - `wf:DisinfectionProcess`

**New Property Created:**
- `wf:performsProcess` - Links physical treatment units (material entities) to the processes (occurrents) they enable

**Physical Treatment Units (BFO:0000040 - Material Entity):**
All treatment units are now properly classified as material entities under `wf:TreatmentUnit`:
- `wf:ScreeningUnit` (with alias `wf:Screening`)
- `wf:GritChamber` (with alias `wf:GritRemoval`)
- `wf:PrimaryClarifier` (with alias `wf:PrimarySettler`)
- `wf:AerationBasin` (with alias `wf:AerationTank`)
- `wf:SecondaryClarifier` (with alias `wf:SecondarySettler`)
- `wf:MembraneFilterUnit`
- `wf:MembraneBioreactor`
- `wf:NitrificationReactor` (with alias `wf:NitrificationTank`)
- `wf:DenitrificationReactor` (with alias `wf:DenitrificationTank`)
- `wf:PhosphorusRemovalTank`
- `wf:DisinfectionChamber` (with alias `wf:DisinfectionUnit`)

### Validation Results

**BFO Compliance Check:** PASSED
- Query: Check for material entities incorrectly classified as processes
- Result: 0 violations found
- Verification:
  - `wf:WaterSystemComponent` → `bfo:BFO_0000040` (material entity/continuant) ✓
  - `wf:TreatmentUnit` → `wf:WaterSystemComponent` (material entity) ✓
  - `wf:WaterTreatmentProcess` → `bfo:BFO_0000015` (occurrent/process) ✓
  - All physical units properly subclass `wf:TreatmentUnit` ✓
  - No material entities inherit from process classes ✓

**Instance File Validation:**
- WWTP-1: 7 treatment units with 10 process links (nutrient removal performs 3 processes)
- WWTP-2: 7 treatment units with 10 process links (MBR performs 2 processes, nutrient removal performs 3)
- All instances now explicitly link physical units to the processes they perform via `wf:performsProcess`

### Design Decisions

**Decision 1: Backward-Compatible Aliases**
- Context: Existing case study instances used old class names
- Decision: Create alias classes (e.g., `wf:Screening` as subclass of `wf:ScreeningUnit`)
- Rationale: Minimizes disruption to existing instance data while promoting new names
- Alternative: Force update all instances immediately (rejected - too disruptive for early phase)

**Decision 2: Multi-Process Units**
- Context: Some physical units perform multiple processes (e.g., MBR, nutrient removal)
- Decision: Allow multiple `wf:performsProcess` statements per unit
- Rationale: Reflects reality - one physical unit can host multiple simultaneous processes
- Alternative: Force 1:1 mapping (rejected - overly restrictive)

**Decision 3: Process Module Placement**
- Context: Where to place the new processes module
- Decision: Place in `modules/core/processes.ttl` alongside material_entities
- Rationale: Processes are as fundamental as material entities in water treatment ontology
- Alternative: Create separate process domain modules (rejected - premature for this phase)

### Issues Encountered

No blocking issues encountered. Implementation was straightforward following the plan.

### Future Considerations

1. Consider adding intermediate process categories (PhysicalProcess, BiologicalProcess, ChemicalProcess)
2. May need to add temporal extent properties for processes (duration, start/end times)
3. Consider adding process capability/efficiency properties in future phases
4. Could add process-specific parameters (e.g., hydraulic retention time, sludge age)

### Date Completed
2026-01-28

---

## Phase 3: WaWO+ Cleanup

### Summary
Phase 3 successfully removed all references to the unpublished WaWO+ ontology (rdfs:seeAlso URIs) and converted them to textual documentation in rdfs:comment. This ensures the ontology contains no non-resolvable URIs and maintains semantic correctness.

### Implementation Details

**Problem:**
WaWO+ is an unpublished ontology with URIs like `http://www.semanticweb.org/wawo/...` that are not resolvable. These rdfs:seeAlso references were inappropriate for semantic linking and needed to be converted to textual documentation.

**Files Modified:**
- `data/ontology_enhanced/modules/core/material_entities.ttl` - 24 WaWO+ references converted
- `data/ontology_enhanced/modules/qualities.ttl` - 2 WaWO+ references converted
- `data/ontology_enhanced/modules/core/processes.ttl` - 10 WaWO+ references converted

**Total References Converted:** 36

**Conversion Pattern:**
Before:
```turtle
wf:AerationBasin rdfs:subClassOf wf:TreatmentUnit ;
    rdfs:label "Aeration basin" ;
    rdfs:seeAlso <http://www.semanticweb.org/wawo/BiologicalOxidation> ;
    rdfs:comment "Physical tank where aerobic biological treatment occurs" .
```

After:
```turtle
wf:AerationBasin rdfs:subClassOf wf:TreatmentUnit ;
    rdfs:label "Aeration basin" ;
    rdfs:comment "Physical tank where aerobic biological treatment occurs. Conceptually related to WaWO+ BiologicalOxidation process (unpublished ontology)." .
```

**WaWO+ Concepts Referenced (now as textual notes):**
- Material Entities: MembraneFiltration, ReverseOsmosis, Screening, GritRemoval, PrimaryClarification, BiologicalOxidation, Clarification, Nitrification, Denitrification, PhosphorusRemoval, Disinfection
- Qualities: DrinkingWaterComposition, WastewaterComposition

### Validation Results

**URI Reference Check:** PASSED
- Command: `grep -r "semanticweb.org/wawo" data/ontology_enhanced/`
- Result: 0 matches (all WaWO+ URIs successfully removed)

**Documentation Preservation:**
- All WaWO+ concept names preserved as textual references
- Clear indication that WaWO+ is an unpublished ontology
- Maintains documentation value while removing non-resolvable URIs

### Design Decisions

**Decision 1: Textual Reference Format**
- Context: How to preserve WaWO+ concept information without URIs
- Decision: Use format "Conceptually related to WaWO+ [ConceptName] (unpublished ontology)."
- Rationale: Makes it clear the reference is informational, not a semantic link
- Alternative: Remove all WaWO+ references (rejected - loses valuable documentation)

**Decision 2: Merge Duplicate Comments**
- Context: Some classes had duplicate rdfs:comment statements
- Decision: Merge into single comprehensive comment
- Rationale: Cleaner RDF and easier to maintain
- Alternative: Keep separate comments (rejected - violates best practices)

**Decision 3: Extend to All Modules**
- Context: Plan only mentioned material_entities and qualities
- Decision: Also clean up processes.ttl (10 additional references)
- Rationale: Complete cleanup ensures no WaWO+ URIs remain anywhere
- Alternative: Skip processes.ttl (rejected - incomplete cleanup)

### Issues Encountered

No blocking issues encountered. Implementation was straightforward following the conversion pattern.

### Future Considerations

1. If WaWO+ is ever published with resolvable URIs, these textual references could be converted back to rdfs:seeAlso
2. Consider adding skos:related properties if publishing WaWO+ mapping later
3. May want to add more detailed conceptual mappings in documentation

### Date Completed
2026-01-28

---

## Phase 4: Property Relationships - Semantic Connections

### Summary
Phase 4 successfully created explicit semantic connections between three previously disconnected flow properties: flowsTo, dischargesInto, and abstractsFrom. A property hierarchy was established to clarify the distinction between engineered system topology and environmental discharge relationships.

### Implementation Details

**Problem:**
Three related properties existed with no explicit semantic connections:
- `wf:flowsTo` - Port-level flow connections (OutputPort → InputPort) for engineered system topology
- `wf:dischargesInto` - Component-level environmental discharge (component → ENVO aquatic feature)
- `wf:abstractsFrom` - Component-level source abstraction (component ← ENVO aquatic feature)

These properties serve different competency questions (engineering design vs. environmental compliance) but lacked documentation explaining their relationships.

**Files Modified:**
- `data/ontology_enhanced/modules/core/properties.ttl` (lines 5, 44-49, 195-221) - Added ENVO prefix, updated flowsTo comment, created property hierarchy
- `data/ontology_enhanced/modules/bridges/envo_alignment.ttl` (lines 56-69) - Removed duplicate definitions, added reference note

**Files Created:**
- `case_studies/ghent_enhanced/validation/property_hierarchy_check.sparql` - SPARQL validation query

**Property Hierarchy Created:**

```
wf:dischargesToEnvironment (root property)
├── Domain: wf:WaterSystemComponent
├── Range: bfo:BFO_0000040 (material entity - environmental recipients)
└── wf:dischargesInto (specialized subproperty)
    ├── rdfs:subPropertyOf wf:dischargesToEnvironment
    ├── Domain: wf:WaterSystemComponent
    └── Range: envo:00000063 (aquatic feature - more specific)

wf:abstractsFrom (related but distinct)
├── Domain: wf:WaterSystemComponent
├── Range: envo:00000063 (aquatic feature)
└── Related to dischargesInto (opposite flow direction)

wf:flowsTo (engineered system property - documented relationship)
├── Domain: wf:OutputPort
├── Range: wf:InputPort
└── Distinct from dischargesInto (different competency questions)
```

**New Property Added:**
- `wf:dischargesToEnvironment` - Generic property for environmental discharge to any material entity (water body, soil, atmosphere)

**Properties Modified:**
- `wf:dischargesInto` - Now defined as subproperty of dischargesToEnvironment with constrained range to ENVO aquatic features
- `wf:abstractsFrom` - Enhanced comment to explain relationship to dischargesInto
- `wf:flowsTo` - Updated comment to clarify distinction from environmental discharge properties

### Design Rationale

**Different Competency Questions:**
- `wf:flowsTo` answers: "How is water routed through the engineered system for simulation?"
- `wf:dischargesInto` answers: "Where does this facility discharge to the environment for compliance?"
- `wf:abstractsFrom` answers: "What natural water source does this facility draw from?"

**Property Hierarchy Benefits:**
1. Makes relationship between generic discharge and aquatic-specific discharge explicit
2. Allows future expansion (e.g., dischargesToSoil, dischargesToAtmosphere as siblings)
3. Enables reasoning: anything that dischargesInto also dischargesToEnvironment
4. Clarifies that environmental discharge is at component level, not port level

**Separation of Concerns:**
- Port-level properties (flowsTo, receivesFlowFrom) - Operational topology for simulation/design
- Component-level properties (dischargesInto, abstractsFrom) - Environmental context for compliance/ecology

### Validation Results

**Property Hierarchy Structure:** VERIFIED
- wf:dischargesInto correctly declared as rdfs:subPropertyOf wf:dischargesToEnvironment
- wf:dischargesToEnvironment has domain wf:WaterSystemComponent and range bfo:BFO_0000040
- wf:dischargesInto has constrained range envo:00000063 (aquatic feature)
- wf:abstractsFrom has same domain/range as dischargesInto but opposite semantic direction

**Documentation Clarity:** VERIFIED
- wf:flowsTo comment now explains distinction from dischargesInto
- Property comments explain their different roles and competency questions
- ENVO alignment module updated to reference properties.ttl definitions

**Consistency Check:** PASSED
- No duplicate property definitions across modules
- ENVO prefix added to properties.ttl for aquatic feature references
- All IRIs correctly formatted using ENVO prefix

### Design Decisions

**Decision 1: Create New Generic Property**
- Context: Should dischargesInto remain standalone or become part of hierarchy?
- Decision: Create wf:dischargesToEnvironment as generic parent property
- Rationale: Enables future expansion for other discharge types (soil, atmosphere) and makes semantics explicit
- Alternative: Keep dischargesInto standalone (rejected - less extensible, unclear semantics)

**Decision 2: Property Placement**
- Context: Where to define environmental discharge properties?
- Decision: Define in properties.ttl (core module), reference from envo_alignment.ttl (bridge module)
- Rationale: Properties are core infrastructure, ENVO alignment provides usage context
- Alternative: Define in envo_alignment.ttl (rejected - properties are waterFRAME concepts, not ENVO concepts)

**Decision 3: Documentation Style**
- Context: How to explain the relationship between flowsTo and dischargesInto?
- Decision: Enhanced comments explaining "different competency questions" approach
- Rationale: Makes it clear both properties are correct, serve different purposes
- Alternative: Make flowsTo and dischargesInto related via property chain (rejected - they operate at different granularities)

### Issues Encountered

No blocking issues encountered. Implementation was straightforward following the plan.

### Future Considerations

1. Could add sibling properties: wf:dischargesToSoil, wf:dischargesToAtmosphere for other discharge types
2. May want to add inverse property for abstractsFrom (e.g., wf:suppliesWaterTo)
3. Could create property chains: component hasOutputPort → flowsTo → hasInputPort → component to infer hasDownstreamComponent
4. Consider adding temporal properties for seasonal abstraction/discharge patterns

### Semantic Impact

**Improved Reasoning:**
- OWL reasoners can now infer that anything dischargesInto aquatic features also dischargesToEnvironment
- Clear distinction between operational topology (ports) and environmental context (components)
- Explicit semantics enable better query patterns for compliance reporting

**Competency Question Coverage:**
- CQ3 (input sources): Can query "What river does this plant abstract from?" using wf:abstractsFrom
- CQ4 (downstream nodes): Can query "What ecosystem receives this discharge?" using wf:dischargesInto
- Enhanced separation of design questions (flowsTo) from environmental questions (dischargesInto)

### Date Completed
2026-01-28

---

## Phase 5: Conveyance System Expansion

*No issues logged yet*

---

## Phase 6: OWL-Time Simplification

*No issues logged yet*

---

## Phase 7: Usage Point Refinement

*No issues logged yet*

---

## Phase 8: Facility Definitions

*No issues logged yet*

---

## Phase 9: Fit-for-Purpose Framework

*No issues logged yet*

---

## Phase 10: Testing & Validation

*No issues logged yet*

---

## Decisions Log

### Format
```
## Decision #N: [Title]
- **Phase:** [Phase number]
- **Date:** [YYYY-MM-DD]
- **Context:** [Why this decision was needed]
- **Decision:** [What was decided]
- **Rationale:** [Why this approach was chosen]
- **Alternatives Considered:** [Other options]
```

---

## Commit Log

This section tracks commits made by each subagent during implementation.

### Phase 1: ENVO Verification
- *Commits will be logged here*

### Phase 2: BFO Alignment
- `feat(ontology): Phase 2 - fix BFO violation, separate material entities from processes` (2026-01-28)
  - Created new processes.ttl module with BFO-compliant process hierarchy
  - Renamed treatment units in material_entities.ttl to physical infrastructure names
  - Added wf:performsProcess property linking physical units to processes
  - Updated waterframe.ttl to import processes module
  - Updated WWTP instance files (wwtp1.ttl, wwtp2.ttl) with new classes and process links
  - Validated BFO compliance: 0 violations found

### Phase 3: WaWO+ Cleanup
- `refactor(ontology): Phase 3 - remove WaWO+ URIs, convert to textual comments` (2026-01-28)
  - Converted 36 WaWO+ rdfs:seeAlso URI references to textual rdfs:comment documentation
  - Modified material_entities.ttl (24 references), qualities.ttl (2 references), processes.ttl (10 references)
  - Preserved WaWO+ concept names as informational references with "(unpublished ontology)" notation
  - Validated removal: grep confirms 0 remaining WaWO+ URIs in ontology

### Phase 4: Property Relationships
- `feat(ontology): Phase 4 - add semantic connections between flow properties` (2026-01-28)
  - Created property hierarchy: dischargesToEnvironment → dischargesInto
  - Added wf:dischargesToEnvironment as generic environmental discharge property
  - Updated wf:dischargesInto as specialized subproperty for aquatic features
  - Enhanced wf:flowsTo comment to clarify distinction from environmental discharge
  - Moved property definitions from envo_alignment.ttl to properties.ttl
  - Created validation query: property_hierarchy_check.sparql
  - Documented design rationale and competency question coverage

### Phase 5: Conveyance System
- *Commits will be logged here*

### Phase 6: OWL-Time Simplification
- *Commits will be logged here*

### Phase 7: Usage Point Refinement
- *Commits will be logged here*

### Phase 8: Facility Definitions
- *Commits will be logged here*

### Phase 9: Fit-for-Purpose Framework
- *Commits will be logged here*

### Phase 10: Testing & Validation
- *Commits will be logged here*

---

## Notes

- All phases follow the clean break approach (prioritize correctness over backward compatibility)
- Each subagent is responsible for committing their work
- Validation should be performed after each phase when possible
