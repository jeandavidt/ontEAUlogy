# Household Case Study — Missing Ontology Concepts

This document records ontology gaps discovered during implementation of the
household case study model services. Gaps are categorised as either
**already present** (verified in `data/ontology/`) or **missing** (needs
addition to the ontology).

---

## Treatment Unit Classes

| Concept | IRI | Status | Notes |
|---------|-----|--------|-------|
| `wf:MembraneBioreactorUnit` | `wf:MembraneBioreactorUnit` | ✅ Present | Used in `household_case1.ttl` line 71 |
| `wf:ReverseOsmosisUnit` | `wf:ReverseOsmosisUnit` | ✅ Present | Used in `household_case1.ttl` line 75 |
| `wf:InfiltrationUnit` | `wf:InfiltrationUnit` | ✅ Present | Used in `household_case1.ttl` line 79 |

---

## Flow Type Properties & Individuals

| Concept | Status | Notes |
|---------|--------|-------|
| `wf:hasFlowType` | ✅ Present | Used extensively in `household_case1.ttl` |
| `wf:hasFlowDirection` | ✅ Present | Used in `household_case1.ttl` |
| `wf:GreywaterFlow` | ✅ Present | `household_case1.ttl` lines 100–121 |
| `wf:BlackwaterFlow` | ✅ Present | `household_case1.ttl` line 126 |
| `wf:RainwaterFlow` | ✅ Present | `household_case1.ttl` lines 166–179 |
| `wf:ReclaimedWaterFlow` | ✅ Present | `household_case1.ttl` lines 130, 139–157 |
| `wf:PotableWaterFlow` | ✅ Present | `household_case1.ttl` line 188 |
| `wf:UnidirectionalFlow` | ✅ Present | Used as `wf:hasFlowDirection` value |
| `wf:ConditionalFlow` | ✅ Present | Used as `wf:hasFlowDirection` value |
| `wf:OverflowFlow` | ✅ Present | `household_case1.ttl` line 162 |

---

## Storage Tank Subclasses

| Concept | Status | Notes |
|---------|--------|-------|
| `wf:RainwaterStorageTank` | ✅ Present | `household_case1.ttl` line 54 |
| `wf:BlackwaterStorageTank` | ✅ Present | `household_case1.ttl` line 68 |
| `wf:PurifiedGreywaterStorageTank` | ✅ Present | `household_case1.ttl` line 62 |
| `wf:PotableWaterStorageTank` | ✅ Present | `household_case1.ttl` line 58 |

---

## QSDsan Unit Gaps

### Gap INF-01: No native Infiltration SanUnit in QSDsan

**Severity:** Medium
**Affects:** `infiltration.py` model service

QSDsan (≥1.3.0) does not provide a `SanUnit` subclass for subsurface soil
infiltration systems. The closest available units are `Lagoon` and `Septic`,
neither of which accurately represents managed soil infiltration.

**Workaround implemented:** A first-order removal model was implemented using
literature-based removal fractions (Crites & Tchobanoglous, *Small and
Decentralized Wastewater Management Systems*):

- COD removal: 70%
- TSS removal: 90% (physical filtration dominant)
- NH4-N removal: 55% (nitrification in soil, high variance)

**Recommended fix:** Submit a `SoilInfiltration` or `VerticallySaturatedFlowWetland`
SanUnit to QSDsan upstream, or maintain this custom analytical unit in the
household package until upstream support is added.

---

### Gap INF-02: QSDsan MembraneBioreactor SanUnit parameter scope

**Severity:** Low
**Affects:** `mbr.py` model service

The QSDsan `MembraneBioreactor` SanUnit is designed for municipal-scale
systems (typical design capacity 10,000–100,000 m³/d). The household MBR
operates at 1–5 m³/d. Default kinetic parameters (HRT, SRT, MLSS) need
rescaling for decentralised household use.

**Workaround:** Implemented as an analytical mass-balance model with
household-appropriate removal efficiencies. Full QSDsan integration with
custom kinetic parameters is deferred to a future iteration.

---

## ModelVariable Subclass Gaps

The following QSDsan/simulation parameters have no matching `wf:ModelVariable`
subclass in the current ontology:

| Parameter | Suggested class | Module to extend |
|-----------|----------------|-----------------|
| `recovery_fraction` (RO/MBR) | `wf:WaterRecoveryFraction` | `agents.ttl` or new `variables.ttl` |
| `removed_cod_fraction` | `wf:PollutantRemovalFraction` | same |
| `sludge_kg_d` | `wf:SludgeProduction` | same |
| `permeate_tds_mg_l` | `wf:DissolvedSolidsConcentration` | core properties |
| `feed_conductivity_us_cm` | `wf:WaterConductivity` | core properties |

These are non-blocking; the services function correctly with `wf:ModelOutput`
as the base class.

---

## Summary

All **treatment unit classes**, **flow type properties**, **flow type individuals**,
and **storage tank subclasses** referenced in `household_case1.ttl` are already
present in the ontology.

Two QSDsan-level gaps (INF-01, INF-02) required custom implementations. Five
`wf:ModelVariable` subclass gaps are deferred enhancements.
