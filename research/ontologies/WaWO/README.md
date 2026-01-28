# WaWO+ Ontology Implementation

This directory contains a complete implementation of the WaWO+ (Water and Wastewater Ontology Plus) ontology based on the specification from Oliva-Felipe et al. (2017) - "Reasoning about river basins: WaWO+ revisited".

## Files

### 1. Ontology Files
- **[wawo_plus.ttl](wawo_plus.ttl)** - Complete WaWO+ ontology in Turtle format
  - 852 triples defining the ontology structure
  - 233 classes organized in a 6-level hierarchy
  - 22 object properties
  - 18 data properties
  - OWL 2 axioms and constraints

### 2. Documentation
- **[WaWO_Plus_Ontology_reverse_enginered.md](WaWO_Plus_Ontology_reverse_enginered.md)** - Detailed specification document
  - Reverse-engineered from the research paper
  - Complete class hierarchies
  - Property definitions with domains and ranges
  - Inference rules and reasoning capabilities
  - SPARQL query examples

- **[competency_questions.md](competency_questions.md)** - Competency questions and test queries
  - 10 categories of competency questions
  - 30+ SPARQL queries to test the ontology
  - Expected results for each question

### 3. Testing
- **[test_wawo_plus.py](test_wawo_plus.py)** - Comprehensive test suite using Python's rdflib
  - 25 automated tests
  - Tests all major ontology features
  - Validates SPARQL query capabilities
  - All tests passing ✓

## Ontology Features

### Core Domains Covered

1. **Water Quality Classification**
   - Chemical indicators (BOD, COD, SS, TN, TP)
   - Physical indicators (temperature, pH, turbidity, conductivity)
   - Heavy metals (Mercury, Lead, Cadmium, etc.)
   - Emerging contaminants (pharmaceuticals, pesticides)
   - Automatic classification of drinking water vs wastewater

2. **Wastewater Treatment**
   - WWTP (Wastewater Treatment Plant) infrastructure
   - Treatment processes (Primary, Secondary, Tertiary)
   - Regulatory compliance checking
   - Population equivalent tracking
   - Influent/effluent monitoring

3. **Urban Water Systems**
   - Water sources (groundwater, surface water, storm water)
   - Conveyor infrastructure (pipes, pumps, collectors)
   - Distribution and collection networks
   - Flow tracking through the system

4. **River Basin Management**
   - Geographical features (river sections, basins, streams)
   - Water mass tracking with quality indicators
   - Stakeholder management (authorities, operators)
   - Spatial relationships

5. **Meteorological Events**
   - Precipitation tracking (rainfall, snowfall)
   - Event classification (normal, light, medium, heavy)
   - Temporal information with timestamps
   - Duration and amount measurements

6. **Regulatory Norms**
   - Regulative norms (obligations, permissions, prohibitions)
   - Constitutive norms (institutional facts)
   - Deontic components (activation, maintenance, expiration)
   - Sanctions for violations

## Usage

### Loading the Ontology

```python
from rdflib import Graph, Namespace

# Create graph and load ontology
g = Graph()
wawo = Namespace("http://www.semanticweb.org/riverbasin#")
g.bind("wawo", wawo)
g.parse("wawo_plus.ttl", format="turtle")

print(f"Loaded {len(g)} triples")
```

### Example SPARQL Queries

#### 1. Find Drinking Water Quality Samples
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?waterMass ?bod ?cod ?tn ?tp
WHERE {
  ?waterMass a wawo:WaterMass ;
             wawo:hasWaterComposition ?comp ;
             wawo:biologicalOxygenDemandConcentration ?bod ;
             wawo:chemicalOxygenDemandConcentration ?cod ;
             wawo:totalNitrogenConcentration ?tn ;
             wawo:totalPhosphorusConcentration ?tp .
  ?comp a wawo:DrinkingWaterComposition .
}
```

#### 2. Identify Non-Compliant WWTPs
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?wwtp ?popEq
WHERE {
  ?wwtp a wawo:WWTP ;
        wawo:populationEquivalent ?popEq .
  FILTER(?popEq >= 10000)
  FILTER NOT EXISTS {
    ?wwtp wawo:performs ?treatment .
    ?treatment a wawo:SecondaryTreatment .
  }
}
```

#### 3. Detect Heavy Metal Contamination
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?waterMass ?concentration ?location
WHERE {
  ?waterMass a wawo:WaterMass ;
             wawo:heavyMetalConcentration ?concentration .
  OPTIONAL {
    ?location wawo:hasWaterMass ?waterMass .
  }
  FILTER(?concentration >= 0.005)  # Mercury limit
}
```

#### 4. Track Water Flow Through System
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?source ?waterMass ?flow ?destination
WHERE {
  ?source wawo:produces ?waterMass .
  ?waterMass a wawo:Flow_water_mass ;
             wawo:flow ?flow .
  OPTIONAL {
    ?destination wawo:received ?waterMass .
  }
}
```

## Running Tests

To run the complete test suite:

```bash
cd research/ontologies/WaWO
uv run python test_wawo_plus.py
```

Expected output:
```
================================================================================
WaWO+ ONTOLOGY TEST SUITE
================================================================================

✓ Ontology loaded successfully: 852 triples
✓ Test data added: 922 total triples

... (25 tests) ...

================================================================================
TEST SUMMARY
================================================================================
Tests run: 25
Successes: 25
Failures: 0
Errors: 0

✓ ALL TESTS PASSED!
```

## Test Coverage

The test suite validates:

1. ✓ Ontology structure and loading
2. ✓ Class hierarchy relationships
3. ✓ Disjoint class axioms
4. ✓ Water quality classification (3 tests)
5. ✓ WWTP compliance tracking (4 tests)
6. ✓ Water mass flow tracking (3 tests)
7. ✓ Heavy metal and contaminant detection (3 tests)
8. ✓ Meteorological event identification (2 tests)
9. ✓ Infrastructure connection mapping (2 tests)
10. ✓ Stakeholder management (1 test)
11. ✓ Population equivalent tracking (1 test)
12. ✓ Aggregate statistics computation (1 test)
13. ✓ Object property definitions (1 test)
14. ✓ Data property definitions (1 test)

## Ontology Statistics

- **Total Classes**: 233 (as specified in the paper)
- **Top-level Classes**: 27
- **Object Properties**: 22
- **Data Properties**: 18
- **Class Hierarchy Depth**: Maximum 6 levels
- **Disjointness Axioms**: Multiple sets defined
- **OWL 2 Restrictions**: Cardinality and value constraints

## Key Class Hierarchies

### Water Quality
```
WaterComposition
├── DrinkingWaterComposition (with quality thresholds)
├── RiverWaterComposition
└── WastewaterComposition

WaterIndicator
├── Chemical
│   ├── BOD, COD, SS, TN, TP
│   ├── EmergingContaminant
│   └── HeavyMetal
└── Physical
    ├── Temperature, pH, Turbidity
    └── Conductivity
```

### Infrastructure
```
WaterTreatmentFacility
└── WWTP

ConveyorUnit
├── Pipe
├── Pump
├── Collector
└── Spillway

Process
└── WastewaterTreatment
    ├── WaterTreatment
    │   ├── SecondaryTreatment
    │   ├── Disinfection
    │   └── Coagulation
    └── ConveyorTransport
```

### Normative Structure
```
Norm
├── RegulativeNorm
│   └── DeonticNorm
│       ├── Obligation
│       ├── Permission
│       └── Prohibition
└── ConstitutiveNorm
```

## Integration Possibilities

The ontology can be integrated with:

1. **GeoSPARQL** - For spatial reasoning about river basins
2. **SSN/SOSA** - For sensor and observation data
3. **PROV-O** - For data provenance tracking
4. **Time Ontology** - For advanced temporal reasoning
5. **ENVO** - For environmental features

## References

- Oliva-Felipe, L., Gómez-Sebastià, I., Verdaguer, M., Sanchez-Marré, M., Poch, M., & Cortés, U. (2017).
  "Reasoning about river basins: WaWO+ revisited".
  *Procedia Computer Science*, 108, 2397-2401.

## License

This implementation is based on academic research and is provided for research and educational purposes.

## Contact

For questions or issues, please refer to the ontEAUlogy project documentation.
