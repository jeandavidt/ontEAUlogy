# WaWO+ TBox/ABox Analysis - Executive Summary

**Date:** 2026-01-27
**Analyst:** ontEAUlogy project
**Full Report:** [TBox_ABox_Analysis.md](./TBox_ABox_Analysis.md)

---

## Purpose

Correct the previous evaluation of WaWO+ which claimed "WaWO+ cannot store water quality data" by:

1. Properly separating TBox (schema) from ABox (data)
2. Examining actual OWL files (not just paper descriptions)
3. Finding concrete examples of water quality measurements

---

## Key Findings

### 1. WaWO+ DOES Store Water Quality Data

**Pattern Used: Amount-based Measurements**

```turtle
:WaterMass_1 wawo:hasConcentration :BOD_measurement_1 .

:BOD_measurement_1 a wawo:BiochemicalOxygenDemand ;
    wawo:hasDataValue 272.0 ;
    wawo:hasUnit qu:milligramPerLitre .
```

**Key Properties:**

- `hasConcentration` (ObjectProperty): Links WaterMass → measurement instance
- `hasDataValue` (DatatypeProperty): Stores numerical value
- `hasUnit` (ObjectProperty): Links to QUDT unit

**Supported Measurements:**

- BiochemicalOxygenDemand (BOD)
- ChemicalOxygenDemand (COD)
- SuspendedSolid (SS)
- TotalNitrogen (TN)
- TotalPhosphorus (TP)
- Heavy metals (Arsenic, Cadmium, Aluminium, etc.)

### 2. Corrected Statistics

| Component | Count | Notes |
|-----------|-------|-------|
| **TBox Classes** | 298 | Schema definitions only |
| **TBox Object Properties** | 53 | Schema definitions only |
| **TBox Data Properties** | 1 | Only `hasDataValue` in upper TBox |
| **ABox Individuals** | 45+ | In wawo-core-abox.owl |
| **Girona ABox Measurements** | Hundreds | BOD, COD, metals, nutrients |

### 3. What Was Wrong with Previous Evaluation

1. **Relied on paper descriptions instead of actual OWL files**
   - Paper mentions properties like `biologicalOxygenDemandConcentration`
   - These **do not exist** in the actual TBox files
   - Actual implementation uses Amount pattern instead

2. **Did not separate TBox from ABox**
   - May have counted instances as classes
   - Confused schema with data

3. **Missed the Amount pattern**
   - Looked for direct data properties: `WaterMass → bodConcentration → float`
   - Actual pattern uses object properties: `WaterMass → hasConcentration → BOD instance`

---

## Concrete Examples from Girona WWTP

### Example 1: BOD Treatment Efficiency

```
Inlet:  272 mg/L BOD  (untreated wastewater)
Outlet:   3 mg/L BOD  (treated effluent)
Removal: 98.9%
```

### Example 2: COD Treatment Efficiency

```
Inlet:  467 mg/L COD
Outlet:  27 mg/L COD
Removal: 94.2%
```

### Example 3: Heavy Metals

```
Arsenic Inlet:  0.0021 mg/L
Arsenic Outlet: 0.0014 mg/L
Removal: 33.3%
```

---

## Pattern Comparison

### WaWO+ Pattern (Amount-based)

**Structure:**
```
WaterMass --hasConcentration--> MeasurementInstance
                                 ├── rdf:type: BiochemicalOxygenDemand
                                 ├── hasDataValue: 272.0
                                 └── hasUnit: qu:milligramPerLitre
```

**Pros:**
- ✓ Strong typing (measurement type = RDF class)
- ✓ Self-contained instances
- ✓ Easy to query by type
- ✓ Explicit units

**Cons:**
- ✗ Creates many instances
- ✗ Not standards-compliant (custom pattern)
- ✗ No temporal/provenance metadata

### WaterFrame Pattern (SOSA-based)

**Structure:**
```
WaterMass --isFeatureOfInterestOf--> Observation
                                     ├── observedProperty: BOD_property
                                     ├── hasSimpleResult: 272.0
                                     ├── unit: qu:MilliGM-PER-L
                                     ├── resultTime: timestamp
                                     └── madeBySensor: sensor_1
```

**Pros:**
- ✓ Standards-compliant (W3C SOSA/SSN)
- ✓ Built-in temporal support
- ✓ Built-in provenance
- ✓ Rich metadata model

**Cons:**
- ✗ More complex queries
- ✗ Requires traversing observation pattern

---

## Recommendations for WaterFrame

### Keep Current SOSA Pattern

WaterFrame's SOSA-based approach is **superior** for:
- Time-series sensor data
- Provenance tracking
- Standards compliance

### Consider Hybrid Enhancements

1. **Add water quality property taxonomy**
   ```turtle
   wf:BODProperty rdfs:subClassOf sosa:ObservableProperty .
   wf:CODProperty rdfs:subClassOf sosa:ObservableProperty .
   ```

2. **Define convenience patterns** for common queries
   ```sparql
   # Shortcut property path
   wf:hasSimpleBODValue owl:propertyChainAxiom (
       sosa:hasObservation
       [sosa:observedProperty wf:BODProperty]
       sosa:hasSimpleResult
   ) .
   ```

3. **Document query patterns** for users
   - Provide example SPARQL queries
   - Create query helper functions

---

## Sample SPARQL Queries

### Query 1: Find all BOD measurements in WaWO+

```sparql
PREFIX wawo: <http://kemlg.upc.edu/wawo-core-tbox#>
PREFIX wawo-upper: <http://kemlg.upc.edu/wawo-upper-tbox#>

SELECT ?waterMass ?bodValue ?unit
WHERE {
  ?waterMass a wawo:WaterMass ;
             wawo:hasConcentration ?bodMeasurement .
  ?bodMeasurement a wawo:BiochemicalOxygenDemand ;
                  wawo-upper:hasDataValue ?bodValue ;
                  wawo-upper:hasUnit ?unit .
}
```

### Query 2: Calculate WWTP treatment efficiency

```sparql
PREFIX wawo: <http://kemlg.upc.edu/wawo-core-tbox#>
PREFIX wawo-upper: <http://kemlg.upc.edu/wawo-upper-tbox#>

SELECT ?parameter ?inletValue ?outletValue
       ((?inletValue - ?outletValue) / ?inletValue * 100 AS ?removalPercent)
WHERE {
  ?wwtp a wawo:WasteWaterTreatmentPlant .

  ?wwtp wawo:receives ?inletWater .
  ?inletWater wawo:hasConcentration ?inletMeasurement .
  ?inletMeasurement a ?parameter ;
                    wawo-upper:hasDataValue ?inletValue .

  ?wwtp wawo:discharges ?outletWater .
  ?outletWater wawo:hasConcentration ?outletMeasurement .
  ?outletMeasurement a ?parameter ;
                     wawo-upper:hasDataValue ?outletValue .

  FILTER(?parameter IN (wawo:BiochemicalOxygenDemand, wawo:ChemicalOxygenDemand))
}
```

---

## Conclusion

**Original Claim:** "WaWO+ cannot store water quality data"

**Corrected Understanding:** WaWO+ stores water quality data using a **typed Amount pattern** with:
- Object properties linking to measurement instances
- Strong typing via RDF classes (BOD, COD, SS, etc.)
- Explicit unit references to QUDT
- Hundreds of actual measurements in Girona ABox

**Lesson Learned:** Always examine actual ontology files, not just papers. Properly separate TBox (schema) from ABox (data) when evaluating ontologies.

**For WaterFrame:** The SOSA pattern is more appropriate for sensor-based water quality monitoring. Consider adding water quality property taxonomy and query convenience features.

---

## Files Generated

1. **`analyze_tbox_abox.py`** - Python script using rdflib to:
   - Load TBox files separately from ABox files
   - Count classes, properties, axioms
   - Investigate SSN/QUDT patterns
   - Find concrete examples

2. **`TBox_ABox_Analysis.md`** - Full detailed report (608 lines) with:
   - Complete statistics
   - Concrete examples from Girona ABox
   - SPARQL query examples
   - Pattern comparisons
   - Recommendations for WaterFrame

3. **`ANALYSIS_SUMMARY.md`** (this file) - Executive summary

---

**End of Summary**
