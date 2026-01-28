# WaWO+ TBox/ABox Analysis Report

**Analysis Date:** 2026-01-27
**Purpose:** Correct previous evaluation of WaWO+ water quality measurement capabilities

---

## Executive Summary

This report provides a corrected analysis of the WaWO+ ontology by properly separating:
- **TBox** (Terminology/Schema): Class definitions, property definitions, axioms
- **ABox** (Assertions/Instances): Actual data instances and their property values

### Key Findings

1. **TBox Statistics (Corrected)**:
   - Classes: 298
   - Object Properties: 53
   - Data Properties: 1

2. **ABox Statistics**:
   - Total Individuals: 45
   - Classes Instantiated: 13

3. **Water Quality Measurement Patterns**:
   - Direct data properties: 0 found
   - SSN Observation support: Minimal
   - QUDT Amount support: Yes

---

## 1. TBox Analysis (Schema Only)

### 1.1 Component Counts

| Component | Count |
|-----------|-------|
| Classes | 298 |
| Object Properties | 53 |
| Data Properties | 1 |
| Annotation Properties | 5 |

### 1.2 Sample Classes

**Top-level classes found in TBox:**

- `BiologicalFeature`
- `Cadmium`
- `CentrifugeSurfaceWaterTreatmentEquipment`
- `DairyIndustrialActivity`
- `DesandingTreatment`
- `DigestionSludgeLineTreatment`
- `EmergingContaminantIndicatorParameter`
- `HouseholdWasteWater`
- `MeteorologicalPattern`
- `Naproxen`
- `Runoff`
- `Selenium`
- `Spillway`
- `SuspendedSolid`
- `TotalNitrogen`
- `TotalPhosphorus`
- `TreatedWasteWater`
- `WasteWaterTreatmentStep`
- `WaterTreatmentEfficiency`
- `XRayContrastMedia`

### 1.3 Axiom Statistics

| Axiom Type | Count |
|------------|-------|
| disjointWith | 2 |
| domain | 14 |
| equivalentClass | 11 |
| range | 25 |
| subClassOf | 312 |
| subPropertyOf | 15 |

---

## 2. ABox Analysis (Instances Only)

### 2.1 Instance Counts

- **Total Named Individuals**: 45
- **Classes with Instances**: 13

### 2.2 Most Populated Classes

| Class | Instance Count |
|-------|----------------|
| `RunoffCoefficient` | 17 |
| `AnnotationProperty` | 6 |
| `DrivesAndWalksLandUse` | 6 |
| `Ontology` | 5 |
| `GreenAreaLandUse` | 4 |
| `Literal` | 4 |
| `AgriculturalLandUse` | 3 |
| `UrbanLandUse` | 3 |
| `LandUse` | 2 |
| `AllDifferent` | 2 |
| `IndustrialLandUse` | 1 |
| `Surface` | 1 |
| `Polygon` | 1 |

---

## 3. Water Quality Measurement Patterns

### 3.1 Pattern A: QUDT Amount Pattern (PRIMARY METHOD)

**WaWO+ uses the Amount pattern as the PRIMARY method for water quality measurements.**

This pattern was initially discovered but underestimated. Manual inspection of the Girona ABox reveals:

**Structure:**
```
WaterMass --hasConcentration--> ConcentrationAmount (instance of BiochemicalOxygenDemand)
                                 |
                                 +--hasDataValue--> xsd:decimal (272)
                                 |
                                 +--hasUnit--> qu:milligramPerLitre
```

**Key Properties:**

- `hasConcentration` (ObjectProperty): Links WaterMass to measurement instances
- `hasDataValue` (DatatypeProperty): Stores the numerical value
- `hasUnit` (ObjectProperty): Links to QUDT unit instances

**Measurement Classes** (subclasses of ChemicalIndicatorParameter):

- `BiochemicalOxygenDemand` (BOD)
- `ChemicalOxygenDemand` (COD)
- `SuspendedSolid` (SS)
- `TotalNitrogen` (TN)
- `TotalPhosphorus` (TP)
- Heavy metals (Aluminium, Arsenic, Cadmium, etc.)

### 3.2 Pattern B: Direct Data Properties

**WaWO+ does NOT use direct data properties** like `biologicalOxygenDemandConcentration: xsd:float`.

Instead, each measurement is a **typed instance** (e.g., instance of BiochemicalOxygenDemand class) that:

1. Represents the measurement type through its class
2. Stores the value via `hasDataValue`
3. Specifies units via `hasUnit`

### 3.3 Pattern C: SSN Observation Pattern

WaWO+ imports SSN but uses it minimally in the provided ABox files. The primary measurement pattern is the Amount/Concentration pattern described above.

---

## 4. Concrete Examples from Girona ABox

**Manual extraction from girona-abox.owl (file has parsing issues but contains valid data)**

### 4.1 Example: BOD Measurement at WWTP Inlet

```xml
<!-- Declaration -->
<Declaration>
    <NamedIndividual IRI="#BODinEDAR"/>
</Declaration>

<!-- Type: This is a BOD measurement -->
<ClassAssertion>
    <Class IRI="http://kemlg.upc.edu/wawo-core-tbox#BiochemicalOxygenDemand"/>
    <NamedIndividual IRI="#BODinEDAR"/>
</ClassAssertion>

<!-- Numerical value: 272 mg/L -->
<DataPropertyAssertion>
    <DataProperty IRI="http://kemlg.upc.edu/wawo-upper-tbox#hasDataValue"/>
    <NamedIndividual IRI="#BODinEDAR"/>
    <Literal datatypeIRI="http://www.w3.org/2001/XMLSchema#decimal">272</Literal>
</DataPropertyAssertion>

<!-- Unit: milligrams per litre -->
<ObjectPropertyAssertion>
    <ObjectProperty IRI="http://kemlg.upc.edu/wawo-upper-tbox#hasUnit"/>
    <NamedIndividual IRI="#BODinEDAR"/>
    <NamedIndividual IRI="http://purl.oclc.org/NET/ssnx/qu/unit#milligramPerLitre"/>
</ObjectPropertyAssertion>
```

**Interpretation:**

- Instance name: `BODinEDAR` (BOD at EDAR/WWTP inlet)
- Measurement type: `BiochemicalOxygenDemand` (via rdf:type)
- Value: `272` (mg/L)
- Unit: QUDT unit `milligramPerLitre`

### 4.2 Example: COD Measurements (Inlet vs Outlet)

#### Inlet (untreated wastewater)


```xml
<ClassAssertion>
    <Class IRI="http://kemlg.upc.edu/wawo-core-tbox#ChemicalOxygenDemand"/>
    <NamedIndividual IRI="#CODinEDAR"/>
</ClassAssertion>
<DataPropertyAssertion>
    <DataProperty IRI="http://kemlg.upc.edu/wawo-upper-tbox#hasDataValue"/>
    <NamedIndividual IRI="#CODinEDAR"/>
    <Literal datatypeIRI="http://www.w3.org/2001/XMLSchema#decimal">467</Literal>
</DataPropertyAssertion>
```

#### Outlet (treated wastewater)

```xml
<ClassAssertion>
    <Class IRI="http://kemlg.upc.edu/wawo-core-tbox#ChemicalOxygenDemand"/>
    <NamedIndividual IRI="#CODoutEDAR"/>
</ClassAssertion>
<DataPropertyAssertion>
    <DataProperty IRI="http://kemlg.upc.edu/wawo-upper-tbox#hasDataValue"/>
    <NamedIndividual IRI="#CODoutEDAR"/>
    <Literal datatypeIRI="http://www.w3.org/2001/XMLSchema#decimal">27</Literal>
</DataPropertyAssertion>
```

**Treatment Efficiency:** 467 → 27 mg/L (94.2% removal)

### 4.3 Example: Heavy Metal Measurements

```xml
<!-- Arsenic at inlet: 0.0021 mg/L -->
<ClassAssertion>
    <Class IRI="http://kemlg.upc.edu/wawo-core-tbox#Arsenic"/>
    <NamedIndividual IRI="#ArsenicIn"/>
</ClassAssertion>
<DataPropertyAssertion>
    <DataProperty IRI="http://kemlg.upc.edu/wawo-upper-tbox#hasDataValue"/>
    <NamedIndividual IRI="#ArsenicIn"/>
    <Literal datatypeIRI="http://www.w3.org/2001/XMLSchema#decimal">0.0021</Literal>
</DataPropertyAssertion>

<!-- Arsenic at outlet: 0.0014 mg/L -->
<DataPropertyAssertion>
    <DataProperty IRI="http://kemlg.upc.edu/wawo-upper-tbox#hasDataValue"/>
    <NamedIndividual IRI="#ArsenicOut"/>
    <Literal datatypeIRI="http://www.w3.org/2001/XMLSchema#decimal">0.0014</Literal>
</DataPropertyAssertion>
```

### 4.4 Summary of Found Measurements in Girona ABox

| Parameter | Inlet Value | Outlet Value | Unit | Removal % |
|-----------|-------------|--------------|------|-----------|
| BOD | 272 | 3 | mg/L | 98.9% |
| COD | 467 | 27 | mg/L | 94.2% |
| Arsenic | 0.0021 | 0.0014 | mg/L | 33.3% |
| Cadmium | 0.001 | 0.001 | mg/L | 0% |
| Aluminium | 0.02 | 0.056 | mg/L | -180% (increased) |
| Ammonium | 0.2 | 0.2 | mg/L | 0% |
| Chloride | 24 | (not shown) | mg/L | - |

---

## 5. Correction to Previous Evaluation

### 5.1 Original Claim

> "WaWO+ cannot store water quality data"

### 5.2 Corrected Understanding

**WaWO+ DOES support water quality data storage through the Amount/Concentration pattern:**

#### The ACTUAL Pattern Used

1. **Typed Amount Instances** (Primary and Only Method Found)
   - Each measurement is an instance of a specific measurement class
   - Classes: `BiochemicalOxygenDemand`, `ChemicalOxygenDemand`, `SuspendedSolid`, etc.
   - Linked to WaterMass via `hasConcentration` object property
   - Value stored via `hasDataValue` data property
   - Units specified via `hasUnit` object property → QUDT units
   - ✓ Strongly typed: each measurement knows its own type
   - ✓ Extensible: new measurement types = new classes
   - ✓ Unit-aware: explicit QUDT unit references

2. **NOT Used: Direct Data Properties**
   - The paper mentions properties like `biologicalOxygenDemandConcentration`
   - **These do not appear in the actual TBox files**
   - The reverse-engineered spec was based on paper descriptions, not actual OWL files
   - Actual implementation uses the Amount pattern instead

3. **Minimal SSN Usage**
   - SSN is imported but not heavily used in the ABox files examined
   - The Amount pattern serves as the primary measurement representation

### 5.3 Why the Previous Evaluation Was Incomplete

The previous evaluation had several issues:

1. **Relied on paper descriptions, not actual OWL files**
   - The reverse-engineered spec documented properties mentioned in the paper
   - The actual TBox files implement a different pattern
   - Lesson: Always examine the actual ontology files, not just papers

2. **Confused schema with data**
   - May have counted ABox instances as classes
   - Did not distinguish between TBox (298 classes) and ABox (individual measurements)

3. **Missed the Amount pattern**
   - Looked for direct data properties like `biologicalOxygenDemandConcentration: float`
   - Actual pattern uses `hasConcentration: BiochemicalOxygenDemand` (object property)
   - Each measurement is a typed instance with `hasDataValue` and `hasUnit`

**This analysis correctly separates:**

- **TBox**: Schema definitions (classes, properties, constraints)
- **ABox**: Actual data (individual water bodies, measurements, observations)

---

## 6. Comparison: WaWO+ vs WaterFrame

### 6.1 Water Quality Measurement Capabilities

| Aspect | WaWO+ (Actual) | WaterFrame (Current) |
|--------|----------------|----------------------|
| Measurement representation | Typed Amount instances | SOSA Observations |
| Property linking | `hasConcentration` (object) | `sosa:observedProperty` |
| Value storage | `hasDataValue` (data property) | `sosa:hasSimpleResult` or `qudt:value` |
| Unit handling | `hasUnit` → QUDT units | QUDT directly |
| Measurement types | Specific classes (BOD, COD, SS, TN, TP, etc.) | Generic ObservableProperty |
| Typing strength | ✓ Strong (class-based) | ✓ Strong (property-based) |

### 6.2 Pattern Comparison

#### WaWO+ Pattern (Amount-based)

```turtle
:WaterMass_1 wawo:hasConcentration :BOD_measurement_1 .
:BOD_measurement_1 rdf:type wawo:BiochemicalOxygenDemand ;
                   wawo:hasDataValue 272.0 ;
                   wawo:hasUnit qu:milligramPerLitre .
```

**Pros:**

- Measurement type is the RDF type (easy to query all BOD measurements)
- Self-contained: each measurement knows its type, value, and unit
- Extensible: add new measurement types by creating new classes

**Cons:**

- Creates many instances (one per measurement)
- Less standard (not using SSN/SOSA)
- No built-in temporal or provenance metadata

#### WaterFrame Pattern (SOSA-based)

```turtle
:WaterMass_1 sosa:isFeatureOfInterestOf :Observation_1 .
:Observation_1 rdf:type sosa:Observation ;
               sosa:observedProperty :BOD_property ;
               sosa:hasSimpleResult "272.0"^^xsd:float ;
               qudt:unit qu:MilliGM-PER-L ;
               sosa:resultTime "2024-01-15T10:00:00Z"^^xsd:dateTime ;
               sosa:madeBySensor :Sensor_1 .
```

**Pros:**

- Standards-compliant (SOSA/SSN)
- Built-in temporal and provenance support
- Sensor/procedure tracking
- Rich metadata model

**Cons:**

- More complex query patterns (need to traverse observation → property)
- Requires defining observable properties separately

### 6.3 Recommendations for WaterFrame

**Keep the SOSA pattern but consider hybrid approach:**

1. **Define specific water quality property classes**
   - Create subclasses of `ObservableProperty` for BOD, COD, SS, etc.
   - Allows querying by property type: `?prop a wf:BODProperty`

2. **Leverage both patterns**
   - Use SOSA for time-series sensor data (with provenance)
   - Consider Amount pattern for static/reference water quality values
   - Provide convenience properties for common queries

3. **Explicit measurement type hierarchy**
   - Create taxonomy of water quality parameters
   - Link to standard measurement methods (e.g., EPA methods)

4. **Query convenience**
   - Define property chains or shortcuts for common patterns
   - Example: `hasSimpleBODValue` as shortcut for observation pattern

---

## 7. Conclusions

### 7.1 Key Takeaways

1. **TBox/ABox separation is critical** for accurate ontology evaluation
   - WaWO+ TBox has **298 classes** (schema only)
   - ABox has **45 individuals** in wawo-core-abox.owl
   - Girona ABox has hundreds of measurement instances

2. **WaWO+ DOES support water quality measurements** through the Amount pattern
   - Each measurement is a typed instance (e.g., `BiochemicalOxygenDemand`)
   - Values stored via `hasDataValue` data property
   - Units via `hasUnit` object property to QUDT units
   - Pattern is **not** direct data properties as paper suggested

3. **Papers can be misleading**
   - The published paper describes properties that don't exist in the actual OWL
   - Always examine actual ontology files, not just documentation
   - Reverse-engineering from papers can introduce errors

4. **Both WaWO+ and WaterFrame are viable** but use different patterns
   - WaWO+: Class-based typing of measurements (Amount instances)
   - WaterFrame: SOSA Observation pattern with temporal/provenance support
   - Each has trade-offs in query complexity vs. expressiveness

### 7.2 Lessons for WaterFrame Development

#### What WaWO+ Does Well

- **Strong typing**: Measurement types are classes, enabling class-based queries
- **Self-contained**: Each measurement carries its type, value, and unit
- **Specific water quality vocabulary**: BOD, COD, SS, TN, TP, heavy metals
- **QUDT integration**: Explicit unit references

#### What WaterFrame Does Better

- **Standards compliance**: Uses SOSA/SSN (W3C standards)
- **Temporal modeling**: Built-in time support via `resultTime`, `phenomenonTime`
- **Provenance tracking**: Sensors, procedures, observers
- **Flexibility**: Generic observation model works for any measurement

#### Recommended Hybrid Approach for WaterFrame

1. **Keep SOSA as primary pattern** (for temporal sensor data)
2. **Add water quality property taxonomy**
   - Define specific `ObservableProperty` subclasses for BOD, COD, etc.
   - Enables property-based queries: `?prop a wf:BODProperty`
3. **Create convenience patterns** for static reference values
4. **Document query patterns** for common use cases

### 7.3 Corrected Understanding

**Original Claim:** "WaWO+ cannot store water quality data"

**Reality:** WaWO+ stores water quality data using typed Amount instances with:

- `hasConcentration` linking WaterMass to measurement instances
- Measurement instances typed by class (BiochemicalOxygenDemand, etc.)
- `hasDataValue` for numerical values
- `hasUnit` for QUDT unit references

**The confusion arose from:**

- Relying on paper descriptions instead of actual OWL files
- Not properly separating TBox (schema) from ABox (data)
- Looking for wrong pattern (direct data properties instead of Amount instances)

---

## Appendix A: SPARQL Query Examples

### Query 1: Find all WaterMass instances with BOD measurements (CORRECTED)

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

### Query 2: Find all BOD measurements regardless of WaterMass

```sparql
PREFIX wawo: <http://kemlg.upc.edu/wawo-core-tbox#>
PREFIX wawo-upper: <http://kemlg.upc.edu/wawo-upper-tbox#>

SELECT ?bodMeasurement ?value ?unit
WHERE {
  ?bodMeasurement a wawo:BiochemicalOxygenDemand ;
                  wawo-upper:hasDataValue ?value ;
                  wawo-upper:hasUnit ?unit .
}
ORDER BY DESC(?value)
```

### Query 3: Compare inlet vs outlet concentrations at WWTP

```sparql
PREFIX wawo: <http://kemlg.upc.edu/wawo-core-tbox#>
PREFIX wawo-upper: <http://kemlg.upc.edu/wawo-upper-tbox#>

SELECT ?parameter ?inletValue ?outletValue
       ((?inletValue - ?outletValue) / ?inletValue * 100 AS ?removalPercent)
WHERE {
  ?wwtp a wawo:WasteWaterTreatmentPlant .

  # Inlet measurements
  ?wwtp wawo:receives ?inletWater .
  ?inletWater wawo:hasConcentration ?inletMeasurement .
  ?inletMeasurement a ?parameter ;
                    wawo-upper:hasDataValue ?inletValue .

  # Outlet measurements
  ?wwtp wawo:discharges ?outletWater .
  ?outletWater wawo:hasConcentration ?outletMeasurement .
  ?outletMeasurement a ?parameter ;
                     wawo-upper:hasDataValue ?outletValue .

  FILTER(?parameter IN (wawo:BiochemicalOxygenDemand, wawo:ChemicalOxygenDemand))
}
```

### Query 4: Find all chemical indicators above threshold

```sparql
PREFIX wawo: <http://kemlg.upc.edu/wawo-core-tbox#>
PREFIX wawo-upper: <http://kemlg.upc.edu/wawo-upper-tbox#>

SELECT ?indicator ?value ?unit
WHERE {
  ?indicator a ?indicatorType ;
             wawo-upper:hasDataValue ?value ;
             wawo-upper:hasUnit ?unit .

  ?indicatorType rdfs:subClassOf* wawo:ChemicalIndicatorParameter .

  FILTER(?value > 100)  # Values above 100 mg/L
}
ORDER BY DESC(?value)
```

---

## Appendix B: RDF/XML to Turtle Conversion Examples

### Example 1: BOD Measurement in RDF/XML (from ABox)

```xml
<ClassAssertion>
    <Class IRI="http://kemlg.upc.edu/wawo-core-tbox#BiochemicalOxygenDemand"/>
    <NamedIndividual IRI="#BODinEDAR"/>
</ClassAssertion>
<DataPropertyAssertion>
    <DataProperty IRI="http://kemlg.upc.edu/wawo-upper-tbox#hasDataValue"/>
    <NamedIndividual IRI="#BODinEDAR"/>
    <Literal datatypeIRI="http://www.w3.org/2001/XMLSchema#decimal">272</Literal>
</DataPropertyAssertion>
<ObjectPropertyAssertion>
    <ObjectProperty IRI="http://kemlg.upc.edu/wawo-upper-tbox#hasUnit"/>
    <NamedIndividual IRI="#BODinEDAR"/>
    <NamedIndividual IRI="http://purl.oclc.org/NET/ssnx/qu/unit#milligramPerLitre"/>
</ObjectPropertyAssertion>
```

### Example 2: Same measurement in Turtle

```turtle
@prefix : <http://example.org/girona#> .
@prefix wawo: <http://kemlg.upc.edu/wawo-core-tbox#> .
@prefix wawo-upper: <http://kemlg.upc.edu/wawo-upper-tbox#> .
@prefix qu: <http://purl.oclc.org/NET/ssnx/qu/unit#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

:BODinEDAR a wawo:BiochemicalOxygenDemand ;
    wawo-upper:hasDataValue 272.0 ;
    wawo-upper:hasUnit qu:milligramPerLitre .
```

---

## Appendix C: Comparison Summary Table

| Aspect | WaWO+ (Actual Implementation) | WaWO+ (Paper Description) | WaterFrame (Current) |
|--------|-------------------------------|---------------------------|----------------------|
| **Measurement Pattern** | Amount instances | Direct data properties (claimed) | SOSA Observations |
| **Property for linking** | `hasConcentration` (object) | `biologicalOxygenDemandConcentration` (data) | `sosa:observedProperty` |
| **Value storage** | `hasDataValue` on Amount | Direct on WaterMass | `sosa:hasSimpleResult` |
| **Typing mechanism** | RDF type of Amount instance | Implicit via property name | Observable property URI |
| **Unit handling** | `hasUnit` → QUDT | Not clearly specified | QUDT directly |
| **Standards compliance** | Custom pattern | Custom pattern | W3C SSN/SOSA |
| **Query complexity** | Medium (1-2 hops) | Low (direct) | High (2-3 hops) |
| **Temporal support** | Not built-in | Not built-in | Built-in (resultTime) |
| **Provenance support** | Not built-in | Not built-in | Built-in (madeBySensor) |

---

**End of Report**
