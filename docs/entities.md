# Ontology Entities

This document contains all entities defined in the ontEAUlogy ontology.

## Table of Contents

- [AgriculturalReuse](#http___example.org_onteaulogy_agriculturalreuse)
- [CropIrrigation](#http___example.org_onteaulogy_cropirrigation)
- [Disinfection](#http___example.org_onteaulogy_disinfection)
- [Filtration](#http___example.org_onteaulogy_filtration)
- [Groundwater](#http___example.org_onteaulogy_groundwater)
- [hasApplication](#http___example.org_onteaulogy_hasapplication)
- [hasQualityParameter](#http___example.org_onteaulogy_hasqualityparameter)
- [hasSource](#http___example.org_onteaulogy_hassource)
- [IndustrialCooling](#http___example.org_onteaulogy_industrialcooling)
- [IndustrialReuse](#http___example.org_onteaulogy_industrialreuse)
- [LakeWater](#http___example.org_onteaulogy_lakewater)
- [MunicipalWastewater](#http___example.org_onteaulogy_municipalwastewater)
- [parameterUnit](#http___example.org_onteaulogy_parameterunit)
- [parameterValue](#http___example.org_onteaulogy_parametervalue)
- [pH](#http___example.org_onteaulogy_ph)
- [pH_Parameter](#http___example.org_onteaulogy_ph_parameter)
- [processEfficiency](#http___example.org_onteaulogy_processefficiency)
- [ReuseApplication](#http___example.org_onteaulogy_reuseapplication)
- [RiverWater](#http___example.org_onteaulogy_riverwater)
- [SandFiltration](#http___example.org_onteaulogy_sandfiltration)
- [SurfaceWater](#http___example.org_onteaulogy_surfacewater)
- [TreatmentProcess](#http___example.org_onteaulogy_treatmentprocess)
- [Turbidity](#http___example.org_onteaulogy_turbidity)
- [Turbidity_Parameter](#http___example.org_onteaulogy_turbidity_parameter)
- [usesTreatmentProcess](#http___example.org_onteaulogy_usestreatmentprocess)
- [UVDisinfection](#http___example.org_onteaulogy_uvdisinfection)
- [Wastewater](#http___example.org_onteaulogy_wastewater)
- [WaterQualityParameter](#http___example.org_onteaulogy_waterqualityparameter)
- [WaterSource](#http___example.org_onteaulogy_watersource)

---

## AgriculturalReuse {#http___example.org_onteaulogy_agriculturalreuse}

**Type:** Class

**URI:** `http://example.org/onteaulogy#AgriculturalReuse`

### Labels

- Agricultural Reuse

### Description

Use of treated water for agricultural irrigation

### Superclasses

- [ReuseApplication](#http___example.org_onteaulogy_reuseapplication)

### Instances

- [CropIrrigation](#http___example.org_onteaulogy_cropirrigation)

### Related Entities

- [CropIrrigation](#http___example.org_onteaulogy_cropirrigation)
- [ReuseApplication](#http___example.org_onteaulogy_reuseapplication)


---

## CropIrrigation {#http___example.org_onteaulogy_cropirrigation}

**Type:** Individual

**URI:** `http://example.org/onteaulogy#CropIrrigation`

### Labels

- Crop Irrigation

### Description

Use of treated water for irrigating agricultural crops

### Instance Of

- [AgriculturalReuse](#http___example.org_onteaulogy_agriculturalreuse)

### Property Values

- **type**: `AgriculturalReuse`
- **type**: `NamedIndividual`
- **type**: `AgriculturalReuse`
- **type**: `NamedIndividual`
- **label**: Crop Irrigation
- **comment**: Use of treated water for irrigating agricultural crops

### Related Entities

- [AgriculturalReuse](#http___example.org_onteaulogy_agriculturalreuse)


---

## Disinfection {#http___example.org_onteaulogy_disinfection}

**Type:** Class

**URI:** `http://example.org/onteaulogy#Disinfection`

### Labels

- Disinfection

### Description

Process to eliminate harmful microorganisms

### Superclasses

- [TreatmentProcess](#http___example.org_onteaulogy_treatmentprocess)

### Instances

- [UVDisinfection](#http___example.org_onteaulogy_uvdisinfection)

### Related Entities

- [TreatmentProcess](#http___example.org_onteaulogy_treatmentprocess)
- [UVDisinfection](#http___example.org_onteaulogy_uvdisinfection)


---

## Filtration {#http___example.org_onteaulogy_filtration}

**Type:** Class

**URI:** `http://example.org/onteaulogy#Filtration`

### Labels

- Filtration

### Description

Physical process to remove particles from water

### Superclasses

- [TreatmentProcess](#http___example.org_onteaulogy_treatmentprocess)

### Instances

- [SandFiltration](#http___example.org_onteaulogy_sandfiltration)

### Related Entities

- [SandFiltration](#http___example.org_onteaulogy_sandfiltration)
- [TreatmentProcess](#http___example.org_onteaulogy_treatmentprocess)


---

## Groundwater {#http___example.org_onteaulogy_groundwater}

**Type:** Class

**URI:** `http://example.org/onteaulogy#Groundwater`

### Labels

- Groundwater

### Description

Water from underground aquifers and wells

### Superclasses

- [WaterSource](#http___example.org_onteaulogy_watersource)

### Related Entities

- [WaterSource](#http___example.org_onteaulogy_watersource)


---

## hasApplication {#http___example.org_onteaulogy_hasapplication}

**Type:** Object Property

**URI:** `http://example.org/onteaulogy#hasApplication`

### Labels

- has application

### Description

Relates treated water to its reuse applications

### Domains

- [TreatmentProcess](#http___example.org_onteaulogy_treatmentprocess)

### Ranges

- ReuseApplication

### Related Entities

- [ReuseApplication](#http___example.org_onteaulogy_reuseapplication)
- [TreatmentProcess](#http___example.org_onteaulogy_treatmentprocess)


---

## hasQualityParameter {#http___example.org_onteaulogy_hasqualityparameter}

**Type:** Object Property

**URI:** `http://example.org/onteaulogy#hasQualityParameter`

### Labels

- has quality parameter

### Description

Relates a water source to its quality parameters

### Domains

- [WaterSource](#http___example.org_onteaulogy_watersource)

### Ranges

- WaterQualityParameter

### Related Entities

- [WaterQualityParameter](#http___example.org_onteaulogy_waterqualityparameter)
- [WaterSource](#http___example.org_onteaulogy_watersource)


---

## hasSource {#http___example.org_onteaulogy_hassource}

**Type:** Object Property

**URI:** `http://example.org/onteaulogy#hasSource`

### Labels

- has source

### Description

Relates a system to its water source

### Domains

- [WaterSource](#http___example.org_onteaulogy_watersource)

### Ranges

- WaterSource

### Characteristics

- Functional

### Related Entities

- [WaterSource](#http___example.org_onteaulogy_watersource)


---

## IndustrialCooling {#http___example.org_onteaulogy_industrialcooling}

**Type:** Individual

**URI:** `http://example.org/onteaulogy#IndustrialCooling`

### Labels

- Industrial Cooling

### Description

Use of treated water for industrial cooling processes

### Instance Of

- [IndustrialReuse](#http___example.org_onteaulogy_industrialreuse)

### Property Values

- **type**: `IndustrialReuse`
- **type**: `NamedIndividual`
- **type**: `IndustrialReuse`
- **type**: `NamedIndividual`
- **label**: Industrial Cooling
- **comment**: Use of treated water for industrial cooling processes

### Related Entities

- [IndustrialReuse](#http___example.org_onteaulogy_industrialreuse)


---

## IndustrialReuse {#http___example.org_onteaulogy_industrialreuse}

**Type:** Class

**URI:** `http://example.org/onteaulogy#IndustrialReuse`

### Labels

- Industrial Reuse

### Description

Use of treated water in industrial processes

### Superclasses

- [ReuseApplication](#http___example.org_onteaulogy_reuseapplication)

### Instances

- [IndustrialCooling](#http___example.org_onteaulogy_industrialcooling)

### Related Entities

- [IndustrialCooling](#http___example.org_onteaulogy_industrialcooling)
- [ReuseApplication](#http___example.org_onteaulogy_reuseapplication)


---

## LakeWater {#http___example.org_onteaulogy_lakewater}

**Type:** Individual

**URI:** `http://example.org/onteaulogy#LakeWater`

### Labels

- Lake Water

### Description

Water sourced from lakes and reservoirs

### Instance Of

- [SurfaceWater](#http___example.org_onteaulogy_surfacewater)

### Property Values

- **type**: `SurfaceWater`
- **type**: `NamedIndividual`
- **type**: `SurfaceWater`
- **type**: `NamedIndividual`
- **label**: Lake Water
- **comment**: Water sourced from lakes and reservoirs

### Related Entities

- [SurfaceWater](#http___example.org_onteaulogy_surfacewater)


---

## MunicipalWastewater {#http___example.org_onteaulogy_municipalwastewater}

**Type:** Individual

**URI:** `http://example.org/onteaulogy#MunicipalWastewater`

### Labels

- Municipal Wastewater

### Description

Wastewater from municipal sewage systems

### Instance Of

- [Wastewater](#http___example.org_onteaulogy_wastewater)

### Property Values

- **type**: `Wastewater`
- **type**: `NamedIndividual`
- **type**: `Wastewater`
- **type**: `NamedIndividual`
- **label**: Municipal Wastewater
- **comment**: Wastewater from municipal sewage systems

### Related Entities

- [Wastewater](#http___example.org_onteaulogy_wastewater)


---

## parameterUnit {#http___example.org_onteaulogy_parameterunit}

**Type:** Datatype Property

**URI:** `http://example.org/onteaulogy#parameterUnit`

### Labels

- parameter unit

### Description

The unit of measurement for a water quality parameter

### Domains

- [WaterQualityParameter](#http___example.org_onteaulogy_waterqualityparameter)

### Ranges

- string

### Characteristics

- Functional

### Related Entities

- [WaterQualityParameter](#http___example.org_onteaulogy_waterqualityparameter)


---

## parameterValue {#http___example.org_onteaulogy_parametervalue}

**Type:** Datatype Property

**URI:** `http://example.org/onteaulogy#parameterValue`

### Labels

- parameter value

### Description

The measured value of a water quality parameter

### Domains

- [WaterQualityParameter](#http___example.org_onteaulogy_waterqualityparameter)

### Ranges

- float

### Characteristics

- Functional

### Related Entities

- [WaterQualityParameter](#http___example.org_onteaulogy_waterqualityparameter)


---

## pH {#http___example.org_onteaulogy_ph}

**Type:** Class

**URI:** `http://example.org/onteaulogy#pH`

### Labels

- pH

### Description

Measure of acidity or alkalinity

### Superclasses

- [WaterQualityParameter](#http___example.org_onteaulogy_waterqualityparameter)

### Instances

- [pH_Parameter](#http___example.org_onteaulogy_ph_parameter)

### Related Entities

- [WaterQualityParameter](#http___example.org_onteaulogy_waterqualityparameter)
- [pH_Parameter](#http___example.org_onteaulogy_ph_parameter)


---

## pH_Parameter {#http___example.org_onteaulogy_ph_parameter}

**Type:** Individual

**URI:** `http://example.org/onteaulogy#pH_Parameter`

### Labels

- pH Measurement

### Instance Of

- [pH](#http___example.org_onteaulogy_ph)

### Property Values

- **type**: `pH`
- **type**: `NamedIndividual`
- **type**: `pH`
- **type**: `NamedIndividual`
- **label**: pH Measurement
- **parameterValue**: 7.2
- **parameterUnit**: pH units

### Related Entities

- [pH](#http___example.org_onteaulogy_ph)


---

## processEfficiency {#http___example.org_onteaulogy_processefficiency}

**Type:** Datatype Property

**URI:** `http://example.org/onteaulogy#processEfficiency`

### Labels

- process efficiency

### Description

The efficiency rating of a treatment process

### Domains

- [TreatmentProcess](#http___example.org_onteaulogy_treatmentprocess)

### Ranges

- float

### Related Entities

- [TreatmentProcess](#http___example.org_onteaulogy_treatmentprocess)


---

## ReuseApplication {#http___example.org_onteaulogy_reuseapplication}

**Type:** Class

**URI:** `http://example.org/onteaulogy#ReuseApplication`

### Labels

- Reuse Application

### Description

An application or use case for reused water

A specific purpose or application for which treated water is reused.

### Subclasses

- [AgriculturalReuse](#http___example.org_onteaulogy_agriculturalreuse)
- [IndustrialReuse](#http___example.org_onteaulogy_industrialreuse)

### Related Entities

- [AgriculturalReuse](#http___example.org_onteaulogy_agriculturalreuse)
- [IndustrialReuse](#http___example.org_onteaulogy_industrialreuse)


---

## RiverWater {#http___example.org_onteaulogy_riverwater}

**Type:** Individual

**URI:** `http://example.org/onteaulogy#RiverWater`

### Labels

- River Water

### Description

Water sourced from rivers and streams

### Instance Of

- [SurfaceWater](#http___example.org_onteaulogy_surfacewater)

### Property Values

- **type**: `SurfaceWater`
- **type**: `NamedIndividual`
- **type**: `SurfaceWater`
- **type**: `NamedIndividual`
- **label**: River Water
- **comment**: Water sourced from rivers and streams
- **hasQualityParameter**: `pH_Parameter`
- **hasQualityParameter**: `Turbidity_Parameter`
- **hasQualityParameter**: `pH_Parameter`
- **hasQualityParameter**: `Turbidity_Parameter`
- **usesTreatmentProcess**: `SandFiltration`
- **usesTreatmentProcess**: `UVDisinfection`
- **usesTreatmentProcess**: `SandFiltration`
- **usesTreatmentProcess**: `UVDisinfection`

### Related Entities

- [SandFiltration](#http___example.org_onteaulogy_sandfiltration)
- [SurfaceWater](#http___example.org_onteaulogy_surfacewater)
- [Turbidity_Parameter](#http___example.org_onteaulogy_turbidity_parameter)
- [UVDisinfection](#http___example.org_onteaulogy_uvdisinfection)
- [pH_Parameter](#http___example.org_onteaulogy_ph_parameter)


---

## SandFiltration {#http___example.org_onteaulogy_sandfiltration}

**Type:** Individual

**URI:** `http://example.org/onteaulogy#SandFiltration`

### Labels

- Sand Filtration

### Description

Filtration process using sand as the filter medium

### Instance Of

- [Filtration](#http___example.org_onteaulogy_filtration)

### Property Values

- **type**: `Filtration`
- **type**: `NamedIndividual`
- **type**: `Filtration`
- **type**: `NamedIndividual`
- **label**: Sand Filtration
- **comment**: Filtration process using sand as the filter medium
- **processEfficiency**: 0.85
- **hasApplication**: `CropIrrigation`

### Related Entities

- [CropIrrigation](#http___example.org_onteaulogy_cropirrigation)
- [Filtration](#http___example.org_onteaulogy_filtration)


---

## SurfaceWater {#http___example.org_onteaulogy_surfacewater}

**Type:** Class

**URI:** `http://example.org/onteaulogy#SurfaceWater`

### Labels

- Surface Water

### Description

Water from surface sources like rivers, lakes, and reservoirs

### Superclasses

- [WaterSource](#http___example.org_onteaulogy_watersource)

### Instances

- [RiverWater](#http___example.org_onteaulogy_riverwater)
- [LakeWater](#http___example.org_onteaulogy_lakewater)

### Related Entities

- [LakeWater](#http___example.org_onteaulogy_lakewater)
- [RiverWater](#http___example.org_onteaulogy_riverwater)
- [WaterSource](#http___example.org_onteaulogy_watersource)


---

## TreatmentProcess {#http___example.org_onteaulogy_treatmentprocess}

**Type:** Class

**URI:** `http://example.org/onteaulogy#TreatmentProcess`

### Labels

- Treatment Process

### Description

A process used to treat water for reuse

A systematic procedure or method for treating wastewater or other water sources to make them suitable for reuse.

### Subclasses

- [Filtration](#http___example.org_onteaulogy_filtration)
- [Disinfection](#http___example.org_onteaulogy_disinfection)

### Related Entities

- [Disinfection](#http___example.org_onteaulogy_disinfection)
- [Filtration](#http___example.org_onteaulogy_filtration)


---

## Turbidity {#http___example.org_onteaulogy_turbidity}

**Type:** Class

**URI:** `http://example.org/onteaulogy#Turbidity`

### Labels

- Turbidity

### Description

Measure of water clarity

### Superclasses

- [WaterQualityParameter](#http___example.org_onteaulogy_waterqualityparameter)

### Instances

- [Turbidity_Parameter](#http___example.org_onteaulogy_turbidity_parameter)

### Related Entities

- [Turbidity_Parameter](#http___example.org_onteaulogy_turbidity_parameter)
- [WaterQualityParameter](#http___example.org_onteaulogy_waterqualityparameter)


---

## Turbidity_Parameter {#http___example.org_onteaulogy_turbidity_parameter}

**Type:** Individual

**URI:** `http://example.org/onteaulogy#Turbidity_Parameter`

### Labels

- Turbidity Measurement

### Instance Of

- [Turbidity](#http___example.org_onteaulogy_turbidity)

### Property Values

- **type**: `Turbidity`
- **type**: `NamedIndividual`
- **type**: `Turbidity`
- **type**: `NamedIndividual`
- **label**: Turbidity Measurement
- **parameterValue**: 1.5
- **parameterUnit**: NTU

### Related Entities

- [Turbidity](#http___example.org_onteaulogy_turbidity)


---

## usesTreatmentProcess {#http___example.org_onteaulogy_usestreatmentprocess}

**Type:** Object Property

**URI:** `http://example.org/onteaulogy#usesTreatmentProcess`

### Labels

- uses treatment process

### Description

Relates a water source to the treatment processes it undergoes

### Domains

- [WaterSource](#http___example.org_onteaulogy_watersource)

### Ranges

- TreatmentProcess

### Related Entities

- [TreatmentProcess](#http___example.org_onteaulogy_treatmentprocess)
- [WaterSource](#http___example.org_onteaulogy_watersource)


---

## UVDisinfection {#http___example.org_onteaulogy_uvdisinfection}

**Type:** Individual

**URI:** `http://example.org/onteaulogy#UVDisinfection`

### Labels

- UV Disinfection

### Description

Disinfection using ultraviolet light

### Instance Of

- [Disinfection](#http___example.org_onteaulogy_disinfection)

### Property Values

- **type**: `Disinfection`
- **type**: `NamedIndividual`
- **type**: `Disinfection`
- **type**: `NamedIndividual`
- **label**: UV Disinfection
- **comment**: Disinfection using ultraviolet light
- **processEfficiency**: 0.99
- **hasApplication**: `IndustrialCooling`

### Related Entities

- [Disinfection](#http___example.org_onteaulogy_disinfection)
- [IndustrialCooling](#http___example.org_onteaulogy_industrialcooling)


---

## Wastewater {#http___example.org_onteaulogy_wastewater}

**Type:** Class

**URI:** `http://example.org/onteaulogy#Wastewater`

### Labels

- Wastewater

### Description

Water that has been used and requires treatment

### Superclasses

- [WaterSource](#http___example.org_onteaulogy_watersource)

### Instances

- [MunicipalWastewater](#http___example.org_onteaulogy_municipalwastewater)

### Related Entities

- [MunicipalWastewater](#http___example.org_onteaulogy_municipalwastewater)
- [WaterSource](#http___example.org_onteaulogy_watersource)


---

## WaterQualityParameter {#http___example.org_onteaulogy_waterqualityparameter}

**Type:** Class

**URI:** `http://example.org/onteaulogy#WaterQualityParameter`

### Labels

- Water Quality Parameter

### Description

A measurable characteristic of water quality

A specific physical, chemical, or biological characteristic that can be measured to assess water quality.

### Subclasses

- [pH](#http___example.org_onteaulogy_ph)
- [Turbidity](#http___example.org_onteaulogy_turbidity)

### Related Entities

- [Turbidity](#http___example.org_onteaulogy_turbidity)
- [pH](#http___example.org_onteaulogy_ph)


---

## WaterSource {#http___example.org_onteaulogy_watersource}

**Type:** Class

**URI:** `http://example.org/onteaulogy#WaterSource`

### Labels

- Water Source

### Description

A source of water that can be used in water reuse systems

Any natural or artificial source from which water can be obtained for reuse purposes.

### Subclasses

- [SurfaceWater](#http___example.org_onteaulogy_surfacewater)
- [Groundwater](#http___example.org_onteaulogy_groundwater)
- [Wastewater](#http___example.org_onteaulogy_wastewater)

### Related Entities

- [Groundwater](#http___example.org_onteaulogy_groundwater)
- [SurfaceWater](#http___example.org_onteaulogy_surfacewater)
- [Wastewater](#http___example.org_onteaulogy_wastewater)


---

