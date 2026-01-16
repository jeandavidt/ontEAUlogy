# waterFRAME Design Decisions

This document records key design decisions made during ontology development, following the format from `dev-resources/agent_builder.md`.

---

## Decision: Sampling Metadata Module

**Date**: 2025-01-16
**Module**: modules/sampling.ttl
**Rationale**: Regulatory compliance requires explicit representation of sampling context (who, what, where, when, how). WHOKG patterns adapted to BFO alignment.
**Trade-off**: Additional complexity for simple observations; full sampling metadata may not always be needed.
**Impact**: Enables CQ12 (compliance checking), chain of custody tracking, supports any jurisdiction's sampling requirements.

**Key classes**:
- `WaterSample` - physical sample linked to observations
- `SamplingPoint` - designated collection location (influent/effluent/process/ambient)
- `SamplingMethod` - grab, composite (time/flow), automated, continuous
- `FlowDirection` - influent/effluent/process/bypass context
- `DischargePoint` - regulatory discharge location
- `DischargeMeasurement` - flow rate for load calculations

---

## Decision: Compliance Status Module

**Date**: 2025-01-16
**Module**: modules/compliance.ttl
**Rationale**: Explicit compliance status representation enables automated compliance tracking and violation reporting. Required for regulatory use cases.
**Trade-off**: Compliance status requires linkage to observations and requirements; adds inference overhead.
**Impact**: Enables CQ12 (compliance checking), violation tracking, supports multi-jurisdiction compliance verification.

**Key classes**:
- `ComplianceStatus` - Compliant/NonCompliant/PendingReview/NotApplicable
- `ComplianceCheck` - verification event linking observation to requirement
- `ViolationRecord` - documented violation with severity and amount
- `LoadCalculation` - concentration x flow for load-based limits

---

## Decision: Generalized Limit Types

**Date**: 2025-01-16
**Module**: modules/compliance.ttl
**Rationale**: Different jurisdictions use different limit types. USEPA distinguishes TBEL vs WQBEL; many jurisdictions use load-based limits.
**Trade-off**: More limit type subclasses; user must select appropriate type.
**Impact**: Enables multi-jurisdiction support (EU, USEPA, WHO, etc.) without ontology changes.

**Key classes**:
- `TechnologyBasedLimit` (TBEL)
- `WaterQualityBasedLimit` (WQBEL)
- `ConcentrationLimit` (mg/L, ug/L)
- `LoadLimit` (kg/day, lbs/day)
- `PercentRemovalLimit`
- Averaging periods: Daily/Weekly/Monthly/Annual

---

## Decision: Flow Direction as Class (not Property)

**Date**: 2025-01-16
**Module**: modules/sampling.ttl
**Rationale**: Flow direction (influent/effluent) is a key regulatory context. Modeling as class allows for reasoning and extension.
**Trade-off**: Requires explicit assignment vs. inference from port direction.
**Impact**: Simplifies regulatory queries; explicit context for observations.

**Open question**: Should flow direction be inferred from port connections? Current approach: explicit assignment for regulatory clarity.

---

## Decision: Violation Severity Classification

**Date**: 2025-01-16
**Module**: modules/compliance.ttl
**Rationale**: Different violations require different responses. Severity classification enables prioritization.
**Trade-off**: Severity assessment may be subjective; thresholds vary by jurisdiction.
**Impact**: Supports violation triage and response planning.

**Classes**: Minor/Moderate/Serious/Critical

---

## Decision: Load Calculation as Process

**Date**: 2025-01-16
**Module**: modules/compliance.ttl
**Rationale**: Load calculations combine concentration and flow measurements. Modeling as process captures the derivation relationship.
**Trade-off**: Adds indirection; alternative would be direct load property on observation.
**Impact**: Enables traceability of load values to source data; supports load-based limit compliance.

**Pattern**: `LoadCalculation` → `fromConcentration` → `WaterQualityObservation`
                          → `fromFlowMeasurement` → `DischargeMeasurement`

---

## Module Import Structure

```
waterframe.ttl (main)
├── modules/core/material_entities.ttl
│   └── imports: BFO
├── modules/core/properties.ttl
│   └── imports: material_entities
├── modules/information.ttl
│   └── imports: material_entities
├── modules/capabilities.ttl
│   └── imports: information
├── modules/qualities.ttl
│   └── imports: material_entities
├── modules/sampling.ttl (NEW)
│   └── imports: material_entities
└── modules/compliance.ttl (NEW)
    └── imports: qualities, sampling
```

---

## CQ Coverage Impact

| CQ | Before | After | Notes |
|----|--------|-------|-------|
| CQ10 | Partial | Full | Water quality parameters |
| CQ11 | Partial | Full | Regulatory limits with types |
| CQ12 | Missing | Full | Compliance checking |
| CQ13 | Missing | Partial | Contaminants above threshold |
| CQ35 | Missing | Full | Source of regulatory limits |

---

## Future Work

1. **SOSA Bridge**: Align `WaterQualityObservation` with SOSA for broader interoperability
2. **PROV-O Bridge**: Add provenance tracking for compliance audit trail
3. **Permit Module**: Model regulatory permits with conditions and schedules
4. **Spatial Module**: Add geospatial coordinates for sampling points and discharge locations
