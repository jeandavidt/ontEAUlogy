# Module: envo_alignment

Bridge module aligning waterFRAME concepts with ENVO (Environment Ontology).

    Integration Strategy (following research/ontologies/envo-2025-10-20/README_EVALUATION.md):

    USE ENVO FOR:
    1. Environmental context - natural water bodies, catchments, ecosystems
    2. Water quality descriptors - environmental quality vocabularies
    3. Spatial features - rivers, lakes, watersheds, drainage basins
    4. Pollution and contamination - environmental impacts

    KEEP waterFRAME FOR:
    1. Treatment processes - detailed unit operations
    2. Process models - computational model metadata
    3. Water reuse frameworks - fit-for-purpose classification
    4. Agent framework - computational agent representation

    This module provides semantic alignments without duplicating ENVO's extensive taxonomies.

**Module URI:** `https://ugentbiomath.github.io/waterframe/bridges/envo_alignment`

**Source:** `ontology/bridges/envo_alignment.ttl`

**Total Entities:** 24

## Contents

- [Classes](#classes) (8)
- [Object Properties](#object-properties) (14)
- [Datatype Properties](#datatype-properties) (2)

---

## Classes

## Catchment {#https___ugentbiomath.github.io_waterframe_catchment}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#Catchment`

### Labels

- Catchment

### Description

The area from which precipitation collects to a common outlet.

A catchment area or watershed containing multiple water system components

### Superclasses

- [BFO_0000040](#https___ugentbiomath.github.io_waterframe_bfo_0000040)
- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)

### Related Entities

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)


---

## ContaminationEvent {#https___ugentbiomath.github.io_waterframe_contaminationevent}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#ContaminationEvent`

### Labels

- Contamination event

### Description

An event where water becomes contaminated

### Superclasses

- [BFO_0000015](#https___ugentbiomath.github.io_waterframe_bfo_0000015)


---

## DrinkingWaterTreatmentPlant {#https___ugentbiomath.github.io_waterframe_drinkingwatertreatmentplant}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#DrinkingWaterTreatmentPlant`

### Labels

- [Undefined label]

### Description

Aligned with ENVO:01001886 (drinking water treatment plant)

### Superclasses

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)

### Related Entities

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)


---

## EnvironmentalQualityMeasurement {#https___ugentbiomath.github.io_waterframe_environmentalqualitymeasurement}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#EnvironmentalQualityMeasurement`

### Labels

- Environmental quality measurement

### Description

Measurement of an environmental quality using ENVO descriptors

### Superclasses

- [WaterQualityObservation](#https___ugentbiomath.github.io_waterframe_waterqualityobservation)

### Related Entities

- [WaterQualityObservation](#https___ugentbiomath.github.io_waterframe_waterqualityobservation)


---

## HydrologicalProcess {#https___ugentbiomath.github.io_waterframe_hydrologicalprocess}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#HydrologicalProcess`

### Labels

- Hydrological process

### Description

Natural hydrological processes affecting water systems

### Superclasses

- [BFO_0000015](#https___ugentbiomath.github.io_waterframe_bfo_0000015)


---

## MonitoringPoint {#https___ugentbiomath.github.io_waterframe_monitoringpoint}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#MonitoringPoint`

### Labels

- Monitoring point

### Description

A point where environmental monitoring occurs

### Superclasses

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)

### Related Entities

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)


---

## UrbanWaterSystem {#https___ugentbiomath.github.io_waterframe_urbanwatersystem}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#UrbanWaterSystem`

### Labels

- Urban water system

### Description

Water system in urban environment

### Superclasses

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)

### Related Entities

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)


---

## WastewaterTreatmentPlant {#https___ugentbiomath.github.io_waterframe_wastewatertreatmentplant}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#WastewaterTreatmentPlant`

### Labels

- Wastewater treatment plant

### Description

A facility that treats wastewater to produce effluent meeting discharge standards.

Aligned with ENVO:00002043 (wastewater treatment plant) for environmental context

### Superclasses

- [BFO_0000040](#https___ugentbiomath.github.io_waterframe_bfo_0000040)
- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)

### Related Entities

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)


---

## Object Properties

## abstractsFrom {#https___ugentbiomath.github.io_waterframe_abstractsfrom}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#abstractsFrom`

### Labels

- abstracts from

### Description

Links a water system component to the natural water body it draws water from

### Domains

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)

### Ranges

- ENVO_00000063

### Related Entities

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)


---

## affectedByWeather {#https___ugentbiomath.github.io_waterframe_affectedbyweather}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#affectedByWeather`

### Labels

- affected by weather

### Description

Links a water system to weather phenomena that affect it

### Domains

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)

### Ranges

- ENVO_01000810

### Related Entities

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)


---

## affectsEcosystem {#https___ugentbiomath.github.io_waterframe_affectsecosystem}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#affectsEcosystem`

### Labels

- affects ecosystem

### Description

Links a water system or discharge to the aquatic ecosystem it affects

### Domains

- [naa095d1752e441c0b346193ffdab1d7bb5](#https___ugentbiomath.github.io_waterframe_naa095d1752e441c0b346193ffdab1d7bb5)

### Ranges

- ENVO_00000428


---

## dischargesInto {#https___ugentbiomath.github.io_waterframe_dischargesinto}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#dischargesInto`

### Labels

- discharges into

### Description

Links a water system component to the natural water body it discharges into

### Domains

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)

### Ranges

- ENVO_00000063

### Related Entities

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)


---

## hasChemicalConstituent {#https___ugentbiomath.github.io_waterframe_haschemicalconstituent}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasChemicalConstituent`

### Labels

- has chemical constituent

### Description

Links water to its chemical constituents via CHEBI (imported by ENVO)

### Domains

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)

### Ranges

- CHEBI_24431

### Related Entities

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)


---

## hasContaminant {#https___ugentbiomath.github.io_waterframe_hascontaminant}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasContaminant`

### Labels

- has contaminant

### Description

Links to a contaminant present in water

### Domains

- [naa095d1752e441c0b346193ffdab1d7bb1](#https___ugentbiomath.github.io_waterframe_naa095d1752e441c0b346193ffdab1d7bb1)

### Ranges

- ENVO_01000432


---

## hasEnvironmentalQuality {#https___ugentbiomath.github.io_waterframe_hasenvironmentalquality}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasEnvironmentalQuality`

### Labels

- has environmental quality

### Description

Links an entity to its environmental quality (ENVO quality classes)

### Domains

- [ENVO_00000063](#https___ugentbiomath.github.io_waterframe_envo_00000063)

### Ranges

- ENVO_09200000


---

## hasWaterType {#https___ugentbiomath.github.io_waterframe_haswatertype}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasWaterType`

### Labels

- has water type

### Description

Links a water system component to the ENVO water material type it contains or processes

### Domains

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)

### Ranges

- ENVO_00002006

### Related Entities

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)


---

## inUrbanArea {#https___ugentbiomath.github.io_waterframe_inurbanarea}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#inUrbanArea`

### Labels

- in urban area

### Description

Links a water system to its urban context

### Domains

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)

### Ranges

- ENVO_01001116

### Related Entities

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)


---

## locatedIn {#https___ugentbiomath.github.io_waterframe_locatedin}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#locatedIn`

### Labels

- located in

### Description

Links a water system component to its environmental context

### Domains

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)

### Ranges

- ENVO_00000428

### Related Entities

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)


---

## monitorsFeature {#https___ugentbiomath.github.io_waterframe_monitorsfeature}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#monitorsFeature`

### Labels

- monitors feature

### Description

Links a monitoring point to the environmental feature it monitors

### Domains

- [MonitoringPoint](#https___ugentbiomath.github.io_waterframe_monitoringpoint)

### Ranges

- ENVO_00000063

### Related Entities

- [MonitoringPoint](#https___ugentbiomath.github.io_waterframe_monitoringpoint)


---

## observesEnvironmentalFeature {#https___ugentbiomath.github.io_waterframe_observesenvironmentalfeature}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#observesEnvironmentalFeature`

### Labels

- observes environmental feature

### Description

Links a water quality observation to the ENVO environmental feature being observed

### Domains

- [WaterQualityObservation](#https___ugentbiomath.github.io_waterframe_waterqualityobservation)

### Ranges

- ENVO_00000063

### Related Entities

- [WaterQualityObservation](#https___ugentbiomath.github.io_waterframe_waterqualityobservation)


---

## partOfCatchment {#https___ugentbiomath.github.io_waterframe_partofcatchment}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#partOfCatchment`

### Labels

- part of catchment

### Description

Links a component to its containing catchment

### Domains

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)

### Ranges

- Catchment

### Related Entities

- [Catchment](#https___ugentbiomath.github.io_waterframe_catchment)
- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)


---

## supportsEcosystem {#https___ugentbiomath.github.io_waterframe_supportsecosystem}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#supportsEcosystem`

### Labels

- supports ecosystem

### Description

Links a water body to the ecosystem it supports

### Domains

- [ENVO_00000063](#https___ugentbiomath.github.io_waterframe_envo_00000063)

### Ranges

- ENVO_00000428


---

## Datatype Properties

## environmentalContext {#https___ugentbiomath.github.io_waterframe_environmentalcontext}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#environmentalContext`

### Labels

- environmental context

### Description

Textual description of environmental context

### Domains

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)

### Ranges

- string

### Related Entities

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)


---

## envoClassification {#https___ugentbiomath.github.io_waterframe_envoclassification}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#envoClassification`

### Labels

- ENVO classification

### Description

ENVO class URI for environmental classification

### Domains

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)

### Ranges

- anyURI

### Related Entities

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)


---

