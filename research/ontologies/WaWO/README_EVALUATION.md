# WaWO+ Ontology Evaluation

This directory contains tools and documentation for evaluating the WaWO+ (Water and Wastewater Ontology Plus) version 1.3.0.

## Files

- **`evaluate_wawo_plus.py`** - Comprehensive Python evaluation script
- **`WaWO_Plus_Evaluation_Report.md`** - Generated evaluation report
- **`test_data_wawo_plus.ttl`** - Test instance data in Turtle format
- **`WaWO_Plus_Ontology_reverse_enginered.md`** - Reverse-engineered specification from paper
- **`wawo_plus_reverse_engineered.ttl`** - Reverse-engineered ontology in Turtle format
- **`competency_questions.md`** - Competency questions for testing

## Running the Evaluation

### Prerequisites

```bash
# Install dependencies
uv sync

# Ensure rdflib is installed (should be in pyproject.toml)
uv add rdflib

# Optional: Install owlready2 for reasoning tests
uv add owlready2
```

### Execute Evaluation

```bash
# From project root
uv run python research/ontologies/WaWO/evaluate_wawo_plus.py

# The script will:
# 1. Load WaWO+ ontology files (wawo-upper-tbox.owl and wawo-core-tbox.owl)
# 2. Generate test instance data
# 3. Run SPARQL queries
# 4. Attempt reasoning with Pellet (if owlready2 available)
# 5. Analyze coverage gaps
# 6. Generate markdown report
```

## Evaluation Protocol

The script follows the systematic ontology testing protocol from `agent_research.md`:

### Phase 1: Load and Inspect
- Loads both wawo-upper-tbox.owl and wawo-core-tbox.owl
- Reports basic statistics (classes, properties, individuals)
- Compares actual counts vs. paper specification (233 classes claimed)
- Identifies import resolution issues

### Phase 2: Instantiate Example Data
Creates test instances for:
- **WaterMass**: Drinking water, wastewater, flow water masses
- **Water Quality Indicators**: BOD, COD, SS, TN, TP concentrations
- **Contaminants**: Heavy metals (mercury), emerging pollutants (pharmaceuticals)
- **Infrastructure**: WWTPs (large and small), river sections, pipes
- **Treatment Processes**: Secondary treatment, chlorination

Test data saved to: `test_data_wawo_plus.ttl`

### Phase 3: Query Testing
Tests SPARQL queries from:
- **Paper Listing 1**: Water quality statistics across river sections
- **Competency Questions**:
  - CQ1.3: Water quality indicators
  - CQ2.2: WWTPs requiring secondary treatment (pop >= 10,000)
  - CQ2.3: Non-compliant WWTPs
  - CQ4.2: Mercury contamination above regulatory limits
  - CQ6.1: Infrastructure connections

Results: PASS/PARTIAL/FAIL/NOT_SUPPORTED

### Phase 4: Reasoning Consistency Check
- Attempts to load with owlready2
- Runs Pellet reasoner for consistency checking
- Reports inferred facts and reasoning performance
- **Note**: May fail due to import resolution issues

### Phase 5: Coverage Gap Analysis
Evaluates support for:
- ✓/◐/✗ Water quality classification
- ✓/◐/✗ Treatment facility compliance
- ✓/◐/✗ Water mass flow tracking
- ✓/◐/✗ Heavy metal and contaminant tracking
- ✓/◐/✗ Meteorological events
- ✓/◐/✗ Infrastructure connections
- ✓/◐/✗ Normative reasoning (norms, obligations)

### Additional: Namespace Analysis
Compares namespace usage between:
- Original WaWO+ (kemlg.upc.edu)
- Reverse-engineered version

## Key Findings

### Statistics Comparison

| Component | Classes | Object Props | Data Props | Individuals |
|-----------|---------|--------------|------------|-------------|
| **Paper Specification** | 233 | 22 | 18 | - |
| **wawo-upper-tbox** | 5 | 4 | 1 | 3 |
| **wawo-core-tbox** | 314 | 53 | 1 | 3 |
| **Combined (upper+core)** | 319 | 57 | 2 | 6 |

**Observations:**
- ✓ More classes than paper claims (319 vs. 233)
- ✓ More object properties than claimed (57 vs. 22)
- ⚠ **Far fewer data properties than claimed (2 vs. 18)**
  - This is a significant gap - water quality properties may be missing

### Import Issues

The following imports are declared but may not resolve:
- `http://purl.oclc.org/NET/ssnx/ssn` (SSN ontology)
- `http://www.w3.org/2006/time#2016` (Time ontology - malformed IRI)
- `http://purl.oclc.org/NET/ssnx/qu/qu-rec20` (Quantities and Units)
- `http://www.opengis.net/gml/` (GML)
- `http://purl.org/geovocamp/ontology/SurfaceWater_Wet`
- `http://kemlg.upc.edu/wawo-upper-abox/1.3.0` (Instance data)

**Impact:** Limited reasoning capabilities due to missing imports

### Query Test Results

**5/6 queries PASSED** (83% success rate)

- ✓ Q1_Paper: Water quality statistics
- ✓ CQ1.3: Query water quality indicators
- ✓ CQ2.2: WWTPs requiring secondary treatment
- ◐ CQ2.3: Non-compliant WWTPs (partial - no violations in test data)
- ✓ CQ4.2: Mercury contamination detection
- ✓ CQ6.1: Infrastructure connections

### Coverage Assessment

| Requirement | Support | Status |
|-------------|---------|--------|
| Treatment facilities | FULL | ✓ WWTP, process classes present |
| Meteorological events | FULL | ✓ Rainfall, precipitation classes |
| Normative reasoning | FULL | ✓ Norm-related classes found |
| Infrastructure connections | PARTIAL | ◐ Classes exist, limited properties |
| Water mass flow tracking | PARTIAL | ◐ Flow class exists, limited integration |
| Water quality classification | NONE | ✗ Missing data properties for BOD/COD/etc |
| Heavy metal tracking | NONE | ✗ Property definitions not found in schema |

## Gaps and Limitations

### Critical Gaps

1. **Data Property Deficiency**: Only 2 data properties found vs. 18 claimed
   - Water quality concentration properties (BOD, COD, SS, TN, TP) may be present in instances but not properly declared in TBox

2. **Import Resolution**: Several critical imports fail to resolve
   - Prevents full reasoning capabilities
   - May hide additional classes/properties

3. **SWRL Rules Missing**: Paper mentions SWRL rules for water classification (Figure 7), but these are not present in OWL files

4. **Documentation**: Many classes lack `rdfs:comment` annotations

### Known Issues

- **owlready2 reasoning fails** due to Time ontology import issue
- **Namespace differences** between original (kemlg.upc.edu) and what might be expected
- **Reverse-engineered version** has MORE elements (486 classes) than original, suggesting specification drift

## Recommendations

### For waterFRAME Integration

**Recommendation: EXTEND**

WaWO+ provides a solid foundation but needs extensions:

1. **Bridge data property gap**
   - Add explicit declarations for water quality properties
   - Ensure BOD, COD, SS, TN, TP are properly typed as `owl:DatatypeProperty`

2. **Fix imports**
   - Use local copies of SSN, Time, QUDT ontologies
   - Correct malformed Time ontology IRI

3. **Add agent integration**
   - Model metadata for computational models
   - Add invocation protocols for optimization agents

4. **Extend normative reasoning**
   - Add SWRL rules for regulatory compliance
   - Model European Water Framework Directive constraints

5. **Process model metadata**
   - Link to ASM/ADM1 process models
   - Add decision variable annotations

## Sample Queries

### Query Water Quality Indicators

```sparql
PREFIX wawo: <http://kemlg.upc.edu/wawo-core-tbox#>

SELECT ?waterMass ?bod ?cod ?ss
WHERE {
  ?waterMass a wawo:WaterMass ;
             wawo:biologicalOxygenDemandConcentration ?bod ;
             wawo:chemicalOxygenDemandConcentration ?cod ;
             wawo:suspendedSolidConcentration ?ss .
}
```

### Find Non-Compliant WWTPs

```sparql
PREFIX wawo: <http://kemlg.upc.edu/wawo-core-tbox#>

SELECT ?wwtp ?popEq
WHERE {
  ?wwtp a wawo:WWTP ;
        wawo:populationEquivalent ?popEq .
  FILTER(?popEq >= 10000)
  FILTER NOT EXISTS {
    ?wwtp wawo:hasTreatmentProcess ?treatment .
    ?treatment a wawo:SecondaryTreatment .
  }
}
```

### Detect Mercury Contamination

```sparql
PREFIX wawo: <http://kemlg.upc.edu/wawo-core-tbox#>

SELECT ?waterMass ?mercury
WHERE {
  ?waterMass a wawo:WaterMass ;
             wawo:heavyMetalConcentration ?mercury .
  FILTER(?mercury >= 0.005)
}
```

## References

- **Paper**: Oliva-Felipe et al. (2017) - "Reasoning about river basins: WaWO+ revisited"
- **Original WaWO**: Based on 2001 ontology focused on wastewater treatment microorganisms
- **WaWO+ Extensions**:
  - Water quality classification (Section 4.1)
  - Urban water cycle (Section 4.2)
  - Social/normative layer (Section 4.3)
  - Meteorological events (Section 4.4)

## Contact

For questions about this evaluation or waterFRAME integration, see project documentation.
