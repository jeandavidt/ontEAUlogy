# QSDsan: Quantitative Sustainable Design for Sanitation and Resource Recovery Systems

**Last Updated:** 2026-01-15
**Documentation:** https://qsdsan.readthedocs.io/

## Important Clarification

**QSDsan is NOT a river or watershed modeling package.** It is specifically designed for **sanitation and resource recovery systems**. If you are looking for river/watershed modeling capabilities, you may be thinking of a different package.

---

## Overview

QSDsan is an open-source, community-led platform for the quantitative sustainable design (QSD) of sanitation and resource recovery systems. It leverages BioSTEAM with enhanced features tailored to sanitation technologies.

### Key Capabilities
- **Process Modeling:** Design and simulate sanitation treatment systems
- **Techno-Economic Analysis (TEA):** Cost analysis and economic evaluation
- **Life Cycle Assessment (LCA):** Environmental impact assessment
- **Dynamic Simulation:** Time-varying process behavior
- **Uncertainty Analysis:** Sensitivity and probabilistic analysis

---

## Core Components

### 1. SanUnit (Sanitation Unit)
The fundamental building block for treatment processes. Examples include:
- [`Lagoon`](https://qsdsan.readthedocs.io/en/latest/api/sanunits/Lagoon.html) - Waste stabilization ponds
- [`Clarifier`](https://qsdsan.readthedocs.io/en/latest/api/sanunits/clarifier.html) - Solid-liquid separation
- [`Sedimentation`](https://qsdsan.readthedocs.io/en/latest/api/sanunits/Sedimentation.html) - Gravity-based settling
- [`SepticTank`](https://qsdsan.readthedocs.io/en/latest/api/sanunits/SepticTank.html) - Anaerobic treatment
- [`ActivatedSludgeProcess`](https://qsdsan.readthedocs.io/en/latest/api/sanunits/ActivatedSludgeProcess.html) - Biological treatment
- [`AnaerobicReactor`](https://qsdsan.readthedocs.io/en/latest/api/sanunits/anaerobic_reactor.html) - Anaerobic digestion reactors
- [`MembraneBioreactor`](https://qsdsan.readthedocs.io/en/latest/api/sanunits/membrane_bioreactor.html) - MBR systems
- [`Toilet`](https://qsdsan.readthedocs.io/en/latest/api/sanunits/toilet.html) - Collection devices
- [`Excretion`](https://qsdsan.readthedocs.io/en/latest/api/sanunits/Excretion.html) - Human waste generation

### 2. Process Models
Biological and chemical process implementations:
- [`ADM1`](https://qsdsan.readthedocs.io/en/latest/api/processes/ADM1.html) - Anaerobic Digestion Model No. 1
- [`ADM1p`](https://qsdsan.readthedocs.io/en/latest/api/processes/ADM1p.html) - ADM1 with Phosphorus extension
- [`ASM1`](https://qsdsan.readthedocs.io/en/latest/api/processes/ASM1.html) - Activated Sludge Model No. 1
- [`ASM2d`](https://qsdsan.readthedocs.io/en/latest/api/processes/ASM2d.html) - Activated Sludge Model No. 2d
- [`PM2`](https://qsdsan.readthedocs.io/en/latest/api/processes/PM2.html) - Phototrophic-Mixotrophic Process Model

### 3. WasteStream
Represents the material flows through the system with composition and properties.

### 4. Component
Defines chemical species and their properties in the system.

---

## System Examples Implemented

### Water Resource Recovery Facilities (WRRFs)
- 18 distinct plant-wide models implemented
- 34 WRRF configurations covered
- See [`werf EXPOsan module`](https://github.com/QSD-Group/EXPOsan/tree/werf/exposan/werf)

### Benchmark Simulation Models
- **BSM1:** Benchmark Simulation Model 1 (WWTP)
- **BSM2:** Extended benchmark with sludge treatment
- Reference: [IWA BSM Webpage](http://iwa-mia.org/benchmarking)

### Non-Sewered Sanitation Systems
- Biogenic Refinery
- Bwaise (Uganda)
- Eco-San systems
- Reclaimer
- NEWgenerator

---

## Installation

```bash
# Standard installation
pip install qsdsan

# Update to latest version
pip install -U qsdsan

# Install from GitHub main branch
pip install git+https://github.com/QSD-Group/QSDsan.git
```

---

## Tutorials and Resources

### Topical Tutorials
1. [Extended Installation Instructions](https://qsdsan.readthedocs.io/en/latest/tutorials/_installation.html)
2. [Quick Overview](https://qsdsan.readthedocs.io/en/latest/tutorials/0_Quick_Overview.html)
3. [Helpful Basics](https://qsdsan.readthedocs.io/en/latest/tutorials/1_Helpful_Basics.html)
4. [Component Class](https://qsdsan.readthedocs.io/en/latest/tutorials/2_Component.html)
5. [WasteStream Class](https://qsdsan.readthedocs.io/en/latest/tutorials/3_WasteStream.html)
6. [SanUnit (basic)](https://qsdsan.readthedocs.io/en/latest/tutorials/4_SanUnit_basic.html)
7. [SanUnit (advanced)](https://qsdsan.readthedocs.io/en/latest/tutorials/5_SanUnit_advanced.html)
8. [System Class](https://qsdsan.readthedocs.io/en/latest/tutorials/6_System.html)
9. [TEA](https://qsdsan.readthedocs.io/en/latest/tutorials/7_TEA.html)
10. [LCA](https://qsdsan.readthedocs.io/en/latest/tutorials/8_LCA.html)
11. [Uncertainty and Sensitivity Analyses](https://qsdsan.readthedocs.io/en/latest/tutorials/9_Uncertainty_and_Sensitivity_Analyses.html)
12. [Process](https://qsdsan.readthedocs.io/en/latest/tutorials/10_Process.html)
13. [Dynamic Simulation](https://qsdsan.readthedocs.io/en/latest/tutorials/11_Dynamic_Simulation.html)
14. [ADM1](https://qsdsan.readthedocs.io/en/latest/tutorials/12_Anaerobic_Digestion_Model_No_1.html)
15. [Process Modeling 101](https://qsdsan.readthedocs.io/en/latest/tutorials/13_Process_Modeling_101.html)

### Interactive Notebooks
Access tutorials via Jupyter notebooks at [mybinder.org](https://mybinder.org/v2/gh/QSD-Group/QSDsan/main?filepath=%2Fdocs%2Fsource%2Ftutorials)

---

## Related Packages

- [**BioSTEAM**](https://biosteam.readthedocs.io) - Process simulation platform that QSDsan extends
- [**chemicals**](https://chemicals.readthedocs.io/) - Thermodynamic property package
- [**DMsan**](https://github.com/QSD-Group/DMsan) - Decision-making for sanitation systems
- [**EXPOsan**](https://github.com/QSD-Group/EXPOsan) - Example systems built with QSDsan

---

## For River/Watershed Modeling

If you need river or watershed modeling capabilities, consider these alternatives:
- **SWAT** (Soil and Water Assessment Tool)
- **HEC-RAS** (River hydraulics)
- **QUAL2K** (River water quality)
- **WASP** (Water quality simulation)
- **BASINS** (Watershed modeling)
- **MIKE** (Hydroinformatics)

---

## References

1. Li, Y.; Trimmer, J.T.; Hand, S.; Zhang, X.; Chambers, K.G.; Lohman, H.A.C.; Shi, R.; Byrne, D.M.; Cook, S.M.; Guest, J.S. Quantitative Sustainable Design (QSD): A Methodology for the Prioritization of Research, Development, and Deployment of Technologies. *Environ. Sci.: Water Res. Technol.* 2022, 8 (11), 2439–2465. https://doi.org/10.1039/D2EW00431C

2. Li, Y.; Zhang, X.; Morgan, V.L.; Lohman, H.A.C.; Rowles, L.S.; Mittal, S.; Kogler, A.; Cusick, R.D.; Tarpeh, W.A.; Guest, J.S. QSDsan: An integrated platform for quantitative sustainable design of sanitation and resource recovery systems. *Environ. Sci.: Water Res. Technol.* 2022, 8 (10), 2289-2303. https://doi.org/10.1039/d2ew00455k

3. Cortés-Peña, Y.; Kumar, D.; Singh, V.; Guest, J.S. BioSTEAM: A Fast and Flexible Platform for the Design, Simulation, and Techno-Economic Analysis of Biorefineries under Uncertainty. *ACS Sustainable Chem. Eng.* 2020, 8 (8), 3302–3310. https://doi.org/10.1021/acssuschemeng.9b07040
