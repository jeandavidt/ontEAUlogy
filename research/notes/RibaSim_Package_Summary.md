# RibaSim: Water Resources Modeling Package

**Last Updated:** 2026-01-15
**Documentation:** https://ribasim.org/
**GitHub:** https://github.com/Deltares/Ribasim

## Overview

RibaSim is a **water resources model** designed to model rivers, watersheds, and surface water systems. It is written in the [Julia programming language](https://julialang.org/) and built on top of the [SciML: Open Source Software for Scientific Machine Learning](https://sciml.ai/) libraries.

RibaSim is the replacement for the regional surface water modules Mozart and SIMRES in the Netherlands Hydrological Instrument (NHI).

---

## Core Modeling Capabilities

### 1. Physical Layer - Water Balance Modeling

RibaSim uses the fundamental water balance equation:

```
dS/dt = Q_in - Q_out
```

Where:
- `S` = Storage in the basin
- `Q_in` = Inflow fluxes
- `Q_out` = Outflow fluxes

Fluxes can be split into:
- **Precipitation (P)**
- **Evapotranspiration (ET)**
- **Other fluxes (Q_rest)**

### 2. Spatial Modeling - Representative Elementary Watersheds (REWs)

RibaSim implements a **semi-distributed** modeling approach using Representative Elementary Watersheds (REWs):

- The watershed is divided into a network of connected REWs (called "basins")
- Each basin has an associated polygon
- Basins are connected as a directed graph
- Flow can be **bi-directional**
- The graph does **not have to be acyclic**

**Example Network Structure:**
```
basin A --- basin B
   |          |
   |          |
basin C --- basin D
```

### 3. Temporal Modeling

- Supports multiple timescales: years, weeks, days, or hours
- Uses **DifferentialEquations.jl** for ODE solvers
- Adaptive time stepping based on system state
- Supports **unequal time series** for forcing data
- Continuous simulation rather than discrete daily/hourly

---

## Node Types (Modeling Blocks)

### Storage/Nodes

#### 1. [`Basin`](https://ribasim.org/reference/node/basin)
- **Purpose:** Represents a drainage basin / Representative Elementary Watershed (REW)
- **Key Properties:**
  - Storage volume (m³)
  - Wetted area (m²)
  - Level-storage relationship
  - Level-area relationship
- **Forcing Data:** Precipitation, Evaporation
- **Used for:** Modeling lakes, reservoirs, ponds, catchment areas

#### 2. [`Junction`](https://ribasim.org/reference/node/junction)
- **Purpose:** Simple connection point without storage
- **Used for:** Network routing points

### Boundaries

#### 3. [`LevelBoundary`](https://ribasim.org/reference/node/level-boundary)
- **Purpose:** Boundary node with fixed water level
- **Used for:** Modeling connections to sea, lakes with constant level

#### 4. [`FlowBoundary`](https://ribasim.org/reference/node/flow-boundary)
- **Purpose:** Boundary node with prescribed flow rate
- **Used for:** Inflows from external sources (rivers, groundwater)

### Demand Nodes

#### 5. [`UserDemand`](https://ribasim.org/reference/node/user-demand)
- **Purpose:** Water consumption/demand node
- **Features:** Priority-based allocation
- **Used for:** Agricultural irrigation, municipal water supply, industrial use

#### 6. [`FlowDemand`](https://ribasim.org/reference/node/flow-demand)
- **Purpose:** Node with specific flow requirements

#### 7. [`LevelDemand`](https://ribasim.org/reference/node/level-demand)
- **Purpose:** Demand node maintaining minimum water level

### Connector Nodes (Flow Calculation)

#### 8. [`TabulatedRatingCurve`](https://ribasim.org/reference/node/tabulated-rating-curve)
- **Purpose:** One-directional flow based on upstream head
- **Typical Use:** 
  - Gravity flow conditions
  - Open water channels
  - Fixed structures (weirs, gates)
- **Behavior:** Flow is a function of water level

#### 9. [`LinearResistance`](https://ribasim.org/reference/node/linear-resistance)
- **Purpose:** Bi-directional flow based on head difference and linear resistance
- **Typical Use:**
  - Bi-directional flow situations
  - Head difference determining flow capacity
- **Equation:** Q = K * (h_upstream - h_downstream)

#### 10. [`ManningResistance`](https://ribasim.org/reference/node/manning-resistance)
- **Purpose:** Bi-directional flow using Manning-Gauckler formula
- **Typical Use:** Same as LinearResistance with better hydrological parameterization
- **Advantage:** More physically meaningful resistance parameters

#### 11. [`Pump`](https://ribasim.org/reference/node/pump)
- **Purpose:** One-directional structure with set flow rate
- **Features:** 
  - Controlled flow rate
  - Can be activated/deactivated by control layer
- **Typical Use:** Pumping stations, irrigation systems

#### 12. [`Outlet`](https://ribasim.org/reference/node/outlet)
- **Purpose:** One-directional gravity structure with set flow rate
- **Features:**
  - Automated mechanism to stop flow when head difference is zero
  - Control-based flow management
- **Typical Use:** Controlled releases, overflow structures

### Control Nodes

#### 13. [`DiscreteControl`](https://ribasim.org/reference/node/discrete-control)
- **Purpose:** Rule-based control of infrastructure
- **Features:** ON/OFF logic, threshold-based actions
- **Used for:** Operating rules, safety protocols

#### 14. [`ContinuousControl`](https://ribasim.org/reference/node/continuous-control)
- **Purpose:** Continuous control actions
- **Used for:** Smooth transitions, continuous operations

#### 15. [`PIDControl`](https://ribasim.org/reference/node/pid-control)
- **Purpose:** Proportional-Integral-Derivative control
- **Used for:** Maintaining target levels, automated regulation

---

## Allocation System

RibaSim implements a **priority-based allocation** system for water resources:

### Nested Allocation
For large networks (10,000+ nodes), RibaSim supports:
1. **Primary network** - main water distribution system
2. **Sub-networks** - local distribution areas

### Allocation Process
1. Inventory of demands from sub-networks
2. Allocate available water in primary network to sub-network inlets
3. Allocate assigned water within sub-networks to individual demands

### Priority System
- Water is allocated based on priority levels
- Higher priority demands are satisfied first
- Supports complex water rights and allocation rules

---

## Water Quality (Tracers)

RibaSim supports conservative tracer calculations (experimental feature):

**Available Source Tracers:**
- **Continuity** - Mass balance, fraction of all water sources
- **Initial** - Fraction of initial storages
- **LevelBoundary** - Fraction from level boundaries
- **FlowBoundary** - Fraction from flow boundaries
- **UserDemand** - Fraction from demand nodes
- **Drainage** - Fraction from drainage
- **Precipitation** - Fraction from precipitation
- **ResidenceTime** - Average residence time in seconds

**Note:** For full water quality modeling, RibaSim recommends coupling with [Delwaq](https://ribasim.org/guide/coupling/#sec-waterquality).

---

## Input Data Format

RibaSim uses **GeoPackage (.gpkg)** format for spatial data and **CSV** tables for parameters:

### Required Tables
1. **Basin** - Basin geometry and properties
2. **Node** - Node locations and types
3. **Edge** - Connections between nodes
4. **TimeSeries** - Forcing data (precipitation, evaporation, etc.)

### Example Structure
```
Model/
├── geometry.gpkg (spatial data)
├── basin.csv
├── tabulated_rating_curve.csv
├── user_demand.csv
└── forcing.csv
```

---

## Installation

### Pre-built Executables
Download from [latest release](https://github.com/Deltares/Ribasim/releases/latest):
- **Linux:** `ribasim_linux.zip`
- **Windows:** `ribasim_windows.zip`
- **QGIS Plugin:** `ribasim_qgis.zip`
- **Test Models:** `generated_testmodels.zip`

### Julia Package
```julia
using Pkg
Pkg.add("Ribasim")
```

---

## QGIS Integration

RibaSim provides a QGIS plugin for:
- Visual model setup
- Network editing
- Results visualization

---

## Example Applications

### Netherlands Water Distribution Network
RibaSim includes a comprehensive model of the main water distribution network in the Netherlands.

### Watershed Modeling
- Catchment delineation
- River network routing
- Reservoir operation
- Irrigation demand

---

## Coupling with Other Tools

RibaSim can be coupled with:
- **Delwaq** - Water quality modeling
- **Other hydroinformatics tools** via standard interfaces

See [coupling documentation](https://ribasim.org/guide/coupling.qmd) for details.

---

## References

1. Reggiani, P., et al. "A unified framework for hydrological modelling." Advances in Water Resources (1998).
2. Netherlands Hydrological Instrument (NHI)
3. Deltares - Water and subsurface research

---

## Comparison with Other Packages

| Feature | RibaSim | QSDsan | SWAT | HEC-RAS |
|---------|---------|--------|------|---------|
| **Primary Focus** | Water resources | Sanitation systems | Agricultural watershed | River hydraulics |
| **Language** | Julia | Python | Fortran/C++ | C++ |
| **Spatial Scale** | Basin/REW | N/A | HRU | River reach |
| **Allocation** | Priority-based | N/A | Limited | No |
| **Open Source** | Yes | Yes | Yes | Yes |
| **GUI** | QGIS Plugin | Jupyter | SWAT+ | HEC-RAS GUI |

---

## For Sanitation Systems

If you need both water resources AND sanitation modeling, consider:
- **RibaSim** for watershed/river modeling
- **QSDsan** for sanitation system design
- Coupling them through data exchange
