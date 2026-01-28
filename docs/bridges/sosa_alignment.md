# Module: sosa_alignment

Aligns waterFRAME observations with SOSA/SSN sensor ontology.

**Module URI:** `https://ugentbiomath.github.io/waterframe/bridges/sosa_alignment`

**Source:** `ontology/bridges/sosa_alignment.ttl`

**Total Entities:** 30

## Contents

- [Classes](#classes) (22)
- [Object Properties](#object-properties) (4)
- [Datatype Properties](#datatype-properties) (4)

---

## Classes

## AirTemperature {#https___ugentbiomath.github.io_waterframe_airtemperature}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#AirTemperature`

### Labels

- Air temperature

### Description

Air temperature measurement. Measured in degrees Celsius.

### Superclasses

- [ObservableProperty](#https___ugentbiomath.github.io_waterframe_observableproperty)


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

## FlowRate {#https___ugentbiomath.github.io_waterframe_flowrate}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#FlowRate`

### Labels

- Flow rate

### Description

Water flow rate measurement. Measured in cubic meters per second or per day.

### Superclasses

- [ObservableProperty](#https___ugentbiomath.github.io_waterframe_observableproperty)


---

## FlowSensor {#https___ugentbiomath.github.io_waterframe_flowsensor}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#FlowSensor`

### Labels

- Flow sensor

### Description

A sensor that measures water flow rate.

### Superclasses

- [Sensor](#https___ugentbiomath.github.io_waterframe_sensor)


---

## Nowcast {#https___ugentbiomath.github.io_waterframe_nowcast}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#Nowcast`

### Labels

- Nowcast

### Description

Short-term weather forecast (0-1 hour ahead).

### Superclasses

- [WeatherForecast](#https___ugentbiomath.github.io_waterframe_weatherforecast)

### Related Entities

- [WeatherForecast](#https___ugentbiomath.github.io_waterframe_weatherforecast)


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

## Precipitation {#https___ugentbiomath.github.io_waterframe_precipitation}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#Precipitation`

### Labels

- Precipitation

### Description

Liquid precipitation measurement. Measured in millimeters.

### Superclasses

- [ObservableProperty](#https___ugentbiomath.github.io_waterframe_observableproperty)


---

## ShortTermForecast {#https___ugentbiomath.github.io_waterframe_shorttermforecast}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#ShortTermForecast`

### Labels

- Short-term forecast

### Description

Weather forecast (1-24 hours ahead).

### Superclasses

- [WeatherForecast](#https___ugentbiomath.github.io_waterframe_weatherforecast)

### Related Entities

- [WeatherForecast](#https___ugentbiomath.github.io_waterframe_weatherforecast)


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

## WaterQualitySensor {#https___ugentbiomath.github.io_waterframe_waterqualitysensor}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#WaterQualitySensor`

### Labels

- Water quality sensor

### Description

A sensor that measures water quality parameters.

### Superclasses

- [Sensor](#https___ugentbiomath.github.io_waterframe_sensor)


---

## WeatherForecast {#https___ugentbiomath.github.io_waterframe_weatherforecast}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#WeatherForecast`

### Labels

- Weather forecast

### Description

A prediction of future weather conditions.

### Superclasses

- [BFO_0000052](#https___ugentbiomath.github.io_waterframe_bfo_0000052)

### Subclasses

- [Nowcast](#https___ugentbiomath.github.io_waterframe_nowcast)
- [ShortTermForecast](#https___ugentbiomath.github.io_waterframe_shorttermforecast)

### Related Entities

- [Nowcast](#https___ugentbiomath.github.io_waterframe_nowcast)
- [ShortTermForecast](#https___ugentbiomath.github.io_waterframe_shorttermforecast)


---

## WeatherSensor {#https___ugentbiomath.github.io_waterframe_weathersensor}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#WeatherSensor`

### Labels

- Weather sensor

### Description

A sensor that measures weather conditions.

### Superclasses

- [Sensor](#https___ugentbiomath.github.io_waterframe_sensor)


---

## Object Properties

## attachedTo {#https___ugentbiomath.github.io_waterframe_attachedto}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#attachedTo`

### Labels

- attached to

### Description

Links a sensor to the water system component it's attached to.

### Domains

- [Sensor](#https___ugentbiomath.github.io_waterframe_sensor)

### Ranges

- WaterSystemComponent

### Related Entities

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)


---

## hasForecast {#https___ugentbiomath.github.io_waterframe_hasforecast}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasForecast`

### Labels

- has forecast

### Description

Links a weather sensor to its forecasts.

### Domains

- [WeatherSensor](#https___ugentbiomath.github.io_waterframe_weathersensor)

### Ranges

- WeatherForecast

### Related Entities

- [WeatherForecast](#https___ugentbiomath.github.io_waterframe_weatherforecast)
- [WeatherSensor](#https___ugentbiomath.github.io_waterframe_weathersensor)


---

## hasSensorReading {#https___ugentbiomath.github.io_waterframe_hassensorreading}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasSensorReading`

### Labels

- has sensor reading

### Description

Links a sensor to its readings (inverse of sosa:madeObservation).

### Domains

- [Sensor](#https___ugentbiomath.github.io_waterframe_sensor)

### Ranges

- Observation

### Inverse Properties

- [madeObservation](#https___ugentbiomath.github.io_waterframe_madeobservation)


---

## monitorsPort {#https___ugentbiomath.github.io_waterframe_monitorsport}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#monitorsPort`

### Labels

- monitors port

### Description

Links a sensor to port it monitors (OntoCAPE pattern).

### Domains

- [Sensor](#https___ugentbiomath.github.io_waterframe_sensor)

### Ranges

- Port

### Related Entities

- [Port](#https___ugentbiomath.github.io_waterframe_port)


---

## Datatype Properties

## confidence {#https___ugentbiomath.github.io_waterframe_confidence}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#confidence`

### Labels

- confidence

### Description

Forecast confidence level (0-1).

### Domains

- [WeatherForecast](#https___ugentbiomath.github.io_waterframe_weatherforecast)

### Ranges

- double

### Related Entities

- [WeatherForecast](#https___ugentbiomath.github.io_waterframe_weatherforecast)


---

## forecastHorizon {#https___ugentbiomath.github.io_waterframe_forecasthorizon}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#forecastHorizon`

### Labels

- forecast horizon

### Description

How far ahead forecast is (e.g., PT1H for 1 hour).

### Domains

- [WeatherForecast](#https___ugentbiomath.github.io_waterframe_weatherforecast)

### Ranges

- duration

### Related Entities

- [WeatherForecast](#https___ugentbiomath.github.io_waterframe_weatherforecast)


---

## forecastTime {#https___ugentbiomath.github.io_waterframe_forecasttime}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#forecastTime`

### Labels

- forecast time

### Description

The time for which forecast is valid.

### Domains

- [WeatherForecast](#https___ugentbiomath.github.io_waterframe_weatherforecast)

### Ranges

- dateTime

### Related Entities

- [WeatherForecast](#https___ugentbiomath.github.io_waterframe_weatherforecast)


---

## hasSamplingRate {#https___ugentbiomath.github.io_waterframe_hassamplingrate}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasSamplingRate`

### Labels

- has sampling rate

### Description

The sampling frequency of sensor in Hz (readings per second).

### Domains

- [Sensor](#https___ugentbiomath.github.io_waterframe_sensor)

### Ranges

- double


---

