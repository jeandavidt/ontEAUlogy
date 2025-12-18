# OntoCAPE Modular Architecture Summary

**Date**: 2025-12-17
**Ontology**: OntoCAPE (Computer-Aided Process Engineering Ontology)
**Version**: Analyzed from local files
**Total modules**: 58 OWL files (56 successfully loaded)
**Total classes**: 1,233 | **Object Properties**: 237 | **Data Properties**: 62

---

## Executive Summary

**Is OntoCAPE properly modular in the vein of Alan Rector?**

✅ **YES** - OntoCAPE demonstrates **strong modular design** following Rector's principles with:
1. **Clear vertical layering** (abstraction levels)
2. **Horizontal aspect separation** (function/behavior/realization)
3. **Cohesive modules** with focused purposes
4. **Reusable foundational modules**

⚠️ **However**: Hardcoded file paths (`file:///C:/OntoCAPE/`) reduce portability, though the modular structure itself is sound.

---

## 1. Module Hierarchy & Dependencies

### 1.1 Vertical Layering (Abstraction Levels)

OntoCAPE follows a clear top-down architecture:

```
┌─────────────────────────────────────────────┐
│  UPPER LEVEL (Abstract)                     │
│  - system.owl                               │
│  - technical_system.owl                     │
│  - network_system.owl                       │
└─────────────────┬───────────────────────────┘
                  │ imports
┌─────────────────▼───────────────────────────┐
│  SUPPORTING CONCEPTS (Foundational)         │
│  - physical_dimension/                      │
│  - SI_unit/                                 │
│  - space_and_time/                          │
│  - geometry/                                │
│  - mathematical_relation/                   │
└─────────────────┬───────────────────────────┘
                  │ imports
┌─────────────────▼───────────────────────────┐
│  DOMAIN LEVEL (Chemical Engineering)        │
│  - material/ (substances, phases)           │
│  - chemical_process_system/                 │
│  - model/                                   │
└─────────────────┬───────────────────────────┘
                  │ imports
┌─────────────────▼───────────────────────────┐
│  APPLICATION LEVEL (Specific Tools)         │
│  - applications/aspen_plus/                 │
│  - software_system/                         │
└─────────────────────────────────────────────┘
```

### 1.2 Horizontal Aspect Separation

Within `chemical_process_system/`, the ontology separates concerns using **four orthogonal aspects**:

```
chemical_process_system/
├── CPS_function/       ← What the system DOES
│   ├── process.owl            (ProcessStep, inputs/outputs)
│   ├── controller.owl         (Control functions)
│   └── process_control.owl    (Control strategies)
│
├── CPS_behavior/       ← How the system BEHAVES
│   └── behavior.owl           (Mass balance, energy balance, dynamics)
│
├── CPS_realization/    ← Physical EQUIPMENT
│   ├── plant.owl              (PlantItem hierarchy)
│   ├── plant_equipment/       (Tanks, pumps, pipes)
│   └── process_control_equipment/
│
├── CPS_performance/    ← Performance METRICS
│   └── economic_performance.owl
│
└── process_units/      ← Specialized UNITS
    ├── chemical_reactor.owl
    ├── distillation_system.owl
    ├── heat_transfer_unit.owl
    ├── mixing_unit.owl
    ├── splitting_unit.owl
    └── flash_unit.owl
```

**This is excellent ontology engineering**: The same wastewater treatment plant can be described from multiple perspectives without redundancy or confusion.

---

## 2. Module-by-Module Breakdown

### **Module 1: upper_level/system.owl**
**Purpose**: Abstract system theory - what a "system" is
**Classes (30)**: `System`, `CompositeSystem`, `ElementarySystem`, `Property`, `Aspect`
**Properties**: `hasProperty`, `hasSubsystem`, `partOf`
**Imports**: `meta_model`

**Example Instance**:
```turtle
@prefix system: <file:///C:/OntoCAPE/OntoCAPE/upper_level/system.owl#> .
@prefix ex: <http://example.org/waterframe/> .

ex:WastewaterTreatmentPlant_A
    a system:System ;
    rdfs:label "Wastewater Treatment Plant A" ;
    system:hasProperty ex:TreatmentCapacity ;
    system:hasSubsystem ex:PrimaryTreatment ,
                        ex:SecondaryTreatment ,
                        ex:TertiaryTreatment .
```

---

### **Module 2: upper_level/technical_system.owl**
**Purpose**: Engineering systems (vs. natural systems)
**Classes (7)**: `TechnicalSystem`, `SystemFunction`, `SystemBehavior`, `SystemRealization`, `SystemPerformance`
**Properties**: `hasFunctionAspect`, `hasBehaviorAspect`, `hasRealizationAspect`, `hasPerformanceAspect`
**Imports**: `system`

**Key insight**: Introduces the **four-aspect pattern** (function/behavior/realization/performance) that pervades the entire ontology.

**Example Instance**:
```turtle
@prefix tech: <file:///C:/OntoCAPE/OntoCAPE/upper_level/technical_system.owl#> .

ex:Aeration_Blower_System
    a tech:TechnicalSystem ;
    rdfs:label "Aeration tank blower system" ;
    tech:hasFunctionAspect ex:OxygenSupplyFunction ;
    tech:hasBehaviorAspect ex:BlowerBehavior ;
    tech:hasRealizationAspect ex:BlowerEquipment ;
    tech:hasPerformanceAspect ex:EnergyEfficiency .
```

---

### **Module 3: upper_level/network_system.owl**
**Purpose**: Graph-theoretic view of systems
**Classes (7)**: `NetworkSystem`, `Node`, `Connection`, `DirectedConnection`, `ConnectionPoint`
**Properties**: `connectsFrom`, `connectsTo`, `hasConnectionPoint`
**Imports**: `system`

**Wastewater relevance**: Treatment plants are **naturally networks** (flowsheets).

**Example Instance**:
```turtle
@prefix net: <file:///C:/OntoCAPE/OntoCAPE/upper_level/network_system.owl#> .

ex:TreatmentNetwork
    a net:NetworkSystem ;
    rdfs:label "WWTP Process Network" .

ex:PrimarySettler a net:Node ; net:partOfNetwork ex:TreatmentNetwork .
ex:AerationTank   a net:Node ; net:partOfNetwork ex:TreatmentNetwork .

ex:Stream1
    a net:DirectedConnection ;
    net:connectsFrom ex:PrimarySettler ;
    net:connectsTo ex:AerationTank .
```

---

### **Module 4: supporting_concepts/physical_dimension/**
**Purpose**: Physical dimensions (SI foundation)
**Classes (8)**: `BaseDimension`, `DerivedDimension`, `Length`, `Mass`, `Time`, `Volume`, `Concentration`
**Imports**: `mathematical_relation`, `system`

**Derived dimensions include**:
- `Volume` (L³)
- `Concentration` (M/L³)
- `VolumetricFlowRate` (L³/T)
- `Pressure` (M/LT²)

---

### **Module 5: supporting_concepts/SI_unit/**
**Purpose**: SI units and prefixes
**Classes (5)**: `SI_BaseUnit`, `SI_DerivedUnit`, `SI_Prefix`
**Instances (many)**: `meter`, `kilogram`, `second`, `m3`, `kg_per_m3`, `m3_per_day`
**Imports**: `physical_dimension`

**Critical pattern**: All quantities use `ScalarQuantity` with `numericalValue` + `hasUnit`.

**Example Instance**:
```turtle
@prefix derived: <file:///C:/OntoCAPE/OntoCAPE/supporting_concepts/SI_unit/derived_SI_units.owl#> .
@prefix system: <file:///C:/OntoCAPE/OntoCAPE/upper_level/system.owl#> .

ex:InflowRate_5000
    a system:ScalarQuantity ;
    system:numericalValue "5000.0"^^xsd:double ;
    system:hasUnit derived:m3_per_day ;
    rdfs:label "Inflow rate: 5000 m³/day" .
```

---

### **Module 6: supporting_concepts/space_and_time/**
**Purpose**: Spatiotemporal concepts
**Classes (many)**: `SpatialRegion`, `TimeInterval`, `CoordinateSystem`
**Imports**: `physical_dimension`, `coordinate_system`

**Wastewater relevance**: Treatment process **retention times**, spatial location of equipment.

---

### **Module 7: material/substance/**
**Purpose**: Chemical species and their properties
**Classes (110)**: `Substance`, `ChemicalSpecies`, `Atom`, `Molecule`, `Ion`, `Reaction`
**Data properties**: `molecularFormula`, `CAS_RegistryNumber`, `InChI`, `name`, `atomicNumber`
**Imports**: `derived_dimensions`
**Individuals (7,000+)**: Extensive database of chemical species with CAS numbers

**Example Instance**:
```turtle
@prefix substance: <file:///C:/OntoCAPE/OntoCAPE/material/substance/substance.owl#> .
@prefix chemical: <file:///C:/OntoCAPE/OntoCAPE/material/substance/chemical_species.owl#> .

# Reuse existing species
ex:WastewaterStream1
    substance:containsSubstance chemical:Ammonia ,
                                chemical:Water ,
                                chemical:Nitrate .

# Or define new pollutant
ex:PFAS_Compound
    a substance:ChemicalSpecies ;
    substance:name "Perfluorooctanoic acid" ;
    substance:CAS_RegistryNumber "335-67-1" ;
    substance:molecularFormula "C8HF15O2" .
```

---

### **Module 8: material/phase_system/**
**Purpose**: Phases, streams, thermodynamics
**Classes (51)**: `PhaseSystem`, `Phase`, `LiquidPhase`, `GasPhase`, `MaterialStream`, `Composition`
**Properties**: `hasPhase`, `containsComponent`, `hasFlowRate`, `hasTemperature`, `hasPressure`
**Imports**: `reaction_mechanism`, `network_system`

**Wastewater relevance**: **Critical for streams, water quality, dissolved vs. suspended phases**.

**Example Instance**:
```turtle
@prefix phase: <file:///C:/OntoCAPE/OntoCAPE/material/phase_system/phase_system.owl#> .

ex:InflowStream
    a phase:LiquidMaterialStream ;
    rdfs:label "Wastewater inflow" ;
    phase:hasFlowRate ex:Flow_5000m3day ;
    phase:hasTemperature ex:Temp_15C ;
    phase:containsPhase ex:AqueousPhase .

ex:AqueousPhase
    a phase:LiquidPhase ;
    phase:containsComponent chemical:Water ;
    phase:containsComponent ex:COD_Component ;
    phase:containsComponent ex:NH3_Component .
```

---

### **Module 9: chemical_process_system/CPS_function/process**
**Purpose**: What a process **does** (its function)
**Classes (36)**: `ProcessStep`, `BatchProcess`, `ContinuousProcess`, `ChemicalTransformation`, `PhysicalTransformation`
**Properties**: `hasInput`, `hasOutput`, `realizes` (function)
**Imports**: `network_system`, `phase_system`

**Example Instance**:
```turtle
@prefix process: <file:///C:/OntoCAPE/OntoCAPE/chemical_process_system/CPS_function/process.owl#> .

ex:BiologicalTreatment
    a process:ProcessStep ;
    rdfs:label "Activated sludge treatment" ;
    process:hasInput ex:InflowStream ;
    process:hasOutput ex:TreatedEffluent ;
    process:realizes ex:BODRemovalFunction .

ex:BODRemovalFunction
    a process:ChemicalTransformation ;
    rdfs:comment "Microbial oxidation of organic matter" .
```

---

### **Module 10: chemical_process_system/CPS_behavior/behavior**
**Purpose**: How a process **behaves** (dynamics, balances)
**Classes (65)**: `Behavior`, `MassBalance`, `EnergyBalance`, `ConvectiveTransportRate`, `Accumulation`
**Properties**: `hasInflowRate`, `hasOutflowRate`, `governedBy`
**Imports**: `material`, `geometry`, `space_and_time`

**Example Instance**:
```turtle
@prefix behavior: <file:///C:/OntoCAPE/OntoCAPE/chemical_process_system/CPS_behavior/behavior.owl#> .

ex:AerationTankBehavior
    a behavior:ContinuousProcess ;
    behavior:hasInflowRate ex:Flow_in ;
    behavior:hasOutflowRate ex:Flow_out ;
    behavior:hasAccumulation ex:BiomassAccumulation ;
    behavior:governedBy ex:MassBalanceEq .

ex:MassBalanceEq
    a behavior:MassBalance ;
    rdfs:comment "dV/dt = Q_in - Q_out ; dX/dt = μX - Q/V·X" .
```

---

### **Module 11: chemical_process_system/CPS_realization/plant**
**Purpose**: Physical **equipment** and plant items
**Classes (27)**: `PlantItem`, `Equipment`, `Apparatus`, `Instrument`, `Pipe`, `Tank`, `Pump`
**Properties**: `hasCapacity`, `hasVolume`, `hasDiameter`, `locatedAt`
**Imports**: `substance`, `geometry`

**Example Instance**:
```turtle
@prefix plant: <file:///C:/OntoCAPE/OntoCAPE/chemical_process_system/CPS_realization/plant.owl#> .
@prefix apparatus: <file:///C:/OntoCAPE/OntoCAPE/chemical_process_system/CPS_realization/plant_equipment/apparatus.owl#> .

ex:AerationTank1_Physical
    a apparatus:Tank ;
    rdfs:label "Aeration Tank #1" ;
    plant:hasVolume ex:Vol_1000m3 ;
    plant:hasInsideDiameter ex:Dia_15m ;
    plant:locatedAt ex:GPS_Location .

ex:Vol_1000m3
    a system:ScalarQuantity ;
    system:numericalValue "1000.0"^^xsd:double ;
    system:hasUnit derived:m3 .
```

---

### **Module 12: chemical_process_system/process_units/**
**Purpose**: Specialized unit operations
**Submodules**:
- `chemical_reactor.owl` - reactors (biological reactors fit here!)
- `distillation_system.owl` - separation
- `heat_transfer_unit.owl` - heating/cooling
- `mixing_unit.owl` - mixing
- `splitting_unit.owl` - stream splitting
- `flash_unit.owl` - flash separation

**Example Instance**:
```turtle
@prefix reactor: <file:///C:/OntoCAPE/OntoCAPE/chemical_process_system/process_units/chemical_reactor.owl#> .

ex:ASM_Bioreactor
    a reactor:ChemicalReactor ;
    rdfs:label "Activated sludge bioreactor" ;
    reactor:hasReactionType ex:AerobicOxidation ;
    reactor:hasRetentionTime ex:HRT_8hours ;
    plant:hasVolume ex:Vol_1000m3 .

ex:HRT_8hours
    a system:ScalarQuantity ;
    system:numericalValue "8.0"^^xsd:double ;
    system:hasUnit derived:hour .
```

---

### **Module 13: model/mathematical_model**
**Purpose**: Mathematical representation of systems
**Classes (11)**: `MathematicalModel`, `ModelVariable`, `StateVariable`, `Parameter`, `Constant`
**Properties**: `models` (the system), `hasModelVariable`, `hasParameter`
**Imports**: `system`

**Key for waterFRAME**: This is where **ASM, ADM, BSM models** would be represented.

**Example Instance**:
```turtle
@prefix model: <file:///C:/OntoCAPE/OntoCAPE/model/mathematical_model.owl#> .

ex:ASM1_Model
    a model:MathematicalModel ;
    rdfs:label "Activated Sludge Model No. 1" ;
    model:models ex:ASM_Bioreactor ;
    model:hasModelVariable ex:Substrate_S ;
    model:hasModelVariable ex:Biomass_X ;
    model:hasParameter ex:mu_max ;
    model:hasParameter ex:Y_yield ;
    model:hasParameter ex:K_s .

ex:Substrate_S
    a model:StateVariable ;
    rdfs:label "Substrate concentration [mg COD/L]" .

ex:mu_max
    a model:Parameter ;
    rdfs:label "Maximum specific growth rate" ;
    model:hasValue "0.4"^^xsd:double ;
    model:hasUnit derived:per_day .
```

---

### **Module 14: model/process_model**
**Purpose**: Process-specific models (extends MathematicalModel)
**Classes (4)**: `ProcessModel`, `PropertyModel`, `Law`, `ModelingPrinciple`
**Imports**: `mathematical_model`, `chemical_process_system`

**Example Instance**:
```turtle
@prefix pmodel: <file:///C:/OntoCAPE/OntoCAPE/model/process_model.owl#> .

ex:WWTP_PlantModel
    a pmodel:ProcessModel ;
    rdfs:label "Full WWTP model with ASM + ADM" ;
    pmodel:models ex:WastewaterTreatmentPlant_A ;
    pmodel:hasSubmodel ex:ASM1_Model ;
    pmodel:hasSubmodel ex:ADM1_Model ;
    pmodel:hasSubmodel ex:SettlerModel ;
    pmodel:hasInputVariable ex:InflowRate_Var ;
    pmodel:hasInputVariable ex:InflowCOD_Var ;
    pmodel:hasOutputVariable ex:EffluentQuality_Var .
```

---

### **Module 15: software_system/**
**Purpose**: Represent simulation/modeling software
**Classes (20)**: `SoftwareSystem`, `ProcessModelingSoftware`, `SolverComponent`
**Properties**: `canExecute`, `hasVersion`
**Imports**: `technical_system`, `physical_dimension`

**Example Instance**:
```turtle
@prefix software: <file:///C:/OntoCAPE/OntoCAPE/software_system/software_system.owl#> .

ex:BioWin_Simulator
    a software:ProcessModelingSoftware ;
    rdfs:label "BioWin WWTP simulator" ;
    software:canExecute ex:ASM1_Model ;
    software:canExecute ex:ADM1_Model ;
    software:hasVersion "6.1" .
```

---

## 3. Modularity Assessment (Rector's Principles)

### ✅ **Principle 1: Vertical Modularity (Abstraction Layers)**
**Score: Excellent**

OntoCAPE has **four clear layers**:
1. **Upper level**: Generic system theory (reusable beyond process engineering)
2. **Supporting concepts**: Foundational (dimensions, units, math relations)
3. **Domain level**: Chemical process engineering specifics
4. **Application level**: Tool integrations (Aspen Plus)

This allows selective import. A simple application might only use upper_level + supporting_concepts. A full process simulator uses everything.

### ✅ **Principle 2: Horizontal Modularity (Aspect Separation)**
**Score: Excellent**

The **function/behavior/realization/performance** split is textbook ontology engineering. Same entity, multiple viewpoints, no redundancy.

Example: An aeration tank
- **Function**: `ex:OxygenTransfer a process:ProcessStep`
- **Behavior**: `ex:AerationDynamics a behavior:MassBalance`
- **Realization**: `ex:Tank1 a apparatus:Tank`
- **Model**: `ex:ASM_Model models ex:OxygenTransfer`

### ✅ **Principle 3: Reusability**
**Score: Good**

Supporting concepts modules (`SI_unit`, `physical_dimension`, `space_and_time`) are **domain-independent** and could be reused in hydrology, civil engineering, etc.

### ⚠️ **Principle 4: Import Structure**
**Score: Mixed**

- ✓ Uses `owl:imports` consistently
- ✗ Hardcoded `file:///C:/OntoCAPE/` paths (portability issue)
- ✗ Some circular dependencies at domain level (acceptable for large integrated ontology)

**Recommendation**: Replace with proper HTTP URIs (e.g., `https://ontocape.org/OntoCAPE/`)

### ✅ **Principle 5: Cohesion**
**Score: Excellent**

Each module has a **focused purpose**. No "junk drawer" modules with unrelated concepts.

### ✅ **Principle 6: Coupling**
**Score: Good**

Modules depend on each other, but dependencies are **hierarchical** (not tangled). Domain modules don't reach down to modify upper-level concepts.

---

## 4. Interaction Patterns Between Modules

### Pattern 1: **Foundation → Domain**
```
supporting_concepts/physical_dimension
    ↓ (defines dimensions)
supporting_concepts/SI_unit
    ↓ (provides units)
material/substance
    ↓ (uses units for properties)
material/phase_system
    ↓ (represents streams with properties)
chemical_process_system/CPS_function/process
    (uses streams as inputs/outputs)
```

### Pattern 2: **Abstract → Concrete Specialization**
```
upper_level/system:System
    ↓ (specializes to)
upper_level/technical_system:TechnicalSystem
    ↓ (specializes to)
chemical_process_system/chemical_process_system:ChemicalProcessSystem
    ↓ (specializes to)
chemical_process_system/process_units/chemical_reactor:ChemicalReactor
```

### Pattern 3: **Four-Aspect Decomposition**
```
                    TechnicalSystem
                          |
        ┌─────────────────┼─────────────────┬────────────────┐
        ↓                 ↓                 ↓                ↓
 SystemFunction   SystemBehavior   SystemRealization  SystemPerformance
        |                 |                 |                |
        ↓                 ↓                 ↓                ↓
 CPS_function/     CPS_behavior/     CPS_realization/  CPS_performance/
```

All aspects **co-refer** to the same real-world entity but from different angles.

---

## 5. Relevance to waterFRAME

### **High-value modules for water reuse**:
1. ✅ `material/phase_system` - streams, water quality
2. ✅ `chemical_process_system/CPS_function/process` - treatment operations
3. ✅ `chemical_process_system/CPS_realization/plant` - equipment
4. ✅ `chemical_process_system/process_units/chemical_reactor` - bioreactors
5. ✅ `model/process_model` - ASM/ADM representation
6. ✅ `upper_level/network_system` - treatment train topology

### **Gaps for water reuse** (to be addressed):
- ❌ **Fit-for-purpose classification** (drinking, irrigation, industrial)
- ❌ **Water quality standards** (regulatory limits)
- ❌ **Risk assessment** (pathogen removal, chemical hazards)
- ❌ **Multi-plant optimization** (catchment-scale)
- ❌ **Agent invocation metadata** (how to call model APIs)

These can be **added as extensions** without breaking OntoCAPE's structure.

---

## 6. Conclusion

**OntoCAPE is a well-engineered modular ontology** that successfully applies Rector's principles. Its clear layering and aspect separation make it an excellent foundation for waterFRAME, though water-specific extensions (fit-for-purpose, regulations, agent metadata) will be needed.

**Recommended approach**:
1. **Reuse** OntoCAPE core modules directly (upper_level, supporting_concepts, material, process_system)
2. **Extend** with water-specific modules (water_reuse, water_quality_standards, fit_for_purpose)
3. **Bridge** to SOSA/SSN for monitoring, QUDT for units alignment
4. **Add** agent/optimization layer on top (OntoAgent-style)

**Next steps**: Phase 2 (create test instances) and Phase 3 (test against competency questions).
