# Design Decisions

This document records key design decisions made during ontology development, following the format from `dev-resources/agent_builder.md`.

## Decision: ENVO Integration for Environmental Context

**Date**: 2026-01-27
**Module**: bridges/envo_alignment.ttl
**Based on**: research/ontologies/envo-2025-10-20/README_EVALUATION.md

**Rationale**: waterFRAME needed rich environmental context for water systems but lacked coverage of natural water bodies, ecosystems, and environmental processes. ENVO provides 77% coverage (9/13 full support) for environmental requirements. Integration enables queries like "which river does this plant discharge into?" and "what ecosystem does this affect?"

**Trade-off**:
- **Benefit**: Comprehensive environmental vocabulary (9,159 ENVO classes) without reinventing the wheel
- **Cost**: Added namespace dependency and need for ENVO awareness
- **Mitigation**: Lightweight reference approach (no full instance import)avoids performance overhead

**Impact**:
- CQ3 (input sources): Can now query natural water body sources with environmental classification
- CQ4 (downstream nodes): Can track environmental discharge destinations
- CQ10-11 (water quality): Link parameters to ENVO environmental quality descriptors
- CQ12 (compliance): Environmental context for compliance checking
- CQ14 (stream classification): Use ENVO water material types

**Implementation Details**:
1. Created `bridges/envo_alignment.ttl` with 14 new object properties
2. Added 6 new classes (`ContaminationEvent`, `Catchment`, `HydrologicalProcess`, `MonitoringPoint`, `UrbanWaterSystem`, `EnvironmentalQualityMeasurement`)
3. Semantic properties bridge waterFRAME and ENVO: `dischargesInto`, `abstractsFrom`, `locatedIn`, `hasWaterType`, etc.
4. Updated `waterframe.ttl` to import ENVO alignment
5. Updated Lieve River instance with ENVO classifications
6. Created comprehensive integration guide

**Layered Architecture Decision**:
Following ENVO evaluation recommendations:
- **Layer 1: ENVO** - Environmental context (water bodies, ecosystems, biomes, contamination)
- **Layer 2: SOSA/SSN** - Observation and sensor patterns (existing)
- **Layer 3: waterFRAME** - Treatment engineering, process models, computational agents
- **Layer 4: Domain-specific** - Detailed treatment processes (future: WaWO+)

Each layer provides complementary information without duplication.

**Key Design Pattern**: Property-Based Integration
- Avoids forcing waterFRAME classes into ENVO hierarchy
- Enables flexible instance-level linking
- Supports both structured (ENVO URIs) and descriptive (text) environmental context
- Example: `wf:WastewaterTreatmentPlant` remains waterFRAME, but `wf:dischargesInto envo:00000022` links it to ENVO river

**Validation Results**:
- ✓ Ontology remains consistent (409 triples)
- ✓ All competency question tests pass
- ✓ ENVO alignment module valid (146 triples)
- ✓ New properties properly defined
- ✓ Example instances updated successfully

**Open Questions**:
1. Should we create curated European water body instance library?
2. How to handle seasonal/temporal environmental variation?
3. Need inference rules for automatic environmental impact assessment?

**Next Steps**:
1. Integrate WaWO+ for detailed treatment processes (Layer 4)
2. Create extended SPARQL query library for environmental analysis
3. Develop reasoning rules for ecosystem impact inference
4. Add visualization tools for catchment-scale environmental context

---

## Decision: Synthetic Data Approach for Case Studies

**Date**: 2024-XX-XX (previous decision)
**Module**: case_studies/ghent/
**Rationale**: Real operational data for Ghent water systems unavailable. Synthetic but realistic data enables development and testing of ontology and agent framework.

**Trade-off**: Synthetic data lacks real-world complexity but provides controlled test environment with known ground truth.

**Impact**: Enables end-to-end testing of all competency questions and agent workflows.

---

## Decision: Port-Based Flow Modeling

**Date**: 2024-XX-XX (previous decision)
**Module**: properties.ttl
**Rationale**: Explicit ports enable clear flow topology, support multiple inputs/outputs, and facilitate model composition.

**Trade-off**: More verbose instance data vs. clearer semantics and better queryability.

**Impact**: CQ2, CQ3, CQ4, CQ5 (flow topology questions) now fully answerable.

---

## Decision: BFO Alignment

**Date**: 2024-XX-XX (previous decision)
**Rationale**: BFO provides upper-level structure for clear categorical distinction (materials vs. processes vs. qualities vs. information).

**Trade-off**: Added philosophical complexity vs. better interoperability and reasoning support.

**Impact**: Enables clear distinction between physical entities (tanks), processes (treatment), qualities (BOD), and information (models).

---

## Template for Future Decisions

```markdown
## Decision: [Short Title]

**Date**: YYYY-MM-DD
**Module**: filename.ttl
**Rationale**: [1-2 sentences on why this decision makes sense]

**Trade-off**:
- **Benefit**: [Key advantage]
- **Cost**: [Main downside]
- **Mitigation**: [How cost is addressed]

**Impact**: [Which CQs/capabilities this enables]

**Open Questions**: [Any remaining design issues]
```

---

**Changelog**:
- 2026-01-27: Added ENVO integration decision with comprehensive details
- Previous: BFO alignment, port-based modeling, synthetic data decisions (to be backfilled with dates)
