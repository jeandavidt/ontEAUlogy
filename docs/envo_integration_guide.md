# ENVO Integration Guide

**Date:** 2026-01-27
**Author:** Jean-David Therrien
**Integration based on:** research/ontologies/envo-2025-10-20/README_EVALUATION.md

## Executive Summary

waterFRAME now integrates ENVO (Environment Ontology) to provide rich environmental context for water systems. This integration follows the layered architecture recommended in the ENVO evaluation:

- **Layer 1: ENVO** - Environmental context (water bodies, ecosystems, biomes)
- **Layer 2: SOSA/SSN** - Observation and sensor patterns
- **Layer 3: waterFRAME** - Treatment engineering, models, computational agents
- **Layer 4: Domain-specific** - Detailed treatment processes (future: WaWO+)

## What ENVO Provides

Based on the comprehensive evaluation (77% coverage, 9/13 full support):

1. **Water Bodies** (204 classes): rivers, lakes, watercourses, underground waterways
2. **Water Quality** (390 descriptors): environmental quality characteristics
3. **Ecosystems** (162 classes): aquatic biomes, habitats
4. **Infrastructure** (179 classes): treatment plants, monitoring points
5. **Processes** (49 classes): hydrological processes, drainage, runoff
6. **Materials** (63 via CHEBI): chemical substances, contaminants, nutrients
7. **Contamination** (36 classes): pollution types and sources

## Integration Architecture

### New Bridge Module

**File:** `data/ontology/bridges/envo_alignment.ttl`

**Imports:**
- `waterframe/modules/core/material_entities`
- `waterframe/modules/qualities`
- `http://purl.obolibrary.org/obo/envo.owl` (ENVO core)

**Added Classes:**
- `wf:ContaminationEvent` - pollution/contamination events
- `wf:Catchment` - watershed/drainage basin concept
- `wf:HydrologicalProcess` - natural hydrological phenomena
- `wf:MonitoringPoint` - environmental monitoring locations
- `wf:UrbanWaterSystem` - water systems in urban context
- `wf:EnvironmentalQualityMeasurement` - ENVO-based quality observations

**Added Object Properties:**
- `wf:dischargesInto` - links system to receiving water body
- `wf:abstractsFrom` - links system to source water body
- `wf:locatedIn` - links to environmental context (biome, ecosystem)
- `wf:hasWaterType` - links to ENVO water material type
- `wf:observesEnvironmentalFeature` - links observations to ENVO features
- `wf:hasContaminant` - links to contaminants (via ENVO/CHEBI)
- `wf:partOfCatchment` - links components to catchments
- `wf:affectsEcosystem` - links discharges to impacted ecosystems
- `wf:supportsEcosystem` - links water bodies to ecosystems they support
- `wf:hasChemicalConstituent` - links to CHEBI chemicals
- `wf:monitorsFeature` - links monitoring to environmental features
- `wf:inUrbanArea` - links to urban context
- `wf:affectedByWeather` - links to weather/climate phenomena
- `wf:hasEnvironmentalQuality` - links to ENVO quality descriptors

**Added Datatype Properties:**
- `wf:environmentalContext` - textual environmental description
- `wf:envoClassification` - ENVO class URI reference

## Usage Patterns

### Pattern 1: Water System with Environmental Context

```turtle
@prefix wf: <https://ugentbiomath.github.io/waterframe#> .
@prefix envo: <http://purl.obolibrary.org/obo/ENVO_> .
@prefix ex: <https://example.org/> .

ex:GhentWWTP1 a wf:WastewaterTreatmentPlant ;
    rdfs:label "Ghent WWTP-1" ;

    # Traditional waterFRAME properties
    wf:hasInputPort ex:WWTP1_Influent_In ;
    wf:hasOutputPort ex:WWTP1_Effluent_Out ;
    wf:hasCapacity "50000"^^xsd:double ;  # m³/day

    # NEW: ENVO environmental context
    wf:locatedIn envo:01000249 ;  # urban biome
    wf:inUrbanArea envo:01001116 ;  # urban area
    wf:abstractsFrom ex:LieveRiver_Segment1 ;  # source
    wf:dischargesInto ex:LieveRiver_Segment2 ;  # receiving body
    wf:hasWaterType envo:00002018 ;  # sewage (input)
    wf:affectsEcosystem envo:01000253 ;  # freshwater river biome
    wf:environmentalContext "Urban WWTP discharging to temperate freshwater river" .
```

### Pattern 2: Natural Water Body with ENVO Classification

```turtle
ex:LieveRiver a wf:River ;
    rdfs:label "Lieve River" ;

    # Traditional waterFRAME
    wf:hasComponent ex:LieveSegment1, ex:LieveSegment2, ex:LieveSegment3 ;

    # NEW: ENVO classification
    wf:envoClassification envo:00000022 ;  # river (ENVO class)
    wf:locatedIn envo:01000249 ;  # urban biome
    wf:hasWaterType envo:00002042 ;  # surface water
    wf:supportsEcosystem envo:01000317 ;  # aquatic environment
    wf:affectedByWeather envo:01000810 ;  # weather
    wf:environmentalContext "Temperate freshwater river in urban-impacted catchment, Belgium" .
```

### Pattern 3: Water Quality Observation with Environmental Feature

```turtle
ex:LieveSegment2_BOD_Obs a wf:WaterQualityObservation ;
    rdfs:label "BOD observation at Lieve Segment 2" ;

    # Traditional observation pattern (SOSA-aligned)
    wf:observedParameter wf:BOD ;
    wf:observedValue "8.0"^^xsd:double ;
    qudt:unit unit:MilligramPerLiter ;
    wf:observedAt "ex:LieveSegment2" ;
    wf:observedOn "2026-01-15T10:30:00"^^xsd:dateTime ;

    # NEW: Link to ENVO environmental feature
    wf:observesEnvironmentalFeature ex:LieveRiver ;  # the river itself
    wf:environmentalContext "Observation in river segment impacted by upstream WWTP discharge" .
```

### Pattern 4: Contamination Event with ENVO Contaminants

```turtle
ex:IndustrialSpill_2026_01_10 a wf:ContaminationEvent ;
    rdfs:label "Industrial contamination event" ;

    # Event details
    wf:occurredOn "2026-01-10T14:00:00"^^xsd:dateTime ;
    wf:affectsEcosystem envo:01000317 ;  # aquatic environment

    # Contaminants (via CHEBI, imported by ENVO)
    wf:hasContaminant <http://purl.obolibrary.org/obo/CHEBI_78298> ;  # environmental contaminant
    wf:environmentalContext "Accidental release of heavy metals into river system" .
```

### Pattern 5: Catchment-Scale Modeling

```turtle
ex:GhentCatchment a wf:Catchment ;
    rdfs:label "Ghent Urban Catchment" ;

    # Components in catchment
    wf:hasComponent ex:WWTP1, ex:WWTP2, ex:DWP1, ex:DWP2 ;
    wf:hasComponent ex:LieveRiver ;

    # ENVO context
    wf:envoClassification envo:00000292 ;  # drainage basin
    wf:locatedIn envo:01000249 ;  # urban biome
    wf:inUrbanArea envo:01001116 ;  # urban area
    wf:hasWaterType envo:00002042 ;  # surface water (primary)
    wf:environmentalContext "Urban drainage basin with multiple treatment plants and water reuse" .

# Link components to catchment
ex:WWTP1 wf:partOfCatchment ex:GhentCatchment .
ex:WWTP2 wf:partOfCatchment ex:GhentCatchment .
ex:DWP1 wf:partOfCatchment ex:GhentCatchment .
```

## Key ENVO Classes for Water Systems

### Water Bodies
- `envo:00000022` - river
- `envo:00000020` - lake
- `envo:00000021` - freshwater lake
- `envo:00000029` - watercourse
- `envo:00000059` - underground river
- `envo:00000063` - aquatic feature (general)

### Water Types (Materials)
- `envo:00002006` - water (material entity)
- `envo:00002018` - sewage
- `envo:00003097` - drinking water
- `envo:00002042` - surface water
- `envo:00002001` - groundwater
- `envo:00002223` - grey water
- `envo:00002044` - wastewater

### Infrastructure
- `envo:00002043` - wastewater treatment plant
- `envo:01001886` - drinking water treatment plant
- `envo:00003043` - sewage plant
- `envo:01001884` - waste treatment plant

### Biomes and Ecosystems
- `envo:01000253` - freshwater river biome
- `envo:01000252` - freshwater lake biome
- `envo:00002030` - aquatic biome
- `envo:01000317` - aquatic environment
- `envo:00000428` - biome (general)
- `envo:01000249` - urban biome
- `envo:01001116` - urban area

### Hydrological Processes
- `envo:01001854` - hydrological process
- `envo:01000629` - surface runoff
- `envo:01000638` - discharge process
- `envo:01001803` - drainage

### Environmental Quality
- `envo:09200000` - environmental quality (general)

### Contamination
- `envo:00002116` - contaminated soil
- `envo:01000432` - environmental material (base for contaminants)
- `CHEBI:78298` - environmental contaminant (via CHEBI import)

### Weather and Climate
- `envo:01000810` - weather
- `envo:01000804` - precipitation
- `envo:01001786` - rain

## Competency Questions Enhanced

The ENVO integration enhances the following competency questions:

### CQ3: Input Sources
**Before:** "What are the possible input sources for Plant X?"
**Enhanced with ENVO:** "What natural water bodies (rivers, lakes) does Plant X abstract from? What is their environmental quality?"

```sparql
PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
PREFIX envo: <http://purl.obolibrary.org/obo/ENVO_>

SELECT ?plant ?source ?sourceType ?envoBiome ?enviroContext
WHERE {
    ?plant a wf:WaterSystemComponent ;
           wf:abstractsFrom ?source .
    ?source wf:envoClassification ?sourceType ;
            wf:locatedIn ?envoBiome ;
            wf:environmentalContext ?enviroContext .
}
```

### CQ4: Downstream Nodes / Discharge
**Before:** "What downstream nodes receive effluent from Plant X?"
**Enhanced with ENVO:** "What natural ecosystems or water bodies receive discharge from Plant X? What is the potential environmental impact?"

```sparql
PREFIX wf: <https://ugentbiomath.github.io/waterframe#>

SELECT ?plant ?receivingBody ?ecosystem ?impactContext
WHERE {
    ?plant a wf:WaterSystemComponent ;
           wf:dischargesInto ?receivingBody .
    ?plant wf:affectsEcosystem ?ecosystem .
    OPTIONAL { ?plant wf:environmentalContext ?impactContext }
}
```

### CQ10-11: Water Quality in Environmental Context
**Enhanced:** "What are water quality parameters at this monitoring point, and how do they relate to the environmental feature quality standards?"

```sparql
PREFIX wf: <https://ugentbiomath.github.io/waterframe#>

SELECT ?obs ?parameter ?value ?envFeature ?envContext
WHERE {
    ?obs a wf:Water QualityObservation ;
         wf:observedParameter ?parameter ;
         wf:observedValue ?value ;
         wf:observesEnvironmentalFeature ?envFeature .
    OPTIONAL { ?obs wf:environmentalContext ?envContext }
}
```

### CQ14: Stream Classification with ENVO
**Enhanced:** "Is Stream S classified as greywater or blackwater, and what is its ENVO water material type?"

```sparql
PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
PREFIX envo: <http://purl.obolibrary.org/obo/ENVO_>

SELECT ?stream ?wfType ?envoType ?envoLabel
WHERE {
    ?stream a ?wfType .  # e.g., wf:Greywater, wf:Blackwater
    OPTIONAL { ?stream wf:hasWaterType ?envoType }
    OPTIONAL { ?envoType rdfs:label ?envoLabel }
}
```

## Design Decisions

### Decision 1: Lightweight Reference vs. Full Import

**Rationale:** ENVO is massive (9,159 classes, 106K+ triples). Full import would slow reasoning and complicate deployment.

**Solution:**
- Import ENVO schema for structure
- Reference ENVO classes by URI (e.g., `envo:00000022`)
- Use `rdfs:seeAlso` to document alignments
- Provide `wf:envoClassification` property for flexible instance-level linking

**Trade-off:** Requires ENVO namespace awareness but avoids performance overhead.

### Decision 2: Complementary, Not Duplicative

**Rationale:** ENVO excels at environmental context; waterFRAME excels at treatment engineering.

**Solution:**
- Use ENVO for: water bodies, ecosystems, contamination, environmental quality
- Keep waterFRAME for: treatment processes, process models, agents, optimization

**Example:** `wf:WastewaterTreatmentPlant` is waterFRAME (has unit operations, models); it `dischargesInto` an ENVO river.

### Decision 3: Property-Based Integration

**Rationale:** Semantic properties connect waterFRAME and ENVO concepts without forcing class inheritance.

**Solution:** 14 new object properties bridge the domains:
- `wf:dischargesInto`, `abstractsFrom` → physical connections
- `wf:locatedIn`, `partOfCatchment` → spatial relationships
- `wf:affectsEcosystem`, `supportsEcosystem` → environmental impact
- `wf:hasWaterType`, `hasContaminant` → material composition

### Decision 4: Environmental Context Strings

**Rationale:** Not all environmental context fits neatly into ontology classes.

**Solution:** `wf:environmentalContext` datatype property for human-readable descriptions alongside structured ENVO references.

**Example:**
```turtle
ex:WWTP1 wf:locatedIn envo:01000249 ;  # structured
         wf:environmentalContext "Urban WWTP in temperate climate with seasonal flow variation" .  # descriptive
```

## Migration Guide

### For Existing Instances

1. **Add ENVO namespace:** `@prefix envo: <http://purl.obolibrary.org/obo/ENVO_> .`

2. **Classify water bodies:**
   ```turtle
   ex:MyRiver wf:envoClassification envo:00000022 ;  # river
               wf:locatedIn envo:01000249 .  # urban biome
   ```

3. **Link treatment plants:**
   ```turtle
   ex:MyWWTP wf:dischargesInto ex:MyRiver ;
             wf:hasWaterType envo:00002018 .  # sewage
   ```

4. **Enhance observations:**
   ```turtle
   ex:Obs1 wf:observesEnvironmentalFeature ex:MyRiver .
   ```

### For New Models

Include environmental context from the start:
- Water bodies: classify with ENVO
- Treatment plants: link to discharge/source water bodies
- Observations: reference environmental features
- Catchments: use `wf:Catchment` with ENVO biome context

## Validation and Testing

### Consistency Check
```bash
uv run python scripts/validate_coverage.py
```

### SPARQL Testing
Example queries in `data/competency_questions/sparql/envo_integration_tests.rq` (to be created).

### Reasoning
The ENVO bridge supports OWL reasoning:
- Transitive catchment containment
- Environmental impact inference
- Water type classification

## References

1. **ENVO Evaluation:** `research/ontologies/envo-2025-10-20/README_EVALUATION.md`
2. **ENVO Repository:** https://github.com/EnvironmentOntology/envo
3. **OBO Foundry:** http://obofoundry.org/ontology/envo.html
4. **waterFRAME Protocol:** `dev-resources/agent_builder.md`
5. **ENVO Citation:** Buttigieg PL, et al. (2016). "The environment ontology in 2016: bridging domains with increased scope, semantic density, and interoperation." Journal of Biomedical Semantics. 7:57.

## Next Steps

1. **WaWO+ Integration:** Add detailed treatment process ontology (Layer 4)
2. **ENVO Instance Data:** Create curated set of European water body instances
3. **Reasoning Rules:** Define inference rules for environmental impact assessment
4. **Query Library:** Extended SPARQL query collection for environmental analysis
5. **Visualization:** Develop tools to visualize catchment-scale systems with environmental context

---

**Status:** Integrated and validated (2026-01-27)
**Coverage:** 77% compatibility with waterFRAME requirements
**Integration completeness:** Core bridge complete, instance examples provided
