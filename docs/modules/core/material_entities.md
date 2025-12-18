# Module: material_entities

Physical objects in water reuse systems

**Module URI:** `https://ugentbiomath.github.io/waterframe/modules/core/material_entities`

**Source:** `ontology/modules/core/material_entities.ttl`

**Total Entities:** 22

## Contents

- [Classes](#classes) (22)

---

## Classes

## Appliance {#https___ugentbiomath.github.io_waterframe_appliance}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#Appliance`

### Labels

- Water-using appliance

### Description

Household appliances that use water

### Superclasses

- [WaterUsagePoint](#https___ugentbiomath.github.io_waterframe_waterusagepoint)

### Related Entities

- [WaterUsagePoint](#https___ugentbiomath.github.io_waterframe_waterusagepoint)


---

## BathingFixture {#https___ugentbiomath.github.io_waterframe_bathingfixture}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#BathingFixture`

### Labels

- Bathing fixture

### Description

Fixtures for bathing and showering

### Superclasses

- [WaterUsagePoint](#https___ugentbiomath.github.io_waterframe_waterusagepoint)

### Related Entities

- [WaterUsagePoint](#https___ugentbiomath.github.io_waterframe_waterusagepoint)


---

## BlackwaterStorageTank {#https___ugentbiomath.github.io_waterframe_blackwaterstoragetank}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#BlackwaterStorageTank`

### Labels

- Blackwater storage tank

### Description

Tank for storing blackwater (toilet waste)

### Superclasses

- [StorageTank](#https___ugentbiomath.github.io_waterframe_storagetank)

### Related Entities

- [StorageTank](#https___ugentbiomath.github.io_waterframe_storagetank)


---

## CleaningFixture {#https___ugentbiomath.github.io_waterframe_cleaningfixture}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#CleaningFixture`

### Labels

- Cleaning fixture

### Description

Fixtures for cleaning activities

### Superclasses

- [WaterUsagePoint](#https___ugentbiomath.github.io_waterframe_waterusagepoint)

### Related Entities

- [WaterUsagePoint](#https___ugentbiomath.github.io_waterframe_waterusagepoint)


---

## Conveyance {#https___ugentbiomath.github.io_waterframe_conveyance}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#Conveyance`

### Labels

- Conveyance system

### Description

Physical infrastructure for water transport between components

### Superclasses

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)

### Related Entities

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)


---

## Household {#https___ugentbiomath.github.io_waterframe_household}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#Household`

### Labels

- Household

### Description

A dwelling or building containing water system components

### Superclasses

- [BFO_0000040](#https___ugentbiomath.github.io_waterframe_bfo_0000040)


---

## InfiltrationUnit {#https___ugentbiomath.github.io_waterframe_infiltrationunit}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#InfiltrationUnit`

### Labels

- Infiltration unit

### Description

Physical system for subsurface water infiltration

### Superclasses

- [TreatmentUnit](#https___ugentbiomath.github.io_waterframe_treatmentunit)

### Related Entities

- [TreatmentUnit](#https___ugentbiomath.github.io_waterframe_treatmentunit)


---

## InputPort {#https___ugentbiomath.github.io_waterframe_inputport}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#InputPort`

### Labels

- Input port

### Description

Port through which material enters a component

### Superclasses

- [Port](#https___ugentbiomath.github.io_waterframe_port)
- [Port](#https___ugentbiomath.github.io_waterframe_port)

### Related Entities

- [Port](#https___ugentbiomath.github.io_waterframe_port)


---

## MembraneBioreactorUnit {#https___ugentbiomath.github.io_waterframe_membranebioreactorunit}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#MembraneBioreactorUnit`

### Labels

- Membrane bioreactor unit

### Description

Physical MBR system for biological treatment and membrane filtration

### Superclasses

- [TreatmentUnit](#https___ugentbiomath.github.io_waterframe_treatmentunit)

### Related Entities

- [TreatmentUnit](#https___ugentbiomath.github.io_waterframe_treatmentunit)


---

## OutputPort {#https___ugentbiomath.github.io_waterframe_outputport}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#OutputPort`

### Labels

- Output port

### Description

Port through which material exits a component

### Superclasses

- [Port](#https___ugentbiomath.github.io_waterframe_port)
- [Port](#https___ugentbiomath.github.io_waterframe_port)

### Related Entities

- [Port](#https___ugentbiomath.github.io_waterframe_port)


---

## Port {#https___ugentbiomath.github.io_waterframe_port}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#Port`

### Labels

- Connection port

### Description

Physical interface point on a water system component through which material flow occurs. Based on OntoCAPE terminal/port concept (Marquardt et al. 2010).

### Superclasses

- [BFO_0000040](#https___ugentbiomath.github.io_waterframe_bfo_0000040)
- [BFO_0000040](#https___ugentbiomath.github.io_waterframe_bfo_0000040)

### Subclasses

- [InputPort](#https___ugentbiomath.github.io_waterframe_inputport)
- [OutputPort](#https___ugentbiomath.github.io_waterframe_outputport)
- [InputPort](#https___ugentbiomath.github.io_waterframe_inputport)
- [OutputPort](#https___ugentbiomath.github.io_waterframe_outputport)

### Related Entities

- [InputPort](#https___ugentbiomath.github.io_waterframe_inputport)
- [OutputPort](#https___ugentbiomath.github.io_waterframe_outputport)


---

## PotableWaterStorageTank {#https___ugentbiomath.github.io_waterframe_potablewaterstoragetank}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#PotableWaterStorageTank`

### Labels

- Potable water storage tank

### Description

Tank for storing drinking water

### Superclasses

- [StorageTank](#https___ugentbiomath.github.io_waterframe_storagetank)

### Related Entities

- [StorageTank](#https___ugentbiomath.github.io_waterframe_storagetank)


---

## PurifiedGreywaterStorageTank {#https___ugentbiomath.github.io_waterframe_purifiedgreywaterstoragetank}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#PurifiedGreywaterStorageTank`

### Labels

- Purified greywater storage tank

### Description

Tank for storing treated greywater for reuse

### Superclasses

- [StorageTank](#https___ugentbiomath.github.io_waterframe_storagetank)

### Related Entities

- [StorageTank](#https___ugentbiomath.github.io_waterframe_storagetank)


---

## RainwaterCollectionSystem {#https___ugentbiomath.github.io_waterframe_rainwatercollectionsystem}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#RainwaterCollectionSystem`

### Labels

- Rainwater collection system

### Description

Infrastructure for collecting rainwater (roof, gutters, collection)

### Superclasses

- [WaterSource](#https___ugentbiomath.github.io_waterframe_watersource)

### Related Entities

- [WaterSource](#https___ugentbiomath.github.io_waterframe_watersource)


---

## RainwaterStorageTank {#https___ugentbiomath.github.io_waterframe_rainwaterstoragetank}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#RainwaterStorageTank`

### Labels

- Rainwater storage tank

### Description

Tank specifically for collecting and storing rainwater

### Superclasses

- [StorageTank](#https___ugentbiomath.github.io_waterframe_storagetank)

### Related Entities

- [StorageTank](#https___ugentbiomath.github.io_waterframe_storagetank)


---

## ReverseOsmosisUnit {#https___ugentbiomath.github.io_waterframe_reverseosmosisunit}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#ReverseOsmosisUnit`

### Labels

- Reverse osmosis unit

### Description

Physical RO system for advanced water purification

### Superclasses

- [TreatmentUnit](#https___ugentbiomath.github.io_waterframe_treatmentunit)

### Related Entities

- [TreatmentUnit](#https___ugentbiomath.github.io_waterframe_treatmentunit)


---

## StorageTank {#https___ugentbiomath.github.io_waterframe_storagetank}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#StorageTank`

### Labels

- Storage tank

### Description

Vessel for storing water of various types

### Superclasses

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)

### Subclasses

- [RainwaterStorageTank](#https___ugentbiomath.github.io_waterframe_rainwaterstoragetank)
- [PotableWaterStorageTank](#https___ugentbiomath.github.io_waterframe_potablewaterstoragetank)
- [PurifiedGreywaterStorageTank](#https___ugentbiomath.github.io_waterframe_purifiedgreywaterstoragetank)
- [BlackwaterStorageTank](#https___ugentbiomath.github.io_waterframe_blackwaterstoragetank)

### Related Entities

- [BlackwaterStorageTank](#https___ugentbiomath.github.io_waterframe_blackwaterstoragetank)
- [PotableWaterStorageTank](#https___ugentbiomath.github.io_waterframe_potablewaterstoragetank)
- [PurifiedGreywaterStorageTank](#https___ugentbiomath.github.io_waterframe_purifiedgreywaterstoragetank)
- [RainwaterStorageTank](#https___ugentbiomath.github.io_waterframe_rainwaterstoragetank)
- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)


---

## Toilet {#https___ugentbiomath.github.io_waterframe_toilet}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#Toilet`

### Labels

- Toilet

### Description

Sanitary fixture for human waste disposal

### Superclasses

- [WaterUsagePoint](#https___ugentbiomath.github.io_waterframe_waterusagepoint)

### Related Entities

- [WaterUsagePoint](#https___ugentbiomath.github.io_waterframe_waterusagepoint)


---

## TreatmentUnit {#https___ugentbiomath.github.io_waterframe_treatmentunit}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#TreatmentUnit`

### Labels

- Treatment unit

### Description

Physical infrastructure for water treatment processes

### Superclasses

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)

### Subclasses

- [MembraneBioreactorUnit](#https___ugentbiomath.github.io_waterframe_membranebioreactorunit)
- [ReverseOsmosisUnit](#https___ugentbiomath.github.io_waterframe_reverseosmosisunit)
- [InfiltrationUnit](#https___ugentbiomath.github.io_waterframe_infiltrationunit)

### Related Entities

- [InfiltrationUnit](#https___ugentbiomath.github.io_waterframe_infiltrationunit)
- [MembraneBioreactorUnit](#https___ugentbiomath.github.io_waterframe_membranebioreactorunit)
- [ReverseOsmosisUnit](#https___ugentbiomath.github.io_waterframe_reverseosmosisunit)
- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)


---

## WaterSource {#https___ugentbiomath.github.io_waterframe_watersource}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#WaterSource`

### Labels

- Water source

### Description

Physical infrastructure for water collection

### Superclasses

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)

### Subclasses

- [RainwaterCollectionSystem](#https___ugentbiomath.github.io_waterframe_rainwatercollectionsystem)

### Related Entities

- [RainwaterCollectionSystem](#https___ugentbiomath.github.io_waterframe_rainwatercollectionsystem)
- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)


---

## WaterSystemComponent {#https___ugentbiomath.github.io_waterframe_watersystemcomponent}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#WaterSystemComponent`

### Labels

- Water system component

### Description

Any physical object that is part of a water system

### Superclasses

- [BFO_0000040](#https___ugentbiomath.github.io_waterframe_bfo_0000040)

### Subclasses

- [StorageTank](#https___ugentbiomath.github.io_waterframe_storagetank)
- [TreatmentUnit](#https___ugentbiomath.github.io_waterframe_treatmentunit)
- [WaterUsagePoint](#https___ugentbiomath.github.io_waterframe_waterusagepoint)
- [WaterSource](#https___ugentbiomath.github.io_waterframe_watersource)
- [Conveyance](#https___ugentbiomath.github.io_waterframe_conveyance)

### Related Entities

- [Conveyance](#https___ugentbiomath.github.io_waterframe_conveyance)
- [StorageTank](#https___ugentbiomath.github.io_waterframe_storagetank)
- [TreatmentUnit](#https___ugentbiomath.github.io_waterframe_treatmentunit)
- [WaterSource](#https___ugentbiomath.github.io_waterframe_watersource)
- [WaterUsagePoint](#https___ugentbiomath.github.io_waterframe_waterusagepoint)


---

## WaterUsagePoint {#https___ugentbiomath.github.io_waterframe_waterusagepoint}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#WaterUsagePoint`

### Labels

- Water usage point

### Description

Physical fixture or appliance where water is used

### Superclasses

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)

### Subclasses

- [BathingFixture](#https___ugentbiomath.github.io_waterframe_bathingfixture)
- [CleaningFixture](#https___ugentbiomath.github.io_waterframe_cleaningfixture)
- [Appliance](#https___ugentbiomath.github.io_waterframe_appliance)
- [Toilet](#https___ugentbiomath.github.io_waterframe_toilet)

### Related Entities

- [Appliance](#https___ugentbiomath.github.io_waterframe_appliance)
- [BathingFixture](#https___ugentbiomath.github.io_waterframe_bathingfixture)
- [CleaningFixture](#https___ugentbiomath.github.io_waterframe_cleaningfixture)
- [Toilet](#https___ugentbiomath.github.io_waterframe_toilet)
- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)


---

