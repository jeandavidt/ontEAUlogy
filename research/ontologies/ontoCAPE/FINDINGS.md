# OntoCAPE Consistency Analysis

**Date:** 2025-12-17

## Summary

OntoCAPE is **logically inconsistent** when tested with instances. The ontology loads successfully but contains OWL DL violations that cause reasoner failures.

## Test Configuration

- **Fixed import paths:** Created [OntoCAPE_fixed](OntoCAPE_fixed/) with corrected file:// URIs
- **Modules loaded:** system.owl, substance.owl, process.owl
- **Test instances:** 4 individuals (2× System, 2× ChemicalSpecies)
- **Reasoner:** Pellet 2.3.1

## Identified Issues

### 1. Transitivity + Cardinality Conflict (CRITICAL)
**Property:** `contains`
**Location:** Likely in `upper_level/system.owl` or `upper_level/network_system.owl`

The `contains` property is declared as:
- `owl:TransitiveProperty` AND
- Subject to cardinality restrictions

**Problem:** This violates OWL DL decidability. Transitive properties cannot have cardinality restrictions.

**Pellet output:**
```
WARNING: Ignoring transitivity axiom due to existing cardinality restriction for property contains
WARNING: Ignoring transitivity and/or complex subproperty axioms for contains
ERROR: Ontology is inconsistent
```

### 2. Malformed RDF Lists
**Severity:** High
**Location:** Unknown - requires investigation

Multiple axioms use invalid RDF list structures:
```
WARNING: Invalid list structure: List does not have a rdf:rest property
WARNING: Invalid list structure: List does not have a rdf:first property
```

Likely in class restrictions or property chains.

### 3. Cyclic Subclass
**Class:** `StoichiometricCoefficient`
**Location:** `material/substance/reaction_mechanism.owl`
**Severity:** Low (warning only)

## Module Load Status

✅ **Successfully loaded:** 64/64 OWL files
✅ **Import resolution:** All imports resolve correctly
❌ **Consistency check:** FAILED

## Files Created

- [`fix_imports.py`](fix_imports.py) - Corrects Windows paths → creates OntoCAPE_fixed/
- [`test_import_loading.py`](test_import_loading.py) - Verifies module loading (21/21 passed)
- [`test_with_created_instances.py`](test_with_created_instances.py) - Consistency test with instances (FAILED)

## Actionable Next Steps

### Priority 1: Locate `contains` property conflict
```bash
grep -r "contains" OntoCAPE_fixed/upper_level/*.owl
grep -r "TransitiveProperty" OntoCAPE_fixed/upper_level/*.owl
grep -r "cardinality" OntoCAPE_fixed/upper_level/*.owl
```

### Priority 2: Fix options
**Option A:** Remove transitivity from `contains`
**Option B:** Remove cardinality restrictions on `contains`
**Option C:** Create separate property for transitive relationship

### Priority 3: Test modular consistency
Run layer-by-layer tests to isolate which modules can be used independently:
- Upper level only
- Upper + supporting concepts
- Material domain only
- Process system only

## Implications for waterFRAME

**Cannot use OntoCAPE as-is** - reasoner will fail on any consistency check.

**Options:**
1. Fix the identified issues (requires OWL editing)
2. Use only conflict-free modules (requires isolation testing)
3. Extract patterns/classes without importing the ontology
4. Use alternative ontologies (QUDT, SOSA/SSN, WaWO)

## Test Reproduction

```bash
cd research/ontologies/ontoCAPE
uv run python fix_imports.py
uv run python test_with_created_instances.py
```

Expected output: `❌ ONTOLOGY IS INCONSISTENT`
