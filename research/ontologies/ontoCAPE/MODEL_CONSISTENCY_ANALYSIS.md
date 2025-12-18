# OntoCAPE Model Modules Consistency Analysis

**Date:** 2025-12-18
**Question:** Are OntoCAPE's mathematical model modules consistent and usable for waterFRAME?
**Answer:** ❌ **NO** - The model modules are inconsistent due to inherited issues from upper_level/system.owl

---

## Executive Summary

The `model/mathematical_model.owl` and `model/process_model.owl` modules, which are **critical for representing ASM/ADM models in waterFRAME**, **cannot be used directly** because they inherit OWL DL violations from their dependencies.

### Root Cause

The inconsistency originates in **`upper_level/system.owl`** where the `contains` property is declared as:
1. **`owl:TransitiveProperty`** (line ~77)
2. Used in **cardinality restrictions**

This combination violates OWL DL decidability and causes reasoner failure.

---

## Test Results

### Test Setup
- **Modules tested:** `model/mathematical_model.owl`, `model/process_model.owl`
- **Test instances:** 7 individuals (MathematicalModel, ProcessModel, ModelVariable, Parameter, System)
- **Reasoner:** Pellet 2.3.1

### Test Outcome
```
❌ INCONSISTENT
```

**Pellet errors:**
```
WARNING: Unsupported axiom: Invalid list structure: List does not have a rdf:first property
WARNING: Unsupported axiom: Invalid list structure: List does not have a rdf:rest property
WARNING: Ignoring transitivity axiom due to existing cardinality restriction for property contains
WARNING: Ignoring transitivity and/or complex subproperty axioms for contains
ERROR: Ontology is inconsistent
```

---

## Dependency Chain Analysis

```
model/mathematical_model.owl
    ↓ imports
upper_level/system.owl  ← ⚠️ CONTAINS THE BUG
    ↓ defines
TransitiveProperty "contains"
    ↓ used in
owl:Restriction with cardinality
    ↓ results in
OWL DL VIOLATION → Reasoner failure
```

### Import Dependencies

**`model/mathematical_model.owl`** imports:
- `upper_level/system.owl` ← **Source of inconsistency**

**`model/process_model.owl`** imports:
- `model/mathematical_model.owl`
- `chemical_process_system/chemical_process_system.owl`

**Therefore:** Loading model modules **necessarily loads the broken `contains` property**.

---

## The `contains` Property Issue

**Location:** `upper_level/system.owl` (lines ~77-80)

**Problematic axiom:**
```xml
<owl:Restriction>
  <owl:allValuesFrom rdf:resource="&system;#System"/>
  <owl:onProperty>
    <owl:TransitiveProperty rdf:ID="contains"/>
  </owl:onProperty>
</owl:Restriction>
```

**Why this is invalid:**
- OWL DL **forbids** transitive properties from having cardinality restrictions
- Reasoning over transitive + cardinality is **undecidable**
- Pellet correctly rejects this and marks the ontology inconsistent

---

## Implications for waterFRAME

### What You Need from OntoCAPE Model Modules

From the [MODULE_ARCHITECTURE_SUMMARY.md](MODULE_ARCHITECTURE_SUMMARY.md#module-13-modelMathematical_model):

1. **`MathematicalModel`** class - to represent ASM1, ADM1, BSM models
2. **`ModelVariable`** class - to represent state variables (Substrate_S, Biomass_X)
3. **`Parameter`** class - to represent kinetic parameters (μ_max, Y_yield, K_s)
4. **`models`** property - to link models to systems
5. **`hasModelVariable`**, **`hasParameter`** properties - to structure models

### Can You Use Them?

**Option 1: Direct import** ❌ **NOT POSSIBLE**
- Reasoner will fail
- Cannot guarantee logical consistency
- Query results may be incorrect

**Option 2: Fix the ontology** ⚠️ **POSSIBLE BUT REQUIRES CHANGES**
- Remove `owl:TransitiveProperty` from `contains` in `system.owl`
- OR remove cardinality restrictions using `contains`
- Then all downstream modules (including `model/`) become consistent

**Option 3: Extract patterns without importing** ✅ **RECOMMENDED**
- Manually recreate the class structure in waterFRAME ontology
- Copy class names, properties, and design patterns
- Don't use `owl:imports` - write your own axioms
- Avoids all OntoCAPE inconsistencies

---

## Recommended Solution for waterFRAME

### Strategy: Pattern Extraction (Not Import)

**DO:**
```turtle
# In waterframe.ttl - inspired by OntoCAPE but independent

@prefix wf: <http://ontology.waterframe.org/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

# Recreate the model classes WITHOUT importing OntoCAPE
wf:MathematicalModel a owl:Class ;
    rdfs:label "Mathematical model" ;
    rdfs:comment "A mathematical representation of a system. Adapted from OntoCAPE pattern." .

wf:ModelVariable a owl:Class ;
    rdfs:label "Model variable" ;
    rdfs:comment "A variable in a mathematical model (state, input, output)." .

wf:Parameter a owl:Class ;
    rdfs:label "Parameter" ;
    rdfs:comment "A constant parameter in a model." .

wf:models a owl:ObjectProperty ;
    rdfs:domain wf:MathematicalModel ;
    rdfs:range wf:System ;
    rdfs:label "models" .

wf:hasModelVariable a owl:ObjectProperty ;
    rdfs:domain wf:MathematicalModel ;
    rdfs:range wf:ModelVariable ;
    rdfs:label "has model variable" .

wf:hasParameter a owl:ObjectProperty ;
    rdfs:domain wf:MathematicalModel ;
    rdfs:range wf:Parameter ;
    rdfs:label "has parameter" .
```

**DON'T:**
```turtle
# This will fail due to inherited inconsistencies
@prefix ontocape: <file:///path/to/OntoCAPE/model/mathematical_model.owl#> .

wf:ASM1_Model a ontocape:MathematicalModel .  # ❌ Broken
```

### What to Extract from OntoCAPE

From the architecture analysis, these patterns are valuable:

1. **Function/Behavior/Realization/Performance separation**
   - Represent the same system from multiple viewpoints
   - Cleanly separates concerns

2. **Model structure:**
   ```
   MathematicalModel
     ├─ hasModelVariable → ModelVariable
     │    ├─ StateVariable
     │    ├─ InputVariable
     │    └─ OutputVariable
     ├─ hasParameter → Parameter
     └─ models → System
   ```

3. **Process model hierarchy:**
   ```
   ProcessModel (subclass of MathematicalModel)
     └─ models → ChemicalProcessSystem
   ```

4. **Units and quantities pattern:**
   ```
   ScalarQuantity
     ├─ numericalValue (xsd:double)
     └─ hasUnit → SI_Unit
   ```

### Integration with Other Ontologies

**Use these INSTEAD of OntoCAPE for consistency:**

| Need | Use This | Status |
|------|----------|--------|
| Units | **QUDT** | ✅ Well-maintained, consistent |
| Observations | **SOSA/SSN** | ✅ W3C standard, consistent |
| Chemical species | **ChEBI** or **PubChem RDF** | ✅ Active, well-curated |
| Model patterns | **Adapt OntoCAPE patterns** | ⚠️ Manually recreate |

---

## Verification Test

To confirm this analysis, run:

```bash
cd research/ontologies/ontoCAPE
uv run python test_model_consistency.py
```

**Expected output:**
```
❌ MODEL MODULES ARE INCONSISTENT
ERROR: Ontology is inconsistent
```

---

## Conclusion

### Can you use OntoCAPE's model modules?

**Answer:** No, not via `owl:imports`.

### What should you do?

1. **Extract the design patterns** (class structures, property relationships)
2. **Recreate them** in waterframe.ttl without importing
3. **Use consistent alternatives:**
   - QUDT for units
   - SOSA/SSN for observations
   - Custom classes for model metadata
4. **Add waterFRAME-specific extensions:**
   - Agent invocation metadata
   - Fit-for-purpose classification
   - Water quality standards

### What did you learn from OntoCAPE?

The **four-aspect decomposition** (Function/Behavior/Realization/Performance) and the **model metadata structure** are excellent patterns that can be adapted without inheriting the OWL DL violations.

---

## Next Steps

See the [competency questions coverage matrix](../../../data/competency_questions/coverage_matrix.md) to identify what waterFRAME needs beyond OntoCAPE patterns.

**Recommended workflow:**
1. ✅ OntoCAPE analysis complete
2. ⏭️ Analyze QUDT (quantities/units)
3. ⏭️ Analyze SOSA/SSN (observations)
4. ⏭️ Analyze WaWO (wastewater-specific)
5. ⏭️ Design waterFRAME ontology modules
6. ⏭️ Test against competency questions
