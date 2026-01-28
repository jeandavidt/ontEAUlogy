# Ghent Enhanced Case Study

This directory contains an enhanced version of the Ghent synthetic water system case study, demonstrating the new ontology features added in Phases 1-4 of the waterFRAME ontology enhancement project.

## Overview

The Ghent Enhanced case study builds upon the original Ghent case study (`case_studies/ghent/`) by incorporating:

- **Phase 1**: Jurisdiction-aware water composition classes and regulatory frameworks
- **Phase 2**: rdfs:seeAlso references to WaWO+, OntoCAPE, and ENVO ontologies
- **Phase 3**: Scenario modeling with OWL-Time temporal representation
- **Phase 4**: PROV-O provenance tracking for water quality observations

## Directory Structure

```
ghent_enhanced/
├── README.md                          # This file
├── data/
│   ├── system.ttl                     # Enhanced system configuration
│   ├── display_metadata.ttl           # Display metadata (unchanged from original)
│   └── instances/
│       ├── baseline_scenario.ttl      # Baseline scenario with OWL-Time
│       ├── lieve_river.ttl           # River with water composition classes
│       ├── dwp1.ttl                  # DWP-1 with drinking water standards
│       ├── dwp2.ttl                  # DWP-2 with EU directive compliance
│       ├── wwtp1.ttl                 # WWTP-1 with provenance tracking
│       ├── wwtp2.ttl                 # WWTP-2 with advanced treatment composition
│       ├── dampoort_residential.ttl  # Residential district files
│       ├── muide_residential.ttl
│       ├── texfin.ttl                # Industrial facility files
│       ├── foodpro.ttl
│       ├── chiptech.ttl
│       ├── pharmagen.ttl
│       ├── brewco.ttl
│       └── sensors/                  # Sensor configuration files
│           ├── dwp_sensors.ttl
│           ├── wwtp_sensors.ttl
│           ├── flow_sensors.ttl
│           ├── weather_sensors.ttl
│           └── industrial_and_river_sensors.ttl
```

## Key Enhancements

### Phase 1: Jurisdiction-Aware Water Composition

**Regulatory Frameworks** (`system.ttl`):
- `ghent:BelgianDischargeLimits` - VLAREM II standards for Flanders (gn:2800866)
- `ghent:EU_DrinkingWaterDirective` - EU Directive 2020/2184 for Belgium
- `ghent:EU_WaterReuseRegulation` - EU Regulation 2020/741

**Water Composition Classifications**:
- **Drinking Water** (`dwp1.ttl`, `dwp2.ttl`):
  - `ghent:DWP1_DrinkingWaterComposition` - Potable water meeting EU standards
  - `ghent:DWP2_DrinkingWaterComposition` - Advanced treated drinking water
  - Linked to `ghent:EU_DrinkingWaterDirective` via `wf:definingFramework`

- **Treated Wastewater** (`wwtp1.ttl`, `wwtp2.ttl`):
  - `ghent:WWTP1_TreatedEffluentComposition` - Conventional treatment meeting VLAREM II
  - `ghent:WWTP2_AdvancedTreatedComposition` - MBR+GAC exceeding standards
  - Linked to `ghent:BelgianDischargeLimits` via `wf:definingFramework`

- **Surface Water** (`lieve_river.ttl`):
  - `ghent:LieveSegment1_SurfaceWaterComposition` - Clean upstream water
  - `ghent:LieveSegment2_ImpactedWaterComposition` - Post-WWTP-1 impact
  - `ghent:LieveSegment3_DownstreamWaterComposition` - Cumulative WWTP impact

**Jurisdiction Context**:
- All regulatory frameworks linked to Flanders, Belgium via `wf:appliesInJurisdiction gn:2800866`
- GeoNames prefix added: `@prefix gn: <http://sws.geonames.org/>`

### Phase 2: External Ontology References

**WaWO+ Integration**:
- DrinkingWaterQuality class references `<http://www.semanticweb.org/wawo/DrinkingWaterComposition>`
- Surface water classifications inspired by WaWO+ patterns
- Annotations: `rdfs:seeAlso` and `rdfs:comment` for WaWO+ attribution

**ENVO Ontology** (maintained from original):
- River classified with `envo:00000022` (river)
- Located in `envo:01000249` (urban biome)
- Water type `envo:00002042` (surface water)

### Phase 3: Scenario Modeling with OWL-Time

**Baseline Scenario** (`instances/baseline_scenario.ttl`):
- `ghent:Baseline2026` - Complete baseline scenario for 2026
- **Temporal Extent**: Uses OWL-Time `time:Interval` with precise timestamps
  - Start: `2026-01-01T00:00:00Z`
  - End: `2026-12-31T23:59:59Z`
- **Components**: Links all 12 system components (2 DWPs, 2 WWTPs, 2 residential, 5 industrial, 1 river)
- **Metadata**:
  - Scenario name, purpose, and detailed description
  - Configuration summary with water balance and quality data
  - Notes on creating alternative scenarios

**System Link** (`system.ttl`):
- System linked to baseline: `ghent:GhentWaterSystem wf:inScenario ghent:Baseline2026`

**Future Alternative Scenarios**:
- Commented placeholders show how to create alternatives:
  - Water reuse scenarios
  - Greywater recycling scenarios
  - Climate adaptation scenarios
- All alternatives would link via `wf:alternativeTo ghent:Baseline2026`

### Phase 4: PROV-O Provenance Tracking

**Sampling Activities** (`wwtp1.ttl`, `wwtp2.ttl`):
- `ghent:WWTP1_RoutineSampling_2026_01` - Monthly composite sampling (January 2026)
- `ghent:WWTP2_RoutineSampling_2026_01` - Monthly composite sampling with micropollutant tracking
- Both typed as `prov:Activity` and `wf:SamplingActivity`
- Temporal bounds: `prov:startedAtTime` and `prov:endedAtTime`

**Laboratory Agent**:
- `ghent:AquaFin_Lab` - Certified water quality laboratory
- Typed as `prov:Agent`
- Associated with sampling activities via `prov:wasAssociatedWith`

**Water Quality Observations**:
- All 10 WWTP influent/effluent observations enhanced with:
  - `prov:wasGeneratedBy` → links to sampling activity
  - `prov:wasAttributedTo` → links to laboratory
  - `prov:generatedAtTime` → timestamp of analysis result

**Example Observation**:
```turtle
ghent:WWTP1_Effluent_BOD a wf:WaterQualityObservation ;
    wf:observedParameter wf:BOD ;
    wf:observedValue "12.0"^^xsd:double ;
    qudt:unit unit:MilligramPerLiter ;
    wf:observedAt ghent:WWTP1_Effluent_Out ;
    prov:wasGeneratedBy ghent:WWTP1_RoutineSampling_2026_01 ;
    prov:wasAttributedTo ghent:AquaFin_Lab ;
    prov:generatedAtTime "2026-01-16T11:00:00Z"^^xsd:dateTime .
```

## Usage

### Loading the Enhanced Data

```turtle
# Import the system configuration (which references all components)
@prefix ghent: <https://w3id.org/waterframe/case/ghent/> .
@base <https://w3id.org/waterframe/case/ghent/> .

# Load system and baseline
<> owl:imports <case_studies/ghent_enhanced/data/system.ttl> .
<> owl:imports <case_studies/ghent_enhanced/data/instances/baseline_scenario.ttl> .

# Load individual components as needed
<> owl:imports <case_studies/ghent_enhanced/data/instances/wwtp1.ttl> .
# ... etc
```

### Example SPARQL Queries

**Query 1: Find all water compositions and their regulatory frameworks**
```sparql
PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
PREFIX gn: <http://sws.geonames.org/>

SELECT ?composition ?label ?framework ?jurisdiction
WHERE {
  ?composition a wf:WaterComposition ;
               rdfs:label ?label ;
               wf:definingFramework ?framework .
  ?framework wf:appliesInJurisdiction ?jurisdiction .
}
```

**Query 2: Find all observations with provenance information**
```sparql
PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
PREFIX prov: <http://www.w3.org/ns/prov#>

SELECT ?obs ?param ?value ?activity ?lab ?time
WHERE {
  ?obs a wf:WaterQualityObservation ;
       wf:observedParameter ?param ;
       wf:observedValue ?value ;
       prov:wasGeneratedBy ?activity ;
       prov:wasAttributedTo ?lab ;
       prov:generatedAtTime ?time .
}
ORDER BY ?time
```

**Query 3: List all components in the 2026 baseline scenario**
```sparql
PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
PREFIX ghent: <https://w3id.org/waterframe/case/ghent/>

SELECT ?component ?type ?label
WHERE {
  ghent:Baseline2026 wf:scenarioComponent ?component .
  ?component a ?type ;
             rdfs:label ?label .
  FILTER(?type != owl:NamedIndividual)
}
```

**Query 4: Get temporal extent of baseline scenario**
```sparql
PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
PREFIX time: <http://www.w3.org/2006/time#>
PREFIX ghent: <https://w3id.org/waterframe/case/ghent/>

SELECT ?start ?end
WHERE {
  ghent:Baseline2026 wf:hasTemporalExtent ?interval .
  ?interval time:hasBeginning/time:inXSDDateTimeStamp ?start ;
            time:hasEnd/time:inXSDDateTimeStamp ?end .
}
```

## Comparison with Original Case Study

| Feature | Original (`case_studies/ghent/`) | Enhanced (`case_studies/ghent_enhanced/`) |
|---------|----------------------------------|-------------------------------------------|
| **Water composition** | Implicit in observations | Explicit `wf:WaterComposition` classes |
| **Regulatory context** | Generic `wf:VLAREM_II` | Jurisdiction-specific frameworks with GeoNames |
| **Scenario definition** | Comments only | Formal `wf:BaselineScenario` with OWL-Time |
| **Provenance** | None | PROV-O for all observations |
| **External ontology links** | ENVO only | WaWO+, ENVO, references to OntoCAPE patterns |
| **Temporal representation** | Ad-hoc timestamps | OWL-Time intervals and instants |
| **Future extensibility** | Limited | Scenario framework for alternatives |

## Creating Alternative Scenarios

To create an alternative scenario based on this baseline:

1. **Define the scenario**:
```turtle
ghent:WaterReuseAlternative2027 a wf:AlternativeScenario ;
    wf:scenarioName "WWTP-2 Water Reuse Alternative" ;
    wf:alternativeTo ghent:Baseline2026 ;
    wf:scenarioPurpose "Evaluate direct reuse of WWTP-2 effluent for industrial cooling" .
```

2. **Add temporal extent** (if different from baseline):
```turtle
ghent:WaterReuseAlternative2027 wf:hasTemporalExtent [
    a time:Interval ;
    time:hasBeginning [ a time:Instant ; time:inXSDDateTimeStamp "2027-01-01T00:00:00Z"^^xsd:dateTimeStamp ] ;
    time:hasEnd [ a time:Instant ; time:inXSDDateTimeStamp "2027-12-31T23:59:59Z"^^xsd:dateTimeStamp ]
] .
```

3. **Link existing and new components**:
```turtle
# Existing components (unchanged)
ghent:WaterReuseAlternative2027 wf:scenarioComponent ghent:WWTP2 ;
                                 wf:scenarioComponent ghent:ChipTech ;
                                 wf:scenarioComponent ghent:BrewCo .

# New components (only exist in alternative)
ghent:ReuseConnectionPipe a wf:Pipeline ;
    wf:inScenario ghent:WaterReuseAlternative2027 .
```

4. **Compare with baseline** using scenario comparison framework.

## References

- **WaWO+ Ontology**: Water domain ontology (http://www.semanticweb.org/wawo/)
- **ENVO Ontology**: Environment Ontology (http://purl.obolibrary.org/obo/)
- **OWL-Time**: W3C Time Ontology (https://www.w3.org/TR/owl-time/)
- **PROV-O**: W3C Provenance Ontology (https://www.w3.org/TR/prov-o/)
- **GeoNames**: Geographic database (https://www.geonames.org/)

## Data Provenance

- **Original Case Study**: `case_studies/ghent/`
- **Enhancement Date**: January 28, 2026
- **Enhanced Ontology**: `data/ontology_enhanced/`
- **Baseline Period**: Calendar Year 2026
- **Sampling Data**: January 2026 (synthetic)

## Next Steps

Potential future enhancements to this case study:

1. **Additional Scenarios**:
   - Water reuse scenarios (industrial, agricultural, urban non-potable)
   - Greywater recycling in residential districts
   - Climate change adaptation (2030, 2050 projections)
   - Infrastructure expansion alternatives

2. **Enhanced Provenance**:
   - Chain of custody for samples
   - Laboratory equipment and methods
   - Quality control/quality assurance data
   - Sensor calibration records

3. **Optimization Scenarios**:
   - Multi-objective optimization (cost, energy, quality, sustainability)
   - Integration with OntoAgent optimization framework
   - Constraint-based scenario generation

4. **Integration**:
   - Link to real GeoNames features (currently uses generic Flanders ID)
   - Integration with actual regulatory text databases
   - Connection to OntoCAPE process models
   - Alignment with other water system ontologies

## License

This case study inherits the license from the waterFRAME ontology project.

## Contact

For questions about this enhanced case study, please refer to the main waterFRAME documentation.
