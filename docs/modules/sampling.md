# Module: sampling

Classes and properties for water sampling metadata, including samples, sampling points, and sampling methods. Adapted from WHOKG observation patterns for regulatory compliance support.

**Module URI:** `https://ugentbiomath.github.io/waterframe/modules/sampling`

**Source:** `ontology/modules/sampling.ttl`

**Total Entities:** 43

## Contents

- [Classes](#classes) (24)
- [Object Properties](#object-properties) (10)
- [Datatype Properties](#datatype-properties) (9)

---

## Classes

## AmbientSamplingPoint {#https___ugentbiomath.github.io_waterframe_ambientsamplingpoint}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#AmbientSamplingPoint`

### Labels

- Ambient sampling point

### Description

Sampling point in ambient water body (river, lake, groundwater).

### Superclasses

- [SamplingPoint](#https___ugentbiomath.github.io_waterframe_samplingpoint)

### Related Entities

- [SamplingPoint](#https___ugentbiomath.github.io_waterframe_samplingpoint)


---

## AutomatedSampling {#https___ugentbiomath.github.io_waterframe_automatedsampling}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#AutomatedSampling`

### Labels

- Automated sampling

### Description

Sample collected by automated equipment (autosampler).

### Superclasses

- [SamplingMethod](#https___ugentbiomath.github.io_waterframe_samplingmethod)

### Related Entities

- [SamplingMethod](#https___ugentbiomath.github.io_waterframe_samplingmethod)


---

## Autosampler {#https___ugentbiomath.github.io_waterframe_autosampler}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#Autosampler`

### Labels

- Autosampler

### Description

Automated device for collecting water samples at programmed intervals.

### Superclasses

- [SamplingEquipment](#https___ugentbiomath.github.io_waterframe_samplingequipment)

### Related Entities

- [SamplingEquipment](#https___ugentbiomath.github.io_waterframe_samplingequipment)


---

## BypassFlow {#https___ugentbiomath.github.io_waterframe_bypassflow}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#BypassFlow`

### Labels

- Bypass flow

### Description

Water bypassing normal treatment (e.g., during high flow events).

### Superclasses

- [FlowDirection](#https___ugentbiomath.github.io_waterframe_flowdirection)

### Related Entities

- [FlowDirection](#https___ugentbiomath.github.io_waterframe_flowdirection)


---

## CompositeSampling {#https___ugentbiomath.github.io_waterframe_compositesampling}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#CompositeSampling`

### Labels

- Composite sampling

### Description

A sample composed of multiple aliquots collected over time or at multiple locations. Provides a time-weighted or flow-weighted average.

### Superclasses

- [SamplingMethod](#https___ugentbiomath.github.io_waterframe_samplingmethod)

### Subclasses

- [FlowCompositeSampling](#https___ugentbiomath.github.io_waterframe_flowcompositesampling)
- [TimeCompositeSampling](#https___ugentbiomath.github.io_waterframe_timecompositesampling)

### Related Entities

- [FlowCompositeSampling](#https___ugentbiomath.github.io_waterframe_flowcompositesampling)
- [SamplingMethod](#https___ugentbiomath.github.io_waterframe_samplingmethod)
- [TimeCompositeSampling](#https___ugentbiomath.github.io_waterframe_timecompositesampling)


---

## ContinuousSampling {#https___ugentbiomath.github.io_waterframe_continuoussampling}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#ContinuousSampling`

### Labels

- Continuous sampling

### Description

Continuous monitoring with online sensors.

### Superclasses

- [SamplingMethod](#https___ugentbiomath.github.io_waterframe_samplingmethod)

### Related Entities

- [SamplingMethod](#https___ugentbiomath.github.io_waterframe_samplingmethod)


---

## DischargeMeasurement {#https___ugentbiomath.github.io_waterframe_dischargemeasurement}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#DischargeMeasurement`

### Labels

- Discharge measurement

### Description

A measurement event for water discharge rate. Required for load-based limit calculations.

### Superclasses

- [BFO_0000015](#https___ugentbiomath.github.io_waterframe_bfo_0000015)


---

## DischargePoint {#https___ugentbiomath.github.io_waterframe_dischargepoint}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#DischargePoint`

### Labels

- Discharge point

### Description

A regulatory discharge point (outfall) where treated water is released to receiving waters. Subject to permit monitoring requirements.

### Superclasses

- [SamplingPoint](#https___ugentbiomath.github.io_waterframe_samplingpoint)

### Related Entities

- [SamplingPoint](#https___ugentbiomath.github.io_waterframe_samplingpoint)


---

## EffluentFlow {#https___ugentbiomath.github.io_waterframe_effluentflow}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#EffluentFlow`

### Labels

- Effluent

### Description

Water flowing out of a treatment system or unit process.

### Superclasses

- [FlowDirection](#https___ugentbiomath.github.io_waterframe_flowdirection)

### Related Entities

- [FlowDirection](#https___ugentbiomath.github.io_waterframe_flowdirection)


---

## EffluentSamplingPoint {#https___ugentbiomath.github.io_waterframe_effluentsamplingpoint}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#EffluentSamplingPoint`

### Labels

- Effluent sampling point

### Description

Sampling point for outgoing/treated water (e.g., plant effluent, discharge point).

### Superclasses

- [SamplingPoint](#https___ugentbiomath.github.io_waterframe_samplingpoint)

### Related Entities

- [SamplingPoint](#https___ugentbiomath.github.io_waterframe_samplingpoint)


---

## FlowCompositeSampling {#https___ugentbiomath.github.io_waterframe_flowcompositesampling}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#FlowCompositeSampling`

### Labels

- Flow composite sampling

### Description

Composite sample with aliquot volume proportional to flow rate.

### Superclasses

- [CompositeSampling](#https___ugentbiomath.github.io_waterframe_compositesampling)

### Related Entities

- [CompositeSampling](#https___ugentbiomath.github.io_waterframe_compositesampling)


---

## FlowDirection {#https___ugentbiomath.github.io_waterframe_flowdirection}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#FlowDirection`

### Labels

- Flow direction

### Description

Direction of water flow relative to a treatment system. Critical for regulatory monitoring context.

### Subclasses

- [BypassFlow](#https___ugentbiomath.github.io_waterframe_bypassflow)
- [EffluentFlow](#https___ugentbiomath.github.io_waterframe_effluentflow)
- [InfluentFlow](#https___ugentbiomath.github.io_waterframe_influentflow)
- [ProcessFlow](#https___ugentbiomath.github.io_waterframe_processflow)

### Related Entities

- [BypassFlow](#https___ugentbiomath.github.io_waterframe_bypassflow)
- [EffluentFlow](#https___ugentbiomath.github.io_waterframe_effluentflow)
- [InfluentFlow](#https___ugentbiomath.github.io_waterframe_influentflow)
- [ProcessFlow](#https___ugentbiomath.github.io_waterframe_processflow)


---

## GrabSampling {#https___ugentbiomath.github.io_waterframe_grabsampling}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#GrabSampling`

### Labels

- Grab sampling

### Description

A discrete sample taken at a specific point in time. Provides a snapshot of water quality.

### Superclasses

- [SamplingMethod](#https___ugentbiomath.github.io_waterframe_samplingmethod)

### Related Entities

- [SamplingMethod](#https___ugentbiomath.github.io_waterframe_samplingmethod)


---

## InfluentFlow {#https___ugentbiomath.github.io_waterframe_influentflow}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#InfluentFlow`

### Labels

- Influent

### Description

Water flowing into a treatment system or unit process.

### Superclasses

- [FlowDirection](#https___ugentbiomath.github.io_waterframe_flowdirection)

### Related Entities

- [FlowDirection](#https___ugentbiomath.github.io_waterframe_flowdirection)


---

## InfluentSamplingPoint {#https___ugentbiomath.github.io_waterframe_influentsamplingpoint}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#InfluentSamplingPoint`

### Labels

- Influent sampling point

### Description

Sampling point for incoming water (e.g., plant influent, raw water intake).

### Superclasses

- [SamplingPoint](#https___ugentbiomath.github.io_waterframe_samplingpoint)

### Related Entities

- [SamplingPoint](#https___ugentbiomath.github.io_waterframe_samplingpoint)


---

## ManualSampler {#https___ugentbiomath.github.io_waterframe_manualsampler}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#ManualSampler`

### Labels

- Manual sampler

### Description

Equipment for manual sample collection (bottles, bailers, etc.).

### Superclasses

- [SamplingEquipment](#https___ugentbiomath.github.io_waterframe_samplingequipment)

### Related Entities

- [SamplingEquipment](#https___ugentbiomath.github.io_waterframe_samplingequipment)


---

## OnlineSensor {#https___ugentbiomath.github.io_waterframe_onlinesensor}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#OnlineSensor`

### Labels

- Online sensor

### Description

Continuous monitoring sensor installed in the process or water body.

### Superclasses

- [SamplingEquipment](#https___ugentbiomath.github.io_waterframe_samplingequipment)

### Related Entities

- [SamplingEquipment](#https___ugentbiomath.github.io_waterframe_samplingequipment)


---

## ProcessFlow {#https___ugentbiomath.github.io_waterframe_processflow}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#ProcessFlow`

### Labels

- Process flow

### Description

Water within a treatment process (intermediate stream).

### Superclasses

- [FlowDirection](#https___ugentbiomath.github.io_waterframe_flowdirection)

### Related Entities

- [FlowDirection](#https___ugentbiomath.github.io_waterframe_flowdirection)


---

## ProcessSamplingPoint {#https___ugentbiomath.github.io_waterframe_processsamplingpoint}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#ProcessSamplingPoint`

### Labels

- Process sampling point

### Description

Sampling point within a treatment process (e.g., between unit processes).

### Superclasses

- [SamplingPoint](#https___ugentbiomath.github.io_waterframe_samplingpoint)

### Related Entities

- [SamplingPoint](#https___ugentbiomath.github.io_waterframe_samplingpoint)


---

## SamplingEquipment {#https___ugentbiomath.github.io_waterframe_samplingequipment}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#SamplingEquipment`

### Labels

- Sampling equipment

### Description

Equipment used to collect water samples.

### Superclasses

- [BFO_0000040](#https___ugentbiomath.github.io_waterframe_bfo_0000040)

### Subclasses

- [Autosampler](#https___ugentbiomath.github.io_waterframe_autosampler)
- [ManualSampler](#https___ugentbiomath.github.io_waterframe_manualsampler)
- [OnlineSensor](#https___ugentbiomath.github.io_waterframe_onlinesensor)

### Related Entities

- [Autosampler](#https___ugentbiomath.github.io_waterframe_autosampler)
- [ManualSampler](#https___ugentbiomath.github.io_waterframe_manualsampler)
- [OnlineSensor](#https___ugentbiomath.github.io_waterframe_onlinesensor)


---

## SamplingMethod {#https___ugentbiomath.github.io_waterframe_samplingmethod}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#SamplingMethod`

### Labels

- Sampling method

### Description

The method or protocol used to collect a water sample.

### Superclasses

- [BFO_0000027](#https___ugentbiomath.github.io_waterframe_bfo_0000027)

### Subclasses

- [AutomatedSampling](#https___ugentbiomath.github.io_waterframe_automatedsampling)
- [CompositeSampling](#https___ugentbiomath.github.io_waterframe_compositesampling)
- [ContinuousSampling](#https___ugentbiomath.github.io_waterframe_continuoussampling)
- [GrabSampling](#https___ugentbiomath.github.io_waterframe_grabsampling)

### Related Entities

- [AutomatedSampling](#https___ugentbiomath.github.io_waterframe_automatedsampling)
- [CompositeSampling](#https___ugentbiomath.github.io_waterframe_compositesampling)
- [ContinuousSampling](#https___ugentbiomath.github.io_waterframe_continuoussampling)
- [GrabSampling](#https___ugentbiomath.github.io_waterframe_grabsampling)


---

## SamplingPoint {#https___ugentbiomath.github.io_waterframe_samplingpoint}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#SamplingPoint`

### Labels

- Sampling point

### Description

A designated physical location where water samples are collected. May be part of infrastructure (e.g., tap, outfall) or a location in a water body.

### Superclasses

- [BFO_0000040](#https___ugentbiomath.github.io_waterframe_bfo_0000040)

### Subclasses

- [AmbientSamplingPoint](#https___ugentbiomath.github.io_waterframe_ambientsamplingpoint)
- [DischargePoint](#https___ugentbiomath.github.io_waterframe_dischargepoint)
- [EffluentSamplingPoint](#https___ugentbiomath.github.io_waterframe_effluentsamplingpoint)
- [InfluentSamplingPoint](#https___ugentbiomath.github.io_waterframe_influentsamplingpoint)
- [ProcessSamplingPoint](#https___ugentbiomath.github.io_waterframe_processsamplingpoint)

### Related Entities

- [AmbientSamplingPoint](#https___ugentbiomath.github.io_waterframe_ambientsamplingpoint)
- [DischargePoint](#https___ugentbiomath.github.io_waterframe_dischargepoint)
- [EffluentSamplingPoint](#https___ugentbiomath.github.io_waterframe_effluentsamplingpoint)
- [InfluentSamplingPoint](#https___ugentbiomath.github.io_waterframe_influentsamplingpoint)
- [ProcessSamplingPoint](#https___ugentbiomath.github.io_waterframe_processsamplingpoint)


---

## TimeCompositeSampling {#https___ugentbiomath.github.io_waterframe_timecompositesampling}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#TimeCompositeSampling`

### Labels

- Time composite sampling

### Description

Composite sample with aliquots collected at regular time intervals.

### Superclasses

- [CompositeSampling](#https___ugentbiomath.github.io_waterframe_compositesampling)

### Related Entities

- [CompositeSampling](#https___ugentbiomath.github.io_waterframe_compositesampling)


---

## WaterSample {#https___ugentbiomath.github.io_waterframe_watersample}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#WaterSample`

### Labels

- Water sample

### Description

A physical sample of water taken for quality analysis. Links observations to sampling context including location, method, and time.

### Superclasses

- [BFO_0000040](#https___ugentbiomath.github.io_waterframe_bfo_0000040)


---

## Object Properties

## collectedBy {#https___ugentbiomath.github.io_waterframe_collectedby}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#collectedBy`

### Labels

- collected by

### Description

Links a sample to the equipment used for collection

### Domains

- [WaterSample](#https___ugentbiomath.github.io_waterframe_watersample)

### Ranges

- SamplingEquipment

### Related Entities

- [SamplingEquipment](#https___ugentbiomath.github.io_waterframe_samplingequipment)
- [WaterSample](#https___ugentbiomath.github.io_waterframe_watersample)


---

## flowRateUnit {#https___ugentbiomath.github.io_waterframe_flowrateunit}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#flowRateUnit`

### Labels

- flow rate unit

### Description

Unit of flow rate measurement (e.g., m3/day, MGD)

### Domains

- [DischargeMeasurement](#https___ugentbiomath.github.io_waterframe_dischargemeasurement)

### Ranges

- Unit

### Related Entities

- [DischargeMeasurement](#https___ugentbiomath.github.io_waterframe_dischargemeasurement)


---

## hasDischargePoint {#https___ugentbiomath.github.io_waterframe_hasdischargepoint}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasDischargePoint`

### Labels

- has discharge point

### Description

Links a facility to its regulatory discharge points

### Domains

- [BFO_0000040](#https___ugentbiomath.github.io_waterframe_bfo_0000040)

### Ranges

- DischargePoint

### Related Entities

- [DischargePoint](#https___ugentbiomath.github.io_waterframe_dischargepoint)


---

## hasFlowDirection {#https___ugentbiomath.github.io_waterframe_hasflowdirection}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasFlowDirection`

### Labels

- has flow direction

### Description

Links a sample or observation to its flow direction context

### Domains

- [nf58bf835e929450fa0a3e025f20ccd10b1](#https___ugentbiomath.github.io_waterframe_nf58bf835e929450fa0a3e025f20ccd10b1)

### Ranges

- FlowDirection

### Related Entities

- [FlowDirection](#https___ugentbiomath.github.io_waterframe_flowdirection)


---

## hasSample {#https___ugentbiomath.github.io_waterframe_hassample}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasSample`

### Labels

- has sample

### Description

Links an observation to the sample it was made on

### Domains

- [WaterQualityObservation](#https___ugentbiomath.github.io_waterframe_waterqualityobservation)

### Ranges

- WaterSample

### Related Entities

- [WaterQualityObservation](#https___ugentbiomath.github.io_waterframe_waterqualityobservation)
- [WaterSample](#https___ugentbiomath.github.io_waterframe_watersample)


---

## locatedAt {#https___ugentbiomath.github.io_waterframe_locatedat}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#locatedAt`

### Labels

- located at

### Description

Links a sampling point to the component or location it monitors

### Domains

- [SamplingPoint](#https___ugentbiomath.github.io_waterframe_samplingpoint)

### Ranges

- BFO_0000040

### Related Entities

- [SamplingPoint](#https___ugentbiomath.github.io_waterframe_samplingpoint)


---

## measuredAt {#https___ugentbiomath.github.io_waterframe_measuredat}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#measuredAt`

### Labels

- measured at

### Description

Links a discharge measurement to the discharge point

### Domains

- [DischargeMeasurement](#https___ugentbiomath.github.io_waterframe_dischargemeasurement)

### Ranges

- DischargePoint

### Related Entities

- [DischargeMeasurement](#https___ugentbiomath.github.io_waterframe_dischargemeasurement)
- [DischargePoint](#https___ugentbiomath.github.io_waterframe_dischargepoint)


---

## sampleOf {#https___ugentbiomath.github.io_waterframe_sampleof}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#sampleOf`

### Labels

- sample of

### Description

Links a sample to the material entity (water body, tank, process) it represents

### Domains

- [WaterSample](#https___ugentbiomath.github.io_waterframe_watersample)

### Ranges

- BFO_0000040

### Related Entities

- [WaterSample](#https___ugentbiomath.github.io_waterframe_watersample)


---

## takenAt {#https___ugentbiomath.github.io_waterframe_takenat}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#takenAt`

### Labels

- taken at

### Description

Links a sample to the sampling point where it was collected

### Domains

- [WaterSample](#https___ugentbiomath.github.io_waterframe_watersample)

### Ranges

- SamplingPoint

### Related Entities

- [SamplingPoint](#https___ugentbiomath.github.io_waterframe_samplingpoint)
- [WaterSample](#https___ugentbiomath.github.io_waterframe_watersample)


---

## usedSamplingMethod {#https___ugentbiomath.github.io_waterframe_usedsamplingmethod}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#usedSamplingMethod`

### Labels

- used sampling method

### Description

Links a sample to the method used for collection

### Domains

- [WaterSample](#https___ugentbiomath.github.io_waterframe_watersample)

### Ranges

- SamplingMethod

### Related Entities

- [SamplingMethod](#https___ugentbiomath.github.io_waterframe_samplingmethod)
- [WaterSample](#https___ugentbiomath.github.io_waterframe_watersample)


---

## Datatype Properties

## collectedOn {#https___ugentbiomath.github.io_waterframe_collectedon}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#collectedOn`

### Labels

- collected on

### Description

Date and time when the sample was collected

### Domains

- [WaterSample](#https___ugentbiomath.github.io_waterframe_watersample)

### Ranges

- dateTime

### Related Entities

- [WaterSample](#https___ugentbiomath.github.io_waterframe_watersample)


---

## compositePeriod {#https___ugentbiomath.github.io_waterframe_compositeperiod}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#compositePeriod`

### Labels

- composite period

### Description

Duration over which composite sample was collected (hours)

### Domains

- [WaterSample](#https___ugentbiomath.github.io_waterframe_watersample)

### Ranges

- double

### Related Entities

- [WaterSample](#https___ugentbiomath.github.io_waterframe_watersample)


---

## flowRate {#https___ugentbiomath.github.io_waterframe_flowrate}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#flowRate`

### Labels

- flow rate

### Description

Measured flow rate value

### Domains

- [DischargeMeasurement](#https___ugentbiomath.github.io_waterframe_dischargemeasurement)

### Ranges

- double

### Related Entities

- [DischargeMeasurement](#https___ugentbiomath.github.io_waterframe_dischargemeasurement)


---

## latitude {#https___ugentbiomath.github.io_waterframe_latitude}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#latitude`

### Labels

- latitude

### Description

Geographic latitude of sampling point

### Domains

- [SamplingPoint](#https___ugentbiomath.github.io_waterframe_samplingpoint)

### Ranges

- double

### Related Entities

- [SamplingPoint](#https___ugentbiomath.github.io_waterframe_samplingpoint)


---

## longitude {#https___ugentbiomath.github.io_waterframe_longitude}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#longitude`

### Labels

- longitude

### Description

Geographic longitude of sampling point

### Domains

- [SamplingPoint](#https___ugentbiomath.github.io_waterframe_samplingpoint)

### Ranges

- double

### Related Entities

- [SamplingPoint](#https___ugentbiomath.github.io_waterframe_samplingpoint)


---

## measuredOn {#https___ugentbiomath.github.io_waterframe_measuredon}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#measuredOn`

### Labels

- measured on

### Description

Date and time of discharge measurement

### Domains

- [DischargeMeasurement](#https___ugentbiomath.github.io_waterframe_dischargemeasurement)

### Ranges

- dateTime

### Related Entities

- [DischargeMeasurement](#https___ugentbiomath.github.io_waterframe_dischargemeasurement)


---

## numberOfAliquots {#https___ugentbiomath.github.io_waterframe_numberofaliquots}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#numberOfAliquots`

### Labels

- number of aliquots

### Description

Number of aliquots in a composite sample

### Domains

- [WaterSample](#https___ugentbiomath.github.io_waterframe_watersample)

### Ranges

- integer

### Related Entities

- [WaterSample](#https___ugentbiomath.github.io_waterframe_watersample)


---

## pointName {#https___ugentbiomath.github.io_waterframe_pointname}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#pointName`

### Labels

- point name

### Description

Regulatory or operational name of the sampling point

### Domains

- [SamplingPoint](#https___ugentbiomath.github.io_waterframe_samplingpoint)

### Ranges

- string

### Related Entities

- [SamplingPoint](#https___ugentbiomath.github.io_waterframe_samplingpoint)


---

## sampleId {#https___ugentbiomath.github.io_waterframe_sampleid}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#sampleId`

### Labels

- sample ID

### Description

Unique identifier for the sample (chain of custody tracking)

### Domains

- [WaterSample](#https___ugentbiomath.github.io_waterframe_watersample)

### Ranges

- string

### Related Entities

- [WaterSample](#https___ugentbiomath.github.io_waterframe_watersample)


---

