# Module: qualities

Water quality parameters and requirements for modeling and regulation. Uses Entity_Feature_Value pattern from Manchester ODPs.

**Module URI:** `https://ugentbiomath.github.io/waterframe/modules/qualities`

**Source:** `ontology/modules/qualities.ttl`

**Total Entities:** 51

## Contents

- [Classes](#classes) (43)
- [Object Properties](#object-properties) (4)
- [Datatype Properties](#datatype-properties) (4)

---

## Classes

## Alkalinity {#https___ugentbiomath.github.io_waterframe_alkalinity}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#Alkalinity`

### Labels

- Alkalinity

### Description

The capacity of water to neutralize acids. Measured as mg/L CaCO3.

### Superclasses

- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)

### Related Entities

- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)


---

## Ammonia {#https___ugentbiomath.github.io_waterframe_ammonia}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#Ammonia`

### Labels

- Ammonia

### Description

Concentration of ammonia (NH3-N). Measured in mg/L.

### Superclasses

- [ObservableProperty](#https___ugentbiomath.github.io_waterframe_observableproperty)
- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)

### Related Entities

- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)


---

## AverageLimit {#https___ugentbiomath.github.io_waterframe_averagelimit}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#AverageLimit`

### Labels

- Average limit

### Description

The average or mean value limit.

### Superclasses

- [LimitType](#https___ugentbiomath.github.io_waterframe_limittype)

### Related Entities

- [LimitType](#https___ugentbiomath.github.io_waterframe_limittype)


---

## BOD {#https___ugentbiomath.github.io_waterframe_bod}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#BOD`

### Labels

- Biochemical Oxygen Demand

### Description

The amount of dissolved oxygen needed by aerobic biological organisms to break down organic matter. Measured in mg/L.

### Superclasses

- [ObservableProperty](#https___ugentbiomath.github.io_waterframe_observableproperty)
- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)

### Related Entities

- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)


---

## Chlorine {#https___ugentbiomath.github.io_waterframe_chlorine}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#Chlorine`

### Labels

- Chlorine

### Description

Residual chlorine concentration. Measured in mg/L.

### Superclasses

- [ObservableProperty](#https___ugentbiomath.github.io_waterframe_observableproperty)
- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)

### Related Entities

- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)


---

## COD {#https___ugentbiomath.github.io_waterframe_cod}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#COD`

### Labels

- Chemical Oxygen Demand

### Description

The oxygen equivalent of the organic matter content. Measured in mg/L.

### Superclasses

- [ObservableProperty](#https___ugentbiomath.github.io_waterframe_observableproperty)
- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)

### Related Entities

- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)


---

## Coliform {#https___ugentbiomath.github.io_waterframe_coliform}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#Coliform`

### Labels

- Coliform

### Description

Concentration of coliform bacteria. Measured as MPN/100mL or CFU/100mL.

### Superclasses

- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)

### Related Entities

- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)


---

## Conductivity {#https___ugentbiomath.github.io_waterframe_conductivity}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#Conductivity`

### Labels

- Conductivity

### Description

The ability of water to conduct electricity, indicating ion concentration. Measured in μS/cm.

### Superclasses

- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)

### Related Entities

- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)


---

## DissolvedOxygen {#https___ugentbiomath.github.io_waterframe_dissolvedoxygen}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#DissolvedOxygen`

### Labels

- Dissolved Oxygen

### Description

The amount of oxygen dissolved in water. Measured in mg/L.

### Superclasses

- [ObservableProperty](#https___ugentbiomath.github.io_waterframe_observableproperty)
- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)

### Related Entities

- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)


---

## EUWaterFrameworkDirective {#https___ugentbiomath.github.io_waterframe_euwaterframeworkdirective}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#EUWaterFrameworkDirective`

### Labels

- EU Water Framework Directive

### Description

European Union Water Framework Directive standards.

### Superclasses

- [RegulatoryStandard](#https___ugentbiomath.github.io_waterframe_regulatorystandard)

### Related Entities

- [RegulatoryStandard](#https___ugentbiomath.github.io_waterframe_regulatorystandard)


---

## ExcellentQuality {#https___ugentbiomath.github.io_waterframe_excellentquality}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#ExcellentQuality`

### Labels

- Excellent quality

### Description

Water of excellent quality, suitable for all uses.

### Superclasses

- [WaterQualityClass](#https___ugentbiomath.github.io_waterframe_waterqualityclass)

### Related Entities

- [WaterQualityClass](#https___ugentbiomath.github.io_waterframe_waterqualityclass)


---

## FairQuality {#https___ugentbiomath.github.io_waterframe_fairquality}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#FairQuality`

### Labels

- Fair quality

### Description

Water of fair quality, treatment may be required for some uses.

### Superclasses

- [WaterQualityClass](#https___ugentbiomath.github.io_waterframe_waterqualityclass)

### Related Entities

- [WaterQualityClass](#https___ugentbiomath.github.io_waterframe_waterqualityclass)


---

## FitForPurpose {#https___ugentbiomath.github.io_waterframe_fitforpurpose}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#FitForPurpose`

### Labels

- Fit-for-purpose classification

### Description

Classification of water by its intended use.

### Subclasses

- [GroundwaterRechargeWater](#https___ugentbiomath.github.io_waterframe_groundwaterrechargewater)
- [IndustrialProcessWater](#https___ugentbiomath.github.io_waterframe_industrialprocesswater)
- [IrrigationWater](#https___ugentbiomath.github.io_waterframe_irrigationwater)
- [LandscapeIrrigationWater](#https___ugentbiomath.github.io_waterframe_landscapeirrigationwater)
- [PotableWater](#https___ugentbiomath.github.io_waterframe_potablewater)
- [ToiletFlushingWater](#https___ugentbiomath.github.io_waterframe_toiletflushingwater)

### Related Entities

- [GroundwaterRechargeWater](#https___ugentbiomath.github.io_waterframe_groundwaterrechargewater)
- [IndustrialProcessWater](#https___ugentbiomath.github.io_waterframe_industrialprocesswater)
- [IrrigationWater](#https___ugentbiomath.github.io_waterframe_irrigationwater)
- [LandscapeIrrigationWater](#https___ugentbiomath.github.io_waterframe_landscapeirrigationwater)
- [PotableWater](#https___ugentbiomath.github.io_waterframe_potablewater)
- [ToiletFlushingWater](#https___ugentbiomath.github.io_waterframe_toiletflushingwater)


---

## GoodQuality {#https___ugentbiomath.github.io_waterframe_goodquality}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#GoodQuality`

### Labels

- Good quality

### Description

Water of good quality, suitable for most uses.

### Superclasses

- [WaterQualityClass](#https___ugentbiomath.github.io_waterframe_waterqualityclass)

### Related Entities

- [WaterQualityClass](#https___ugentbiomath.github.io_waterframe_waterqualityclass)


---

## GroundwaterRechargeWater {#https___ugentbiomath.github.io_waterframe_groundwaterrechargewater}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#GroundwaterRechargeWater`

### Labels

- Groundwater recharge water

### Description

Water suitable for groundwater recharge.

### Superclasses

- [FitForPurpose](#https___ugentbiomath.github.io_waterframe_fitforpurpose)

### Related Entities

- [FitForPurpose](#https___ugentbiomath.github.io_waterframe_fitforpurpose)


---

## IndustrialProcessWater {#https___ugentbiomath.github.io_waterframe_industrialprocesswater}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#IndustrialProcessWater`

### Labels

- Industrial process water

### Description

Water suitable for industrial processes.

### Superclasses

- [FitForPurpose](#https___ugentbiomath.github.io_waterframe_fitforpurpose)

### Related Entities

- [FitForPurpose](#https___ugentbiomath.github.io_waterframe_fitforpurpose)


---

## IrrigationWater {#https___ugentbiomath.github.io_waterframe_irrigationwater}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#IrrigationWater`

### Labels

- Irrigation water

### Description

Water suitable for crop irrigation.

### Superclasses

- [FitForPurpose](#https___ugentbiomath.github.io_waterframe_fitforpurpose)

### Related Entities

- [FitForPurpose](#https___ugentbiomath.github.io_waterframe_fitforpurpose)


---

## LandscapeIrrigationWater {#https___ugentbiomath.github.io_waterframe_landscapeirrigationwater}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#LandscapeIrrigationWater`

### Labels

- Landscape irrigation water

### Description

Water suitable for landscape irrigation.

### Superclasses

- [FitForPurpose](#https___ugentbiomath.github.io_waterframe_fitforpurpose)

### Related Entities

- [FitForPurpose](#https___ugentbiomath.github.io_waterframe_fitforpurpose)


---

## LimitType {#https___ugentbiomath.github.io_waterframe_limittype}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#LimitType`

### Labels

- Limit type

### Description

Classification of water quality limit types.

### Subclasses

- [AnnualAverageLimit](#https___ugentbiomath.github.io_waterframe_annualaveragelimit)
- [AverageLimit](#https___ugentbiomath.github.io_waterframe_averagelimit)
- [ConcentrationLimit](#https___ugentbiomath.github.io_waterframe_concentrationlimit)
- [DailyMaximumLimit](#https___ugentbiomath.github.io_waterframe_dailymaximumlimit)
- [LoadLimit](#https___ugentbiomath.github.io_waterframe_loadlimit)
- [MaximumLimit](#https___ugentbiomath.github.io_waterframe_maximumlimit)
- [MinimumLimit](#https___ugentbiomath.github.io_waterframe_minimumlimit)
- [MonthlyAverageLimit](#https___ugentbiomath.github.io_waterframe_monthlyaveragelimit)
- [PercentRemovalLimit](#https___ugentbiomath.github.io_waterframe_percentremovallimit)
- [RangeLimit](#https___ugentbiomath.github.io_waterframe_rangelimit)
- [TechnologyBasedLimit](#https___ugentbiomath.github.io_waterframe_technologybasedlimit)
- [WaterQualityBasedLimit](#https___ugentbiomath.github.io_waterframe_waterqualitybasedlimit)
- [WeeklyAverageLimit](#https___ugentbiomath.github.io_waterframe_weeklyaveragelimit)

### Related Entities

- [AnnualAverageLimit](#https___ugentbiomath.github.io_waterframe_annualaveragelimit)
- [AverageLimit](#https___ugentbiomath.github.io_waterframe_averagelimit)
- [ConcentrationLimit](#https___ugentbiomath.github.io_waterframe_concentrationlimit)
- [DailyMaximumLimit](#https___ugentbiomath.github.io_waterframe_dailymaximumlimit)
- [LoadLimit](#https___ugentbiomath.github.io_waterframe_loadlimit)
- [MaximumLimit](#https___ugentbiomath.github.io_waterframe_maximumlimit)
- [MinimumLimit](#https___ugentbiomath.github.io_waterframe_minimumlimit)
- [MonthlyAverageLimit](#https___ugentbiomath.github.io_waterframe_monthlyaveragelimit)
- [PercentRemovalLimit](#https___ugentbiomath.github.io_waterframe_percentremovallimit)
- [RangeLimit](#https___ugentbiomath.github.io_waterframe_rangelimit)
- [TechnologyBasedLimit](#https___ugentbiomath.github.io_waterframe_technologybasedlimit)
- [WaterQualityBasedLimit](#https___ugentbiomath.github.io_waterframe_waterqualitybasedlimit)
- [WeeklyAverageLimit](#https___ugentbiomath.github.io_waterframe_weeklyaveragelimit)


---

## MaximumLimit {#https___ugentbiomath.github.io_waterframe_maximumlimit}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#MaximumLimit`

### Labels

- Maximum limit

### Description

The maximum allowed value for a parameter.

### Superclasses

- [LimitType](#https___ugentbiomath.github.io_waterframe_limittype)

### Related Entities

- [LimitType](#https___ugentbiomath.github.io_waterframe_limittype)


---

## MinimumLimit {#https___ugentbiomath.github.io_waterframe_minimumlimit}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#MinimumLimit`

### Labels

- Minimum limit

### Description

The minimum allowed value for a parameter.

### Superclasses

- [LimitType](#https___ugentbiomath.github.io_waterframe_limittype)

### Related Entities

- [LimitType](#https___ugentbiomath.github.io_waterframe_limittype)


---

## Nitrate {#https___ugentbiomath.github.io_waterframe_nitrate}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#Nitrate`

### Labels

- Nitrate

### Description

Concentration of nitrate (NO3-N). Measured in mg/L.

### Superclasses

- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)

### Related Entities

- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)


---

## Nitrite {#https___ugentbiomath.github.io_waterframe_nitrite}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#Nitrite`

### Labels

- Nitrite

### Description

Concentration of nitrite (NO2-N). Measured in mg/L.

### Superclasses

- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)

### Related Entities

- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)


---

## Orthophosphate {#https___ugentbiomath.github.io_waterframe_orthophosphate}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#Orthophosphate`

### Labels

- Orthophosphate

### Description

Concentration of orthophosphate (PO4-P). Measured in mg/L.

### Superclasses

- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)

### Related Entities

- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)


---

## pH {#https___ugentbiomath.github.io_waterframe_ph}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#pH`

### Labels

- pH

### Description

A measure of the acidity or basicity of water. Dimensionless scale 0-14.

### Superclasses

- [ObservableProperty](#https___ugentbiomath.github.io_waterframe_observableproperty)
- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)

### Related Entities

- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)


---

## PoorQuality {#https___ugentbiomath.github.io_waterframe_poorquality}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#PoorQuality`

### Labels

- Poor quality

### Description

Water of poor quality, treatment required for most uses.

### Superclasses

- [WaterQualityClass](#https___ugentbiomath.github.io_waterframe_waterqualityclass)

### Related Entities

- [WaterQualityClass](#https___ugentbiomath.github.io_waterframe_waterqualityclass)


---

## PotableWater {#https___ugentbiomath.github.io_waterframe_potablewater}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#PotableWater`

### Labels

- Potable water

### Description

Water suitable for drinking.

### Superclasses

- [FitForPurpose](#https___ugentbiomath.github.io_waterframe_fitforpurpose)

### Related Entities

- [FitForPurpose](#https___ugentbiomath.github.io_waterframe_fitforpurpose)


---

## RangeLimit {#https___ugentbiomath.github.io_waterframe_rangelimit}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#RangeLimit`

### Labels

- Range limit

### Description

A range of allowed values for a parameter.

### Superclasses

- [LimitType](#https___ugentbiomath.github.io_waterframe_limittype)

### Related Entities

- [LimitType](#https___ugentbiomath.github.io_waterframe_limittype)


---

## RegulatoryStandard {#https___ugentbiomath.github.io_waterframe_regulatorystandard}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#RegulatoryStandard`

### Labels

- Regulatory standard

### Description

A regulatory standard for water quality.

### Superclasses

- [BFO_0000027](#https___ugentbiomath.github.io_waterframe_bfo_0000027)

### Subclasses

- [EUWaterFrameworkDirective](#https___ugentbiomath.github.io_waterframe_euwaterframeworkdirective)
- [USEPAStandard](#https___ugentbiomath.github.io_waterframe_usepastandard)
- [WHOGuideline](#https___ugentbiomath.github.io_waterframe_whoguideline)

### Related Entities

- [EUWaterFrameworkDirective](#https___ugentbiomath.github.io_waterframe_euwaterframeworkdirective)
- [USEPAStandard](#https___ugentbiomath.github.io_waterframe_usepastandard)
- [WHOGuideline](#https___ugentbiomath.github.io_waterframe_whoguideline)


---

## TDS {#https___ugentbiomath.github.io_waterframe_tds}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#TDS`

### Labels

- Total Dissolved Solids

### Description

The total amount of dissolved solids in water. Measured in mg/L.

### Superclasses

- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)

### Related Entities

- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)


---

## Temperature {#https___ugentbiomath.github.io_waterframe_temperature}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#Temperature`

### Labels

- Temperature

### Description

Water temperature. Measured in degrees Celsius.

### Superclasses

- [ObservableProperty](#https___ugentbiomath.github.io_waterframe_observableproperty)
- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)

### Related Entities

- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)


---

## ToiletFlushingWater {#https___ugentbiomath.github.io_waterframe_toiletflushingwater}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#ToiletFlushingWater`

### Labels

- Toilet flushing water

### Description

Water suitable for toilet flushing.

### Superclasses

- [FitForPurpose](#https___ugentbiomath.github.io_waterframe_fitforpurpose)

### Related Entities

- [FitForPurpose](#https___ugentbiomath.github.io_waterframe_fitforpurpose)


---

## TotalNitrogen {#https___ugentbiomath.github.io_waterframe_totalnitrogen}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#TotalNitrogen`

### Labels

- Total Nitrogen

### Description

The total amount of nitrogen in water (organic + inorganic). Measured in mg/L.

### Superclasses

- [ObservableProperty](#https___ugentbiomath.github.io_waterframe_observableproperty)
- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)

### Related Entities

- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)


---

## TotalPhosphorus {#https___ugentbiomath.github.io_waterframe_totalphosphorus}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#TotalPhosphorus`

### Labels

- Total Phosphorus

### Description

The total amount of phosphorus in water. Measured in mg/L.

### Superclasses

- [ObservableProperty](#https___ugentbiomath.github.io_waterframe_observableproperty)
- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)

### Related Entities

- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)


---

## TSS {#https___ugentbiomath.github.io_waterframe_tss}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#TSS`

### Labels

- Total Suspended Solids

### Description

The total amount of solid material suspended in water. Measured in mg/L.

### Superclasses

- [ObservableProperty](#https___ugentbiomath.github.io_waterframe_observableproperty)
- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)

### Related Entities

- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)


---

## Turbidity {#https___ugentbiomath.github.io_waterframe_turbidity}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#Turbidity`

### Labels

- Turbidity

### Description

The cloudiness or haziness of water caused by suspended particles. Measured in NTU.

### Superclasses

- [ObservableProperty](#https___ugentbiomath.github.io_waterframe_observableproperty)
- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)

### Related Entities

- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)


---

## USEPAStandard {#https___ugentbiomath.github.io_waterframe_usepastandard}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#USEPAStandard`

### Labels

- US EPA Standard

### Description

United States Environmental Protection Agency standards.

### Superclasses

- [RegulatoryStandard](#https___ugentbiomath.github.io_waterframe_regulatorystandard)

### Related Entities

- [RegulatoryStandard](#https___ugentbiomath.github.io_waterframe_regulatorystandard)


---

## VeryPoorQuality {#https___ugentbiomath.github.io_waterframe_verypoorquality}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#VeryPoorQuality`

### Labels

- Very poor quality

### Description

Water of very poor quality, limited uses.

### Superclasses

- [WaterQualityClass](#https___ugentbiomath.github.io_waterframe_waterqualityclass)

### Related Entities

- [WaterQualityClass](#https___ugentbiomath.github.io_waterframe_waterqualityclass)


---

## WaterQualityClass {#https___ugentbiomath.github.io_waterframe_waterqualityclass}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#WaterQualityClass`

### Labels

- Water quality class

### Description

A classification of water quality levels.

### Subclasses

- [ExcellentQuality](#https___ugentbiomath.github.io_waterframe_excellentquality)
- [FairQuality](#https___ugentbiomath.github.io_waterframe_fairquality)
- [GoodQuality](#https___ugentbiomath.github.io_waterframe_goodquality)
- [PoorQuality](#https___ugentbiomath.github.io_waterframe_poorquality)
- [VeryPoorQuality](#https___ugentbiomath.github.io_waterframe_verypoorquality)

### Related Entities

- [ExcellentQuality](#https___ugentbiomath.github.io_waterframe_excellentquality)
- [FairQuality](#https___ugentbiomath.github.io_waterframe_fairquality)
- [GoodQuality](#https___ugentbiomath.github.io_waterframe_goodquality)
- [PoorQuality](#https___ugentbiomath.github.io_waterframe_poorquality)
- [VeryPoorQuality](#https___ugentbiomath.github.io_waterframe_verypoorquality)


---

## WaterQualityObservation {#https___ugentbiomath.github.io_waterframe_waterqualityobservation}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#WaterQualityObservation`

### Labels

- Water quality observation

### Description

An observation event where water quality is measured.

An observation event where water quality is measured, aligned with SOSA Observation.

### Superclasses

- [BFO_0000052](#https___ugentbiomath.github.io_waterframe_bfo_0000052)
- [Observation](#https___ugentbiomath.github.io_waterframe_observation)


---

## WaterQualityParameter {#https___ugentbiomath.github.io_waterframe_waterqualityparameter}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#WaterQualityParameter`

### Labels

- Water quality parameter

### Description

A measurable quality or characteristic of water.

### Superclasses

- [BFO_0000019](#https___ugentbiomath.github.io_waterframe_bfo_0000019)
- [ObservableProperty](#https___ugentbiomath.github.io_waterframe_observableproperty)

### Subclasses

- [Alkalinity](#https___ugentbiomath.github.io_waterframe_alkalinity)
- [Ammonia](#https___ugentbiomath.github.io_waterframe_ammonia)
- [BOD](#https___ugentbiomath.github.io_waterframe_bod)
- [COD](#https___ugentbiomath.github.io_waterframe_cod)
- [Chlorine](#https___ugentbiomath.github.io_waterframe_chlorine)
- [Coliform](#https___ugentbiomath.github.io_waterframe_coliform)
- [Conductivity](#https___ugentbiomath.github.io_waterframe_conductivity)
- [DissolvedOxygen](#https___ugentbiomath.github.io_waterframe_dissolvedoxygen)
- [Nitrate](#https___ugentbiomath.github.io_waterframe_nitrate)
- [Nitrite](#https___ugentbiomath.github.io_waterframe_nitrite)
- [Orthophosphate](#https___ugentbiomath.github.io_waterframe_orthophosphate)
- [TDS](#https___ugentbiomath.github.io_waterframe_tds)
- [TSS](#https___ugentbiomath.github.io_waterframe_tss)
- [Temperature](#https___ugentbiomath.github.io_waterframe_temperature)
- [TotalNitrogen](#https___ugentbiomath.github.io_waterframe_totalnitrogen)
- [TotalPhosphorus](#https___ugentbiomath.github.io_waterframe_totalphosphorus)
- [Turbidity](#https___ugentbiomath.github.io_waterframe_turbidity)
- [pH](#https___ugentbiomath.github.io_waterframe_ph)

### Related Entities

- [Alkalinity](#https___ugentbiomath.github.io_waterframe_alkalinity)
- [Ammonia](#https___ugentbiomath.github.io_waterframe_ammonia)
- [BOD](#https___ugentbiomath.github.io_waterframe_bod)
- [COD](#https___ugentbiomath.github.io_waterframe_cod)
- [Chlorine](#https___ugentbiomath.github.io_waterframe_chlorine)
- [Coliform](#https___ugentbiomath.github.io_waterframe_coliform)
- [Conductivity](#https___ugentbiomath.github.io_waterframe_conductivity)
- [DissolvedOxygen](#https___ugentbiomath.github.io_waterframe_dissolvedoxygen)
- [Nitrate](#https___ugentbiomath.github.io_waterframe_nitrate)
- [Nitrite](#https___ugentbiomath.github.io_waterframe_nitrite)
- [Orthophosphate](#https___ugentbiomath.github.io_waterframe_orthophosphate)
- [TDS](#https___ugentbiomath.github.io_waterframe_tds)
- [TSS](#https___ugentbiomath.github.io_waterframe_tss)
- [Temperature](#https___ugentbiomath.github.io_waterframe_temperature)
- [TotalNitrogen](#https___ugentbiomath.github.io_waterframe_totalnitrogen)
- [TotalPhosphorus](#https___ugentbiomath.github.io_waterframe_totalphosphorus)
- [Turbidity](#https___ugentbiomath.github.io_waterframe_turbidity)
- [pH](#https___ugentbiomath.github.io_waterframe_ph)


---

## WaterQualityRequirement {#https___ugentbiomath.github.io_waterframe_waterqualityrequirement}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#WaterQualityRequirement`

### Labels

- Water quality requirement

### Description

A requirement or limit for a water quality parameter (regulatory or operational).

### Superclasses

- [BFO_0000023](#https___ugentbiomath.github.io_waterframe_bfo_0000023)


---

## WHOGuideline {#https___ugentbiomath.github.io_waterframe_whoguideline}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#WHOGuideline`

### Labels

- WHO Guideline

### Description

World Health Organization drinking water guidelines.

### Superclasses

- [RegulatoryStandard](#https___ugentbiomath.github.io_waterframe_regulatorystandard)

### Related Entities

- [RegulatoryStandard](#https___ugentbiomath.github.io_waterframe_regulatorystandard)


---

## Object Properties

## hasLimitType {#https___ugentbiomath.github.io_waterframe_haslimittype}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasLimitType`

### Labels

- has limit type

### Description

The type of limit (maximum, minimum, range, etc.)

### Domains

- [WaterQualityRequirement](#https___ugentbiomath.github.io_waterframe_waterqualityrequirement)

### Ranges

- LimitType

### Related Entities

- [LimitType](#https___ugentbiomath.github.io_waterframe_limittype)
- [WaterQualityRequirement](#https___ugentbiomath.github.io_waterframe_waterqualityrequirement)


---

## hasRegulatoryStandard {#https___ugentbiomath.github.io_waterframe_hasregulatorystandard}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasRegulatoryStandard`

### Labels

- has regulatory standard

### Description

Links a requirement to its regulatory standard

### Domains

- [WaterQualityRequirement](#https___ugentbiomath.github.io_waterframe_waterqualityrequirement)

### Ranges

- RegulatoryStandard

### Related Entities

- [RegulatoryStandard](#https___ugentbiomath.github.io_waterframe_regulatorystandard)
- [WaterQualityRequirement](#https___ugentbiomath.github.io_waterframe_waterqualityrequirement)


---

## hasWaterQualityParameter {#https___ugentbiomath.github.io_waterframe_haswaterqualityparameter}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasWaterQualityParameter`

### Labels

- has water quality parameter

### Description

Links a requirement to the parameter it governs

### Domains

- [WaterQualityRequirement](#https___ugentbiomath.github.io_waterframe_waterqualityrequirement)

### Ranges

- WaterQualityParameter

### Related Entities

- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)
- [WaterQualityRequirement](#https___ugentbiomath.github.io_waterframe_waterqualityrequirement)


---

## observedParameter {#https___ugentbiomath.github.io_waterframe_observedparameter}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#observedParameter`

### Labels

- observed parameter

### Description

Links an observation to the parameter being measured

### Domains

- [WaterQualityObservation](#https___ugentbiomath.github.io_waterframe_waterqualityobservation)

### Ranges

- WaterQualityParameter

### Related Entities

- [WaterQualityObservation](#https___ugentbiomath.github.io_waterframe_waterqualityobservation)
- [WaterQualityParameter](#https___ugentbiomath.github.io_waterframe_waterqualityparameter)


---

## Datatype Properties

## hasLimitValue {#https___ugentbiomath.github.io_waterframe_haslimitvalue}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasLimitValue`

### Labels

- has limit value

### Description

The numeric limit value for the requirement

### Domains

- [WaterQualityRequirement](#https___ugentbiomath.github.io_waterframe_waterqualityrequirement)

### Ranges

- double

### Related Entities

- [WaterQualityRequirement](#https___ugentbiomath.github.io_waterframe_waterqualityrequirement)


---

## observedAt {#https___ugentbiomath.github.io_waterframe_observedat}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#observedAt`

### Labels

- observed at

### Description

The location where the observation was made

### Domains

- [WaterQualityObservation](#https___ugentbiomath.github.io_waterframe_waterqualityobservation)

### Ranges

- string

### Related Entities

- [WaterQualityObservation](#https___ugentbiomath.github.io_waterframe_waterqualityobservation)


---

## observedOn {#https___ugentbiomath.github.io_waterframe_observedon}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#observedOn`

### Labels

- observed on

### Description

The date/time of the observation

### Domains

- [WaterQualityObservation](#https___ugentbiomath.github.io_waterframe_waterqualityobservation)

### Ranges

- dateTime

### Related Entities

- [WaterQualityObservation](#https___ugentbiomath.github.io_waterframe_waterqualityobservation)


---

## observedValue {#https___ugentbiomath.github.io_waterframe_observedvalue}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#observedValue`

### Labels

- observed value

### Description

The numeric value observed

### Domains

- [WaterQualityObservation](#https___ugentbiomath.github.io_waterframe_waterqualityobservation)

### Ranges

- double

### Related Entities

- [WaterQualityObservation](#https___ugentbiomath.github.io_waterframe_waterqualityobservation)


---

