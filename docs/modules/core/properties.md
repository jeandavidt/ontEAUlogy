# Module: properties

Properties that connect water system components and their ports. Uses port-based modeling following OntoCAPE pattern.

**Module URI:** `https://ugentbiomath.github.io/waterframe/modules/core/properties`

**Source:** `ontology/modules/core/properties.ttl`

**Total Entities:** 21

## Contents

- [Classes](#classes) (6)
- [Object Properties](#object-properties) (15)

---

## Classes

## BlackwaterFlow {#https___ugentbiomath.github.io_waterframe_blackwaterflow}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#BlackwaterFlow`

### Labels

- Blackwater flow

### Description

Flow from toilets and urinals

### Superclasses

- [WaterFlow](#https___ugentbiomath.github.io_waterframe_waterflow)
- [WaterFlow](#https___ugentbiomath.github.io_waterframe_waterflow)

### Related Entities

- [WaterFlow](#https___ugentbiomath.github.io_waterframe_waterflow)


---

## GreywaterFlow {#https___ugentbiomath.github.io_waterframe_greywaterflow}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#GreywaterFlow`

### Labels

- Greywater flow

### Description

Flow from non-toilet fixtures (showers, sinks, washing machines)

### Superclasses

- [WaterFlow](#https___ugentbiomath.github.io_waterframe_waterflow)
- [WaterFlow](#https___ugentbiomath.github.io_waterframe_waterflow)

### Related Entities

- [WaterFlow](#https___ugentbiomath.github.io_waterframe_waterflow)


---

## PotableWaterFlow {#https___ugentbiomath.github.io_waterframe_potablewaterflow}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#PotableWaterFlow`

### Labels

- Potable water flow

### Description

Flow of drinking-quality water

### Superclasses

- [WaterFlow](#https___ugentbiomath.github.io_waterframe_waterflow)
- [WaterFlow](#https___ugentbiomath.github.io_waterframe_waterflow)

### Related Entities

- [WaterFlow](#https___ugentbiomath.github.io_waterframe_waterflow)


---

## RainwaterFlow {#https___ugentbiomath.github.io_waterframe_rainwaterflow}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#RainwaterFlow`

### Labels

- Rainwater flow

### Description

Flow from rainwater collection systems

### Superclasses

- [WaterFlow](#https___ugentbiomath.github.io_waterframe_waterflow)
- [WaterFlow](#https___ugentbiomath.github.io_waterframe_waterflow)

### Related Entities

- [WaterFlow](#https___ugentbiomath.github.io_waterframe_waterflow)


---

## ReclaimedWaterFlow {#https___ugentbiomath.github.io_waterframe_reclaimedwaterflow}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#ReclaimedWaterFlow`

### Labels

- Reclaimed water flow

### Description

Flow of treated water for reuse

### Superclasses

- [WaterFlow](#https___ugentbiomath.github.io_waterframe_waterflow)
- [WaterFlow](#https___ugentbiomath.github.io_waterframe_waterflow)

### Related Entities

- [WaterFlow](#https___ugentbiomath.github.io_waterframe_waterflow)


---

## WaterFlow {#https___ugentbiomath.github.io_waterframe_waterflow}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#WaterFlow`

### Labels

- Water flow

### Description

Classification of water flow types in the system

### Subclasses

- [GreywaterFlow](#https___ugentbiomath.github.io_waterframe_greywaterflow)
- [BlackwaterFlow](#https___ugentbiomath.github.io_waterframe_blackwaterflow)
- [RainwaterFlow](#https___ugentbiomath.github.io_waterframe_rainwaterflow)
- [PotableWaterFlow](#https___ugentbiomath.github.io_waterframe_potablewaterflow)
- [ReclaimedWaterFlow](#https___ugentbiomath.github.io_waterframe_reclaimedwaterflow)

### Related Entities

- [BlackwaterFlow](#https___ugentbiomath.github.io_waterframe_blackwaterflow)
- [GreywaterFlow](#https___ugentbiomath.github.io_waterframe_greywaterflow)
- [PotableWaterFlow](#https___ugentbiomath.github.io_waterframe_potablewaterflow)
- [RainwaterFlow](#https___ugentbiomath.github.io_waterframe_rainwaterflow)
- [ReclaimedWaterFlow](#https___ugentbiomath.github.io_waterframe_reclaimedwaterflow)


---

## Object Properties

## correspondsToModelInput {#https___ugentbiomath.github.io_waterframe_correspondstomodelinput}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#correspondsToModelInput`

### Labels

- corresponds to model input

### Description

Port corresponds to an input variable in a computational model

### Domains

- [InputPort](#https___ugentbiomath.github.io_waterframe_inputport)

### Ranges

- Thing

### Related Entities

- [InputPort](#https___ugentbiomath.github.io_waterframe_inputport)


---

## correspondsToModelOutput {#https___ugentbiomath.github.io_waterframe_correspondstomodeloutput}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#correspondsToModelOutput`

### Labels

- corresponds to model output

### Description

Port corresponds to an output variable in a computational model

### Domains

- [OutputPort](#https___ugentbiomath.github.io_waterframe_outputport)

### Ranges

- Thing

### Related Entities

- [OutputPort](#https___ugentbiomath.github.io_waterframe_outputport)


---

## flowsTo {#https___ugentbiomath.github.io_waterframe_flowsto}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#flowsTo`

### Labels

- flows to

### Description

Direct water flow connection from output port to input port

### Domains

- [OutputPort](#https___ugentbiomath.github.io_waterframe_outputport)

### Ranges

- InputPort

### Inverse Properties

- [receivesFlowFrom](#https___ugentbiomath.github.io_waterframe_receivesflowfrom)

### Subproperties

- [hasPrimaryFlow](#https___ugentbiomath.github.io_waterframe_hasprimaryflow)
- [hasBackupFlow](#https___ugentbiomath.github.io_waterframe_hasbackupflow)
- [hasOverflowFlow](#https___ugentbiomath.github.io_waterframe_hasoverflowflow)

### Related Entities

- [InputPort](#https___ugentbiomath.github.io_waterframe_inputport)
- [OutputPort](#https___ugentbiomath.github.io_waterframe_outputport)
- [hasBackupFlow](#https___ugentbiomath.github.io_waterframe_hasbackupflow)
- [hasOverflowFlow](#https___ugentbiomath.github.io_waterframe_hasoverflowflow)
- [hasPrimaryFlow](#https___ugentbiomath.github.io_waterframe_hasprimaryflow)
- [receivesFlowFrom](#https___ugentbiomath.github.io_waterframe_receivesflowfrom)


---

## hasBackupFlow {#https___ugentbiomath.github.io_waterframe_hasbackupflow}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasBackupFlow`

### Labels

- has backup flow

### Description

Alternative flow path for overflow or emergency

### Domains

- [OutputPort](#https___ugentbiomath.github.io_waterframe_outputport)

### Ranges

- InputPort

### Superproperties

- [flowsTo](#https___ugentbiomath.github.io_waterframe_flowsto)

### Related Entities

- [InputPort](#https___ugentbiomath.github.io_waterframe_inputport)
- [OutputPort](#https___ugentbiomath.github.io_waterframe_outputport)
- [flowsTo](#https___ugentbiomath.github.io_waterframe_flowsto)


---

## hasComponent {#https___ugentbiomath.github.io_waterframe_hascomponent}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasComponent`

### Labels

- has component

### Description

Water system component that is part of the household system

### Domains

- [Household](#https___ugentbiomath.github.io_waterframe_household)

### Ranges

- WaterSystemComponent

### Related Entities

- [Household](#https___ugentbiomath.github.io_waterframe_household)
- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)


---

## hasDownstreamComponent {#https___ugentbiomath.github.io_waterframe_hasdownstreamcomponent}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasDownstreamComponent`

### Labels

- has downstream component

### Description

Component that receives flow from this component (via port connections)

### Domains

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)

### Ranges

- WaterSystemComponent

### Related Entities

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)


---

## hasFlowType {#https___ugentbiomath.github.io_waterframe_hasflowtype}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasFlowType`

### Labels

- has flow type

### Description

Classifies the type of water flowing through a port

### Domains

- [Port](#https___ugentbiomath.github.io_waterframe_port)

### Ranges

- WaterFlow

### Related Entities

- [Port](#https___ugentbiomath.github.io_waterframe_port)
- [WaterFlow](#https___ugentbiomath.github.io_waterframe_waterflow)


---

## hasInputPort {#https___ugentbiomath.github.io_waterframe_hasinputport}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasInputPort`

### Labels

- has input port

### Description

Component has a physical interface for receiving material flow

### Domains

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)

### Ranges

- InputPort

### Superproperties

- [hasPort](#https___ugentbiomath.github.io_waterframe_hasport)

### Related Entities

- [InputPort](#https___ugentbiomath.github.io_waterframe_inputport)
- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)
- [hasPort](#https___ugentbiomath.github.io_waterframe_hasport)


---

## hasOutputPort {#https___ugentbiomath.github.io_waterframe_hasoutputport}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasOutputPort`

### Labels

- has output port

### Description

Component has a physical interface for discharging material flow

### Domains

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)

### Ranges

- OutputPort

### Superproperties

- [hasPort](#https___ugentbiomath.github.io_waterframe_hasport)

### Related Entities

- [OutputPort](#https___ugentbiomath.github.io_waterframe_outputport)
- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)
- [hasPort](#https___ugentbiomath.github.io_waterframe_hasport)


---

## hasOverflowFlow {#https___ugentbiomath.github.io_waterframe_hasoverflowflow}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasOverflowFlow`

### Labels

- has overflow flow

### Description

Flow path for excess water beyond capacity

### Domains

- [OutputPort](#https___ugentbiomath.github.io_waterframe_outputport)

### Ranges

- InputPort

### Superproperties

- [flowsTo](#https___ugentbiomath.github.io_waterframe_flowsto)

### Related Entities

- [InputPort](#https___ugentbiomath.github.io_waterframe_inputport)
- [OutputPort](#https___ugentbiomath.github.io_waterframe_outputport)
- [flowsTo](#https___ugentbiomath.github.io_waterframe_flowsto)


---

## hasPort {#https___ugentbiomath.github.io_waterframe_hasport}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasPort`

### Labels

- has port

### Description

Component has a connection port (input or output)

### Domains

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)

### Ranges

- Port

### Subproperties

- [hasInputPort](#https___ugentbiomath.github.io_waterframe_hasinputport)
- [hasOutputPort](#https___ugentbiomath.github.io_waterframe_hasoutputport)

### Related Entities

- [Port](#https___ugentbiomath.github.io_waterframe_port)
- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)
- [hasInputPort](#https___ugentbiomath.github.io_waterframe_hasinputport)
- [hasOutputPort](#https___ugentbiomath.github.io_waterframe_hasoutputport)


---

## hasPrimaryFlow {#https___ugentbiomath.github.io_waterframe_hasprimaryflow}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasPrimaryFlow`

### Labels

- has primary flow

### Description

Main flow connection (as opposed to backup or overflow)

### Domains

- [OutputPort](#https___ugentbiomath.github.io_waterframe_outputport)

### Ranges

- InputPort

### Superproperties

- [flowsTo](#https___ugentbiomath.github.io_waterframe_flowsto)

### Related Entities

- [InputPort](#https___ugentbiomath.github.io_waterframe_inputport)
- [OutputPort](#https___ugentbiomath.github.io_waterframe_outputport)
- [flowsTo](#https___ugentbiomath.github.io_waterframe_flowsto)


---

## hasUpstreamComponent {#https___ugentbiomath.github.io_waterframe_hasupstreamcomponent}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasUpstreamComponent`

### Labels

- has upstream component

### Description

Component that provides flow to this component (via port connections)

### Domains

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)

### Ranges

- WaterSystemComponent

### Inverse Properties

- [hasDownstreamComponent](#https___ugentbiomath.github.io_waterframe_hasdownstreamcomponent)

### Related Entities

- [WaterSystemComponent](#https___ugentbiomath.github.io_waterframe_watersystemcomponent)
- [hasDownstreamComponent](#https___ugentbiomath.github.io_waterframe_hasdownstreamcomponent)


---

## hasUsagePoint {#https___ugentbiomath.github.io_waterframe_hasusagepoint}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasUsagePoint`

### Labels

- has usage point

### Description

Water usage points contained within or associated with a household

### Domains

- [Household](#https___ugentbiomath.github.io_waterframe_household)

### Ranges

- WaterUsagePoint

### Related Entities

- [Household](#https___ugentbiomath.github.io_waterframe_household)
- [WaterUsagePoint](#https___ugentbiomath.github.io_waterframe_waterusagepoint)


---

## receivesFlowFrom {#https___ugentbiomath.github.io_waterframe_receivesflowfrom}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#receivesFlowFrom`

### Labels

- receives flow from

### Description

Input port receives material from upstream output port

### Domains

- [InputPort](#https___ugentbiomath.github.io_waterframe_inputport)

### Ranges

- OutputPort

### Related Entities

- [InputPort](#https___ugentbiomath.github.io_waterframe_inputport)
- [OutputPort](#https___ugentbiomath.github.io_waterframe_outputport)


---

