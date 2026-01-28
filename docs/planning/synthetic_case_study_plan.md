# Synthetic Case Study System Design

## Executive Summary

This document describes the design for a **Ghent Synthetic Water System** - a made-up but realistic water system that will serve as a testbed for the waterFRAME ontology. The system includes:

- **Distributed architecture**: Each water system component exposes its own independent API (simulating real-world heterogeneous systems)
- A Streamlit frontend with a map interface, SPARQL query capability, and **LLM-powered natural language to SPARQL translation**
- Stub process models (upgradeable to QSDsan, Ribasim, PeePyPoo)
- An agent-friendly discovery mechanism for automated optimization

---

## 1. Synthetic Water System: Ghent Case Study

### 1.1 System Overview - Cascade Layout

The system follows a realistic **upstream-to-downstream cascade** along the Lieve River:

```
═══════════════════════════════════════════════════════════════════════════════
                              LIEVE RIVER FLOW →
═══════════════════════════════════════════════════════════════════════════════

UPSTREAM ZONE (Dampoort)                    DOWNSTREAM ZONE (Muide)
─────────────────────────                   ──────────────────────────

     │ River                                      │ River (with WWTP-1 discharge)
     ▼                                            ▼
┌─────────────┐                              ┌─────────────┐
│  DWP-1      │  Drinking Water              │  DWP-2      │  Drinking Water
│  (Intake)   │  Plant 1                     │  (Intake)   │  Plant 2
└──────┬──────┘                              └──────┬──────┘
       │                                            │
       ├────────────────┬───────────┐               ├────────────────┬────────────┬────────────┐
       │                │           │               │                │            │            │
       ▼                ▼           ▼               ▼                ▼            ▼            ▼
┌────────────┐  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐
│ Dampoort   │  │  Texfin    │ │  FoodPro   │ │   Muide    │ │  ChipTech  │ │  PharmaGen │ │  BrewCo    │
│ Residential│  │  (Textile) │ │  (Food)    │ │ Residential│ │(Electronics│ │  (Pharma)  │ │ (Brewery)  │
│            │  │            │ │            │ │            │ │            │ │            │ │            │
└─────┬──────┘  └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
      │               │              │              │               │              │              │
      └───────────────┴──────────────┘              └───────────────┴──────────────┴──────────────┘
                      │                                             │
                      ▼                                             ▼
               ┌─────────────┐                                ┌─────────────┐
               │   WWTP-1    │                                │   WWTP-2    │
               │ (Upstream)  │                                │ (Downstream)│
               └──────┬──────┘                                └──────┬──────┘
                      │                                              │
                      ▼                                              ▼
═══════════════════════════════════════════════════════════════════════════════
                         → RIVER CONTINUES DOWNSTREAM →
═══════════════════════════════════════════════════════════════════════════════
```

### 1.2 Key Design Principle: Upstream/Downstream Impact

This cascade layout enables testing critical water management scenarios:

1. **DWP-2 receives degraded water**: WWTP-1's discharge affects DWP-2's raw water quality
2. **Cumulative pollution**: Both WWTPs discharge to the same river
3. **Competing demands**: Industries and residential areas share the same DWP
4. **Quality propagation**: Upstream decisions affect downstream users

### 1.3 Geographic Context (Ghent, Flanders, Belgium)

| Entity | Zone | Location (Approx.) | Description |
|--------|------|-------------------|-------------|
| Lieve River | Both | 51.06°N, 3.73°E | Historical canal, flows west to east |
| DWP-1 (Drinking Water Plant 1) | Upstream | 51.0620°N, 3.7300°E | Serves Dampoort zone |
| Dampoort Residential | Upstream | 51.0600°N, 3.7320°E | ~3,000 inhabitants |
| Texfin NV (Textile) | Upstream | 51.0585°N, 3.7340°E | Textile finishing |
| FoodPro BVBA (Food) | Upstream | 51.0575°N, 3.7360°E | Food processing |
| WWTP-1 (Upstream) | Upstream | 51.0560°N, 3.7400°E | Treats Dampoort zone wastewater |
| DWP-2 (Drinking Water Plant 2) | Downstream | 51.0540°N, 3.7450°E | Serves Muide zone (receives WWTP-1 impact) |
| Muide Residential | Downstream | 51.0520°N, 3.7470°E | ~5,000 inhabitants |
| ChipTech NV (Electronics) | Downstream | 51.0510°N, 3.7490°E | Electronics manufacturing |
| PharmaGen NV (Pharma) | Downstream | 51.0500°N, 3.7510°E | Pharmaceutical production |
| BrewCo BVBA (Brewery) | Downstream | 51.0495°N, 3.7530°E | Craft brewery |
| WWTP-2 (Downstream) | Downstream | 51.0480°N, 3.7560°E | Treats Muide zone wastewater |

### 1.4 Industrial Entities - Upstream Zone (Dampoort)

#### Texfin NV (Textile Finishing)
- **Water Quality Input Requirements**:
  - Turbidity < 1 NTU
  - Hardness < 50 mg/L CaCO3 (soft water needed)
  - No chlorine residual
- **Water Quality Output**:
  - High COD (200-400 mg/L)
  - Dyes and colorants (ADMI color units 500-2000)
  - High temperature (35-45°C)
- **Water Use**: 500 m³/day
- **Process**: Dyeing, washing, finishing

#### FoodPro BVBA (Food Processing)
- **Water Quality Input Requirements**:
  - Potable water standard (Flemish drinking water decree)
  - E. coli: 0 CFU/100mL
  - Turbidity < 0.5 NTU
- **Water Quality Output**:
  - High BOD (300-600 mg/L)
  - Suspended solids (200-500 mg/L)
  - Fats, oils, grease (50-150 mg/L)
- **Water Use**: 800 m³/day
- **Process**: Washing, cooking, cleaning

### 1.5 Residential Entity - Upstream Zone (Dampoort)

#### Dampoort Residential District
- **Population**: ~3,000 inhabitants
- **Water Quality Requirements**:
  - Flemish Drinking Water Decree (Besluit Vlaamse Regering 13/12/2002)
  - All parameters must meet Belgian/EU potable water standards
- **Water Use**: 150 L/person/day = 450 m³/day total
- **Wastewater Output**:
  - Typical domestic wastewater
  - BOD: 200-300 mg/L
  - TSS: 200-300 mg/L
  - TKN: 40-60 mg/L

### 1.6 Industrial Entities - Downstream Zone (Muide)

#### ChipTech NV (Electronics Manufacturing)
- **Water Quality Input Requirements**:
  - Ultra-pure water (resistivity > 18 MΩ·cm)
  - TOC < 5 ppb
  - Particles > 0.1 µm: < 1/mL
- **Water Quality Output**:
  - Low organic load
  - Heavy metals (Cu, Ni, Pb traces)
  - Solvents and acids
- **Water Use**: 200 m³/day
- **Process**: Wafer cleaning, etching, rinsing
- **Note**: Requires additional on-site treatment of DWP-2 water

#### PharmaGen NV (Pharmaceutical Production)
- **Water Quality Input Requirements**:
  - Purified Water (Ph. Eur. standard)
  - TOC < 500 ppb
  - Conductivity < 4.3 µS/cm
  - Microbial count < 100 CFU/mL
- **Water Quality Output**:
  - Moderate COD (100-200 mg/L)
  - Active pharmaceutical ingredients (trace)
  - Solvents (isopropanol, ethanol traces)
- **Water Use**: 400 m³/day
- **Process**: API synthesis, formulation, cleaning

#### BrewCo BVBA (Craft Brewery)
- **Water Quality Input Requirements**:
  - Potable water standard
  - Low chlorine (affects yeast)
  - Specific mineral profile (Ca, Mg, SO4 for beer style)
- **Water Quality Output**:
  - High BOD (1000-2000 mg/L)
  - High TSS (200-400 mg/L)
  - pH variations (4-10)
  - Yeast and organic matter
- **Water Use**: 600 m³/day
- **Process**: Mashing, boiling, fermentation, cleaning

### 1.7 Residential Entity - Downstream Zone (Muide)

#### Muide Residential District
- **Population**: ~5,000 inhabitants
- **Water Quality Requirements**:
  - Flemish Drinking Water Decree
  - All parameters must meet Belgian/EU potable water standards
- **Water Use**: 150 L/person/day = 750 m³/day total
- **Wastewater Output**:
  - Typical domestic wastewater
  - BOD: 200-300 mg/L
  - TSS: 200-300 mg/L
  - TKN: 40-60 mg/L
- **Note**: DWP-2 source water quality affected by WWTP-1 discharge

### 1.8 Treatment Facilities

#### DWP-1 (Drinking Water Plant - Upstream)
- **Capacity**: 2,000 m³/day
- **Serves**: Dampoort Residential, Texfin, FoodPro
- **Raw Water Source**: Lieve River (pristine)
- **Process Train**:
  1. Coagulation/Flocculation
  2. Sedimentation
  3. Rapid Sand Filtration
  4. Activated Carbon Adsorption
  5. Disinfection (UV + Chloramine)
- **Output**: Potable water meeting Flemish standards

#### DWP-2 (Drinking Water Plant - Downstream)
- **Capacity**: 2,500 m³/day
- **Serves**: Muide Residential, ChipTech, PharmaGen, BrewCo
- **Raw Water Source**: Lieve River (impacted by WWTP-1 discharge)
- **Process Train**:
  1. Pre-ozonation (micropollutant removal)
  2. Coagulation/Flocculation
  3. Sedimentation
  4. Rapid Sand Filtration
  5. GAC Adsorption (enhanced)
  6. Membrane filtration (UF)
  7. Disinfection (UV + Chloramine)
- **Output**: Potable water meeting Flemish standards
- **Challenge**: Must handle degraded raw water quality

#### WWTP-1 (Upstream Zone)
- **Capacity**: 2,000 m³/day
- **Serves**: Dampoort Residential, Texfin, FoodPro
- **Process Train**:
  1. Equalization
  2. pH adjustment
  3. Coagulation/DAF (for textile waste)
  4. Activated Sludge (extended aeration)
  5. Tertiary filtration
- **Discharge**: To Lieve River (VLAREM II limits)
- **Impact**: Degrades water quality for DWP-2 intake

#### WWTP-2 (Downstream Zone)
- **Capacity**: 2,500 m³/day
- **Serves**: Muide Residential, ChipTech, PharmaGen, BrewCo
- **Process Train**:
  1. Equalization (handles brewery pH swings)
  2. Primary Clarification
  3. Activated Sludge (nutrient removal, BNR)
  4. Secondary Clarification
  5. Tertiary treatment (micropollutants from pharma)
  6. Disinfection
- **Discharge**: To Lieve River (VLAREM II limits)

---

## 2. System Architecture

### 2.1 Design Principle: Distributed Heterogeneous APIs

In real-world water systems, different components are managed by different organizations with different APIs, protocols, and data formats. To test that our ontology can **describe and integrate heterogeneous systems**, each model in our case study exposes its **own independent API**.

**Why this matters:**
- Tests whether the ontology can describe diverse API styles
- Simulates real-world integration challenges
- Forces the ontology to be the "lingua franca" for discovery
- Allows testing different backends (REST, GraphQL, gRPC, etc.)

### 2.2 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           STREAMLIT FRONTEND                                │
│  ┌──────────────┐  ┌──────────────────┐  ┌────────────────────────────────┐│
│  │  Map View    │  │ Natural Language │  │  Simulation Status & Results   ││
│  │  (Folium)    │  │   Query Input    │  │                                ││
│  └──────────────┘  └────────┬─────────┘  └────────────────────────────────┘│
└─────────────────────────────┼───────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR / GATEWAY (FastAPI)                         │
│  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────────┐│
│  │   LLM Endpoint     │  │  Ontology Store    │  │   Model Registry       ││
│  │   (NL → SPARQL)    │  │  (waterFRAME TTL)  │  │   (discovers models)   ││
│  └─────────┬──────────┘  └────────────────────┘  └────────────────────────┘│
│            │                                                                │
│  ┌─────────▼──────────────────────────────────────────────────────────────┐│
│  │                        SPARQL Query Engine                              ││
│  │  - Queries combined graph (ontology + all model descriptions)          ││
│  │  - Determines which models to invoke for a given question              ││
│  │  - Aggregates results from multiple model calls                        ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │ HTTP calls to diverse APIs
       ┌──────────────────────┼──────────────────────────────────┐
       │                      │                                  │
       ▼                      ▼                                  ▼
┌─────────────────┐  ┌─────────────────┐               ┌─────────────────┐
│  DWP-1 Model    │  │  WWTP-1 Model   │      ...      │  River Model    │
│  Port: 8001     │  │  Port: 8002     │               │  Port: 8010     │
│  ═══════════════│  │  ═══════════════│               │  ═══════════════│
│  REST API       │  │  REST API       │               │  REST API       │
│  (FastAPI)      │  │  (FastAPI)      │               │  (Ribasim/Julia)│
│                 │  │                 │               │                 │
│ GET /describe   │  │ GET /describe   │               │ GET /describe   │
│ POST /simulate  │  │ POST /simulate  │               │ POST /simulate  │
│ GET /state      │  │ GET /state      │               │ GET /state      │
└─────────────────┘  └─────────────────┘               └─────────────────┘
        │                    │                                  │
        └────────────────────┴──────────────────────────────────┘
                             │
                    Each model returns its
                    self-description in TTL/JSON-LD
                    using waterFRAME ontology
```

### 2.3 Component Responsibilities

| Component | Technology | Port | Responsibility |
|-----------|------------|------|----------------|
| Frontend | Streamlit + Folium | 8501 | Map visualization, NL query input, results display |
| Orchestrator | FastAPI | 8000 | LLM endpoint, ontology store, model discovery, SPARQL |
| DWP-1 Model | FastAPI (stub→QSDsan) | 8001 | Drinking water treatment upstream |
| DWP-2 Model | FastAPI (stub→QSDsan) | 8002 | Drinking water treatment downstream |
| WWTP-1 Model | FastAPI (stub→QSDsan) | 8003 | Wastewater treatment upstream |
| WWTP-2 Model | FastAPI (stub→QSDsan) | 8004 | Wastewater treatment downstream |
| Industry Models | FastAPI (stub) | 8005-8009 | Texfin, FoodPro, ChipTech, PharmaGen, BrewCo |
| River Model | FastAPI (stub→Ribasim) | 8010 | River water quality and flow |
| Residential Models | FastAPI (stub) | 8011-8012 | Dampoort, Muide districts |

### 2.4 Model Self-Registration

On startup, each model:

1. Reads its configuration (entity it represents, capabilities)
2. Generates its self-description in waterFRAME ontology
3. Registers with the orchestrator at `POST /api/v1/register`
4. The orchestrator adds the model's description to the combined graph

This enables **dynamic discovery** - agents and users can query what models exist and what they can do.

### 2.5 Ontology Mapping Agent (Foreign Ontology Integration)

**Scenario**: In real-world systems, not all models will describe themselves using waterFRAME. A model might use:
- SAREF4WATER (IoT-focused)
- SSN/SOSA (sensor observations)
- Schema.org (generic)
- A proprietary/internal ontology
- No ontology at all (just JSON)

**Solution**: The orchestrator includes a **Mapping Agent** that can translate foreign ontology descriptions into waterFRAME-compatible RDF.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ORCHESTRATOR                                    │
│                                                                              │
│  ┌──────────────────┐     ┌──────────────────────────────────────────────┐ │
│  │ Model Registry   │────▶│           MAPPING AGENT                       │ │
│  │                  │     │                                              │ │
│  │ Receives:        │     │  1. Detect source ontology (or raw JSON)    │ │
│  │ - waterFRAME TTL │     │  2. Load appropriate mapping rules          │ │
│  │ - SAREF4WATER    │     │  3. Transform to waterFRAME vocabulary      │ │
│  │ - SSN/SOSA       │     │  4. Validate transformed graph              │ │
│  │ - Raw JSON       │     │  5. Return waterFRAME-compatible TTL        │ │
│  │ - Unknown RDF    │     │                                              │ │
│  └──────────────────┘     │  Can use:                                    │ │
│                           │  - Static mapping rules (SPARQL CONSTRUCT)  │ │
│                           │  - LLM-assisted mapping (for unknown)       │ │
│                           │  - Alignment ontologies (OWL sameAs)        │ │
│                           └──────────────────────────────────────────────┘ │
│                                          │                                  │
│                                          ▼                                  │
│                           ┌──────────────────────────────────────────────┐ │
│                           │         UNIFIED KNOWLEDGE GRAPH              │ │
│                           │  (All models described in waterFRAME)        │ │
│                           └──────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Implementation approach**:

| Source Format | Mapping Strategy |
|--------------|------------------|
| waterFRAME TTL | Pass through (no mapping needed) |
| SAREF4WATER | Static SPARQL CONSTRUCT rules |
| SSN/SOSA | Static alignment ontology |
| Schema.org | Static mapping + inference |
| Unknown RDF | LLM-assisted mapping with human review |
| Raw JSON | JSON-LD frame + LLM schema inference |

**Stub implementation** for Phase 1:
```python
# orchestrator/mapping_agent.py

class MappingAgent:
    """Translates foreign ontology descriptions to waterFRAME."""

    def detect_ontology(self, rdf_graph: Graph) -> str:
        """Detect which ontology the model is using."""
        # Check for known namespace prefixes
        ...

    def map_to_waterframe(self, source_graph: Graph, source_ontology: str) -> Graph:
        """Transform source graph to waterFRAME vocabulary."""
        if source_ontology == "waterframe":
            return source_graph  # No mapping needed
        elif source_ontology == "saref4water":
            return self._map_saref4water(source_graph)
        elif source_ontology == "ssn":
            return self._map_ssn(source_graph)
        else:
            return self._llm_assisted_mapping(source_graph)

    def _llm_assisted_mapping(self, source_graph: Graph) -> Graph:
        """Use LLM to suggest mappings for unknown ontologies."""
        # Stub: returns empty graph with TODO marker
        ...
```

**Testing scenario**: Configure one of the industry models (e.g., ChipTech) to describe itself using SAREF4WATER instead of waterFRAME, then verify the mapping agent correctly translates it.

### 2.6 Directory Structure (Separated Concerns)

The case study is a **separate project** at the repository root, with its own dependencies:

```
ontEAUlogy/                              # Repository root
│
├── data/                                # ONTOLOGY DEVELOPMENT
│   └── ontology/                        # waterFRAME ontology (existing)
│       ├── waterframe.ttl
│       ├── modules/
│       │   ├── core/
│       │   │   ├── material_entities.ttl
│       │   │   └── properties.ttl
│       │   ├── information.ttl          # NEW: model metadata
│       │   ├── capabilities.ttl         # NEW: simulation capabilities
│       │   └── qualities.ttl            # NEW: water quality
│       └── instances/
│           └── household_case1.ttl
│
├── research/                            # Research materials (existing)
│
├── src/                                 # Ontology utilities (existing)
│   └── helpers.py
│
├── tests/                               # Ontology tests (existing)
│
├── notebooks/                           # Ontology exploration (existing)
│
└── case_studies/                        # CASE STUDY PROJECTS
    └── ghent/                           # Ghent synthetic system
        ├── pyproject.toml               # Separate dependencies!
        ├── README.md
        │
        ├── data/                        # Case study data
        │   ├── system.ttl               # Full system description
        │   └── instances/               # Individual entity TTL files
        │       ├── lieve_river.ttl
        │       ├── dwp1.ttl
        │       ├── dwp2.ttl
        │       ├── wwtp1.ttl
        │       ├── wwtp2.ttl
        │       ├── dampoort_residential.ttl
        │       ├── muide_residential.ttl
        │       ├── texfin.ttl
        │       ├── foodpro.ttl
        │       ├── chiptech.ttl
        │       ├── pharmagen.ttl
        │       └── brewco.ttl
        │
        ├── src/                         # Case study code
        │   └── ghent_water/
        │       ├── __init__.py
        │       │
        │       ├── orchestrator/        # Central gateway
        │       │   ├── __init__.py
        │       │   ├── main.py          # FastAPI orchestrator app
        │       │   ├── llm_sparql.py    # NL → SPARQL translation
        │       │   ├── ontology_store.py
        │       │   └── model_registry.py
        │       │
        │       ├── models/              # Individual model services
        │       │   ├── __init__.py
        │       │   ├── base.py          # Abstract model with /describe
        │       │   │
        │       │   ├── stubs/           # Stub implementations
        │       │   │   ├── dwp.py       # Drinking water plant stub
        │       │   │   ├── wwtp.py      # Wastewater plant stub
        │       │   │   ├── industry.py  # Generic industry stub
        │       │   │   ├── residential.py
        │       │   │   └── river.py
        │       │   │
        │       │   ├── qsdsan/          # Future: QSDsan backends
        │       │   ├── ribasim/         # Future: Ribasim backends
        │       │   └── peepypoo/        # Future: PeePyPoo backends
        │       │
        │       └── frontend/            # Streamlit app
        │           ├── __init__.py
        │           ├── app.py
        │           └── components/
        │               ├── map.py
        │               ├── query_panel.py
        │               └── results.py
        │
        ├── tests/
        │   ├── test_orchestrator/
        │   ├── test_models/
        │   └── test_integration/
        │
        └── scripts/
            ├── run_all.py               # Start all services
            ├── run_orchestrator.py
            └── run_model.py             # Start single model by name
```

---

## 3. API Design (Agent-Friendly)

### 3.1 Core Principles

1. **Self-Describing**: Every model endpoint returns its capabilities in RDF/JSON-LD
2. **Discoverable**: A root endpoint lists all available models and their URIs
3. **Queryable**: SPARQL can discover what models can answer what questions
4. **Stateless**: Each simulation request is independent
5. **Async-Ready**: Long simulations return job IDs for polling

### 3.2 API Endpoints

#### Discovery Endpoints

```
GET /api/v1/
    Returns: JSON-LD with links to all endpoints and system description

GET /api/v1/models/
    Returns: List of all registered models with their ontology URIs

GET /api/v1/models/{model_id}/describe
    Returns: JSON-LD/Turtle describing this model's:
      - Inputs (parameters, streams)
      - Outputs (results, streams)
      - Capabilities (simulation types it can perform)
      - Current state
```

#### Query Endpoints

```
POST /api/v1/query/sparql
    Body: { "query": "SELECT ...", "format": "json" }
    Returns: SPARQL query results

POST /api/v1/query/natural
    Body: { "question": "What is the effluent BOD from WWTP-1?" }
    Returns: {
      "sparql_query": "SELECT ...",      # Generated SPARQL
      "requires_simulation": true,        # Whether models need to run
      "models_to_invoke": ["wwtp1"],      # Which models are needed
      "result": { ... }                   # Query/simulation results
    }

    This endpoint uses the LLM to:
    1. Parse the natural language question
    2. Generate appropriate SPARQL query
    3. Determine if answering requires model simulation
    4. Orchestrate model calls if needed
    5. Return aggregated results
```

#### Simulation Endpoints

```
POST /api/v1/models/{model_id}/run
    Body: {
      "inputs": { ... },
      "scenario": "baseline" | "optimized",
      "callback_url": "optional webhook"
    }
    Returns: { "job_id": "...", "status": "queued" }

GET /api/v1/jobs/{job_id}
    Returns: Job status and results when complete

GET /api/v1/models/{model_id}/state
    Returns: Current model state (last run results)
```

#### Ontology Endpoints

```
GET /api/v1/ontology/
    Returns: Full merged ontology graph (waterFRAME + instances)

GET /api/v1/ontology/entity/{uri}
    Returns: All triples about a specific entity

POST /api/v1/ontology/validate
    Body: Turtle/JSON-LD data to validate
    Returns: SHACL validation results
```

### 3.3 Model Self-Description Schema (Capability-Based)

Models describe themselves using **capabilities** rather than linking to specific competency questions. Capabilities describe what types of simulations/analyses the model can perform.

**Why capability-based (not CQ-based)?**
- Competency questions are essentially infinite (natural language is open-ended)
- Capabilities are finite and well-defined (steady-state, dynamic, sensitivity, etc.)
- An LLM can determine which capabilities are needed to answer a question
- Capabilities map cleanly to simulation modes and required inputs

**Capability Taxonomy** (defined in `capabilities.ttl`):

| Capability | Description | Typical Inputs |
|------------|-------------|----------------|
| `SteadyStateSimulation` | Computes equilibrium state | Flow rates, concentrations |
| `DynamicSimulation` | Time-series simulation | Initial conditions, time horizon, time step |
| `SensitivityAnalysis` | Parameter sensitivity | Parameter ranges, number of samples |
| `UncertaintyQuantification` | Monte Carlo / uncertainty | Distributions, sample count |
| `Optimization` | Find optimal parameters | Objective, constraints, bounds |
| `MassBalance` | Conservation calculations | Inlet streams |
| `EnergyBalance` | Energy consumption | Operating parameters |
| `CostEstimation` | Economic analysis | Unit costs, rates |

**Example model self-description** (DWP-1):

```turtle
@prefix wf: <https://w3id.org/waterframe/> .
@prefix cap: <https://w3id.org/waterframe/capability/> .
@prefix ghent: <https://w3id.org/waterframe/case/ghent/> .

ghent:DWP1_Model a wf:ProcessModel ;
    rdfs:label "Drinking Water Plant 1 Model (Upstream)" ;
    wf:representsEntity ghent:DWP1 ;

    # What the model can do (capabilities)
    wf:hasCapability [
        a cap:SteadyStateSimulation ;
        cap:description "Compute treatment performance at steady state" ;
        cap:requiredInputs ( "raw_water_flow" "raw_water_quality" ) ;
        cap:producesOutputs ( "treated_water_flow" "treated_water_quality" "energy_consumption" )
    ] ;
    wf:hasCapability [
        a cap:DynamicSimulation ;
        cap:description "Simulate time-varying treatment response" ;
        cap:requiredInputs ( "raw_water_flow_timeseries" "time_horizon" "time_step" ) ;
        cap:producesOutputs ( "treated_water_timeseries" )
    ] ;
    wf:hasCapability [
        a cap:MassBalance ;
        cap:description "Verify mass conservation across treatment train"
    ] ;

    # Model inputs (what it needs)
    wf:hasInput [
        a wf:ModelInput ;
        wf:parameterName "raw_water_flow" ;
        wf:unit <http://qudt.org/vocab/unit/M3-PER-DAY> ;
        wf:minValue 0 ;
        wf:maxValue 3000 ;
        wf:isDecisionVariable false ;
        wf:description "Incoming raw water flow rate from river intake"
    ] ;
    wf:hasInput [
        a wf:ModelInput ;
        wf:parameterName "coagulant_dose" ;
        wf:unit <http://qudt.org/vocab/unit/MilliGM-PER-L> ;
        wf:minValue 10 ;
        wf:maxValue 100 ;
        wf:isDecisionVariable true ;  # Can be optimized!
        wf:description "Coagulant dosing rate"
    ] ;

    # Model outputs (what it produces)
    wf:hasOutput [
        a wf:ModelOutput ;
        wf:parameterName "treated_water_flow" ;
        wf:unit <http://qudt.org/vocab/unit/M3-PER-DAY>
    ] ;
    wf:hasOutput [
        a wf:ModelOutput ;
        wf:parameterName "treated_water_turbidity" ;
        wf:unit <http://qudt.org/vocab/unit/NTU>
    ] ;
    wf:hasOutput [
        a wf:ModelOutput ;
        wf:parameterName "energy_consumption" ;
        wf:unit <http://qudt.org/vocab/unit/KiloW-HR-PER-M3>
    ] ;

    # Implementation details
    wf:implementedBy "stub" ;  # Later: "qsdsan", "ribasim"
    wf:apiEndpoint <http://localhost:8001> ;
    wf:apiVersion "1.0" .
```

### 3.4 LLM-Powered Natural Language to SPARQL Translation

The orchestrator includes an LLM endpoint that translates natural language questions into SPARQL queries.

**Architecture**:

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        LLM SPARQL Translation                               │
│                                                                             │
│  User Question                                                              │
│  "What would happen to river quality if we doubled WWTP-1 discharge?"       │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. CONTEXT RETRIEVAL                                                │   │
│  │    - Load waterFRAME ontology schema (classes, properties)          │   │
│  │    - Load registered model descriptions (capabilities, I/O)         │   │
│  │    - Load system topology (what connects to what)                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 2. LLM PROMPT                                                       │   │
│  │    System: You are a SPARQL query generator for water systems.      │   │
│  │            Here is the ontology: [schema]                           │   │
│  │            Here are available models: [model descriptions]          │   │
│  │            Here is the system topology: [topology]                  │   │
│  │                                                                     │   │
│  │    User: [question]                                                 │   │
│  │                                                                     │   │
│  │    Output:                                                          │   │
│  │    - SPARQL query to retrieve relevant data                         │   │
│  │    - Whether simulation is needed (and which models)                │   │
│  │    - What inputs to vary (if scenario analysis)                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 3. EXECUTION                                                        │   │
│  │    - Run SPARQL query against knowledge graph                       │   │
│  │    - If simulation needed: invoke model(s) via their APIs           │   │
│  │    - Aggregate results                                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 4. RESPONSE GENERATION                                              │   │
│  │    - Format results for human readability                           │   │
│  │    - Include provenance (which models ran, what queries executed)   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────┘
```

**Example flow**:

| Step | Input | Output |
|------|-------|--------|
| Question | "What is the BOD at WWTP-1 effluent?" | - |
| SPARQL Generated | - | `SELECT ?bod WHERE { ghent:WWTP1 wf:hasEffluent ?eff . ?eff wf:hasBOD ?bod }` |
| Query Result | - | No data (model hasn't run yet) |
| Decision | - | Needs simulation: invoke WWTP1 model |
| Simulation | `POST /simulate` to WWTP1 | `{"effluent_bod": 18.5}` |
| Final Answer | - | "The BOD at WWTP-1 effluent is 18.5 mg/L (from simulation)" |

### 3.5 Agent Discovery Protocol

An optimization agent can discover the system by:

1. **GET /api/v1/** → Learn about available endpoints
2. **GET /api/v1/ontology/** → Download full system graph
3. **POST /api/v1/query/sparql** → Query for decision variables:
   ```sparql
   SELECT ?var ?min ?max ?unit WHERE {
     ?model model:hasInput ?input .
     ?input model:isDecisionVariable true ;
            model:parameterName ?var ;
            model:minValue ?min ;
            model:maxValue ?max ;
            model:unit ?unit .
   }
   ```
4. **POST /api/v1/models/{id}/run** → Run simulations with different inputs
5. **Aggregate results** → Compute objective function

---

## 4. Ontology Extensions Required

### 4.1 New Module: `information.ttl`

This module defines classes for computational model metadata:

```turtle
@prefix wf: <https://w3id.org/waterframe/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

# Core Model Classes
wf:ProcessModel a owl:Class ;
    rdfs:label "Process Model" ;
    rdfs:comment "A computational model that simulates a water system component" .

wf:ModelInput a owl:Class ;
    rdfs:label "Model Input" ;
    rdfs:comment "An input parameter or stream for a model" .

wf:ModelOutput a owl:Class ;
    rdfs:label "Model Output" ;
    rdfs:comment "An output result or stream from a model" .

# Properties linking model to entity
wf:representsEntity a owl:ObjectProperty ;
    rdfs:domain wf:ProcessModel ;
    rdfs:range wf:WaterSystemComponent ;
    rdfs:comment "Links a model to the physical entity it simulates" .

# Input/Output properties
wf:hasInput a owl:ObjectProperty ;
    rdfs:domain wf:ProcessModel ;
    rdfs:range wf:ModelInput .

wf:hasOutput a owl:ObjectProperty ;
    rdfs:domain wf:ProcessModel ;
    rdfs:range wf:ModelOutput .

wf:parameterName a owl:DatatypeProperty ;
    rdfs:domain [ owl:unionOf (wf:ModelInput wf:ModelOutput) ] ;
    rdfs:range xsd:string .

wf:unit a owl:ObjectProperty ;
    rdfs:comment "Links to QUDT unit" .

wf:minValue a owl:DatatypeProperty ;
    rdfs:range xsd:decimal .

wf:maxValue a owl:DatatypeProperty ;
    rdfs:range xsd:decimal .

wf:isDecisionVariable a owl:DatatypeProperty ;
    rdfs:domain wf:ModelInput ;
    rdfs:range xsd:boolean ;
    rdfs:comment "True if this input can be optimized by an agent" .

# Implementation metadata
wf:implementedBy a owl:DatatypeProperty ;
    rdfs:range xsd:string ;
    rdfs:comment "Implementation backend: stub, qsdsan, ribasim, peepypoo" .

wf:apiEndpoint a owl:DatatypeProperty ;
    rdfs:range xsd:anyURI ;
    rdfs:comment "URL where this model's API is accessible" .

wf:apiVersion a owl:DatatypeProperty ;
    rdfs:range xsd:string .

# Capability linkage (see capabilities.ttl)
wf:hasCapability a owl:ObjectProperty ;
    rdfs:domain wf:ProcessModel ;
    rdfs:range wf:ModelCapability ;
    rdfs:comment "Links model to simulation capabilities it supports" .
```

### 4.2 New Module: `capabilities.ttl`

Defines simulation capability types that models can advertise:

```turtle
@prefix wf: <https://w3id.org/waterframe/> .
@prefix cap: <https://w3id.org/waterframe/capability/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

# Base capability class
wf:ModelCapability a owl:Class ;
    rdfs:label "Model Capability" ;
    rdfs:comment "A type of simulation or analysis a model can perform" .

# Capability types
cap:SteadyStateSimulation a owl:Class ;
    rdfs:subClassOf wf:ModelCapability ;
    rdfs:label "Steady-State Simulation" ;
    rdfs:comment "Computes equilibrium state given constant inputs" .

cap:DynamicSimulation a owl:Class ;
    rdfs:subClassOf wf:ModelCapability ;
    rdfs:label "Dynamic Simulation" ;
    rdfs:comment "Time-series simulation with varying inputs" .

cap:SensitivityAnalysis a owl:Class ;
    rdfs:subClassOf wf:ModelCapability ;
    rdfs:label "Sensitivity Analysis" ;
    rdfs:comment "Analyzes output sensitivity to input parameter variations" .

cap:UncertaintyQuantification a owl:Class ;
    rdfs:subClassOf wf:ModelCapability ;
    rdfs:label "Uncertainty Quantification" ;
    rdfs:comment "Monte Carlo or similar probabilistic analysis" .

cap:Optimization a owl:Class ;
    rdfs:subClassOf wf:ModelCapability ;
    rdfs:label "Optimization" ;
    rdfs:comment "Finds optimal parameter values given constraints" .

cap:MassBalance a owl:Class ;
    rdfs:subClassOf wf:ModelCapability ;
    rdfs:label "Mass Balance" ;
    rdfs:comment "Verifies conservation of mass across system" .

cap:EnergyBalance a owl:Class ;
    rdfs:subClassOf wf:ModelCapability ;
    rdfs:label "Energy Balance" ;
    rdfs:comment "Calculates energy consumption and flows" .

cap:CostEstimation a owl:Class ;
    rdfs:subClassOf wf:ModelCapability ;
    rdfs:label "Cost Estimation" ;
    rdfs:comment "Economic analysis of capital and operating costs" .

cap:WaterQualityPrediction a owl:Class ;
    rdfs:subClassOf wf:ModelCapability ;
    rdfs:label "Water Quality Prediction" ;
    rdfs:comment "Predicts effluent/output water quality parameters" .

# Capability properties
cap:description a owl:DatatypeProperty ;
    rdfs:domain wf:ModelCapability ;
    rdfs:range xsd:string .

cap:requiredInputs a owl:DatatypeProperty ;
    rdfs:domain wf:ModelCapability ;
    rdfs:comment "List of input parameter names required for this capability" .

cap:producesOutputs a owl:DatatypeProperty ;
    rdfs:domain wf:ModelCapability ;
    rdfs:comment "List of output parameter names this capability produces" .
```

### 4.3 Extensions to `material_entities.ttl`

Add new entity types for the Ghent case study:

```turtle
# Drinking Water Treatment (more specific than generic WTP)
wf:DrinkingWaterPlant a owl:Class ;
    rdfs:subClassOf wf:WaterSystemComponent ;
    rdfs:label "Drinking Water Treatment Plant" .

wf:WastewaterTreatmentPlant a owl:Class ;
    rdfs:subClassOf wf:WaterSystemComponent ;
    rdfs:label "Wastewater Treatment Plant" .

# Industrial Facilities (base + specific types)
wf:IndustrialFacility a owl:Class ;
    rdfs:subClassOf wf:WaterSystemComponent ;
    rdfs:label "Industrial Facility" .

wf:TextileIndustry a owl:Class ;
    rdfs:subClassOf wf:IndustrialFacility ;
    rdfs:label "Textile Industry" .

wf:FoodProcessingIndustry a owl:Class ;
    rdfs:subClassOf wf:IndustrialFacility ;
    rdfs:label "Food Processing Industry" .

wf:ElectronicsManufacturing a owl:Class ;
    rdfs:subClassOf wf:IndustrialFacility ;
    rdfs:label "Electronics Manufacturing" .

wf:PharmaceuticalIndustry a owl:Class ;
    rdfs:subClassOf wf:IndustrialFacility ;
    rdfs:label "Pharmaceutical Industry" .

wf:Brewery a owl:Class ;
    rdfs:subClassOf wf:IndustrialFacility ;
    rdfs:label "Brewery" .

# Residential
wf:ResidentialDistrict a owl:Class ;
    rdfs:subClassOf wf:WaterSystemComponent ;
    rdfs:label "Residential District" .

# Natural Water Bodies
wf:River a owl:Class ;
    rdfs:subClassOf wf:WaterSystemComponent ;
    rdfs:label "River" .

wf:RiverSegment a owl:Class ;
    rdfs:subClassOf wf:River ;
    rdfs:label "River Segment" ;
    rdfs:comment "A specific reach or segment of a river" .
```

### 4.4 New Module: `qualities.ttl`

Water quality parameters:

```turtle
wf:WaterQualityParameter a owl:Class ;
    rdfs:label "Water Quality Parameter" .

wf:Turbidity a owl:Class ; rdfs:subClassOf wf:WaterQualityParameter .
wf:BOD a owl:Class ; rdfs:subClassOf wf:WaterQualityParameter .
wf:COD a owl:Class ; rdfs:subClassOf wf:WaterQualityParameter .
wf:TSS a owl:Class ; rdfs:subClassOf wf:WaterQualityParameter .
wf:pH a owl:Class ; rdfs:subClassOf wf:WaterQualityParameter .
wf:Temperature a owl:Class ; rdfs:subClassOf wf:WaterQualityParameter .
wf:Conductivity a owl:Class ; rdfs:subClassOf wf:WaterQualityParameter .
wf:TotalNitrogen a owl:Class ; rdfs:subClassOf wf:WaterQualityParameter .
wf:TotalPhosphorus a owl:Class ; rdfs:subClassOf wf:WaterQualityParameter .

wf:hasQualityRequirement a owl:ObjectProperty ;
    rdfs:domain wf:WaterSystemComponent ;
    rdfs:range wf:WaterQualityRequirement .

wf:WaterQualityRequirement a owl:Class ;
    rdfs:label "Water Quality Requirement" .

wf:hasParameter a owl:ObjectProperty ;
    rdfs:domain wf:WaterQualityRequirement ;
    rdfs:range wf:WaterQualityParameter .

wf:hasMaxValue a owl:DatatypeProperty .
wf:hasMinValue a owl:DatatypeProperty .
wf:regulatedBy a owl:ObjectProperty .  # Links to legislation
```

---

## 5. Frontend Design

### 5.1 Main Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│  🌊 Ghent Water System Explorer                              [⚙️ Settings] │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────┐  ┌──────────────────────────────┐  │
│  │                                 │  │  SPARQL Query Interface      │  │
│  │         MAP VIEW                │  │  ┌──────────────────────┐    │  │
│  │        (Folium)                 │  │  │ SELECT ?x WHERE {    │    │  │
│  │                                 │  │  │   ?x a wf:WWTP .     │    │  │
│  │   [🏭] Dampoort Industries      │  │  │ }                    │    │  │
│  │   [🏠] Muide Residential        │  │  └──────────────────────┘    │  │
│  │   [💧] WTP                      │  │  [▶ Run Query]               │  │
│  │   [🚰] WWTP-1, WWTP-2           │  │                              │  │
│  │   [🌊] Lieve River              │  │  ─── OR ───                  │  │
│  │                                 │  │                              │  │
│  │   Click entity for details     │  │  Natural Language:           │  │
│  │                                 │  │  ┌──────────────────────┐    │  │
│  └─────────────────────────────────┘  │  │ What is the BOD      │    │  │
│                                       │  │ discharge from WWTP1?│    │  │
│  ┌─────────────────────────────────┐  │  └──────────────────────┘    │  │
│  │  Entity Details Panel           │  │  [🔍 Ask]                    │  │
│  │  ─────────────────────────────  │  └──────────────────────────────┘  │
│  │  Selected: WWTP-1               │                                    │
│  │  Type: WastewaterTreatmentPlant │  ┌──────────────────────────────┐  │
│  │  Capacity: 2000 m³/day          │  │  Simulation Status           │  │
│  │  Status: 🟢 Idle                │  │  ─────────────────────────── │  │
│  │                                 │  │  Model: WWTP-1               │  │
│  │  Inputs:                        │  │  Status: ⏳ Running...       │  │
│  │   - influent_flow: 1800 m³/d    │  │  Progress: ████████░░ 80%   │  │
│  │   - influent_BOD: 350 mg/L      │  │                              │  │
│  │                                 │  │  Inputs:                     │  │
│  │  Outputs:                       │  │   flow=1800, BOD=350         │  │
│  │   - effluent_flow: 1750 m³/d    │  │                              │  │
│  │   - effluent_BOD: 15 mg/L       │  │  Objective: minimize_energy  │  │
│  │                                 │  └──────────────────────────────┘  │
│  │  [📊 View Model] [▶ Simulate]   │                                    │
│  └─────────────────────────────────┘                                    │
├─────────────────────────────────────────────────────────────────────────┤
│  Query Results                                                          │
│  ═══════════════════════════════════════════════════════════════════   │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ Answer: The BOD discharge from WWTP-1 is 15 mg/L (simulation      │ │
│  │ required, completed in 2.3s)                                      │ │
│  │                                                                   │ │
│  │ Supporting Data:                                                  │ │
│  │ ┌─────────────┬──────────────┬─────────────┐                     │ │
│  │ │ Parameter   │ Value        │ Unit        │                     │ │
│  │ ├─────────────┼──────────────┼─────────────┤                     │ │
│  │ │ effluent_BOD│ 15.2         │ mg/L        │                     │ │
│  │ │ flow_rate   │ 1750         │ m³/day      │                     │ │
│  │ └─────────────┴──────────────┴─────────────┘                     │ │
│  └───────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Key Features

1. **Interactive Map**:
   - Folium map centered on Ghent
   - Markers for each entity with popup summaries
   - Lines showing flow connections
   - Color-coded status (idle/running/error)

2. **SPARQL Query Panel**:
   - Syntax-highlighted editor
   - Pre-loaded example queries
   - Results as table or graph visualization

3. **Entity Details**:
   - Click entity on map → show details
   - Display current state from last simulation
   - Button to trigger new simulation

4. **Simulation Status**:
   - Real-time progress for running models
   - Shows which query triggered simulation
   - Displays inputs/outputs

5. **Results Panel**:
   - Formatted answer to query
   - Supporting data tables
   - Export options (CSV, JSON-LD)

---

## 6. Implementation Phases

### Phase 1: Foundation (Skeleton)
**Goal**: Working end-to-end system with stubs

1. **Ontology Extensions**
   - Create `information.ttl` module for model metadata
   - Extend `material_entities.ttl` with new entity types
   - Create `qualities.ttl` for water quality parameters

2. **Case Study Data**
   - Create `data/case_studies/ghent/` directory
   - Write TTL files for each entity instance
   - Create system topology connections

3. **Backend Skeleton**
   - FastAPI app with router structure
   - Model registry with discovery endpoint
   - SPARQL query endpoint (basic)

4. **Stub Models**
   - Base model class with describe/run interface
   - Stub implementations returning mock data
   - Self-description in waterFRAME ontology

5. **Frontend Skeleton**
   - Streamlit app with basic layout
   - Static map with entity markers
   - Simple query input → result display

### Phase 2: Integration
**Goal**: Full query-to-simulation pipeline

1. **Model Orchestrator**
   - Route queries to appropriate models
   - Handle async simulation jobs
   - Aggregate results from multiple models

2. **Enhanced Frontend**
   - Dynamic map updates during simulation
   - Entity click → details panel
   - Real-time simulation status

3. **SPARQL Enhancements**
   - Query templates for common questions
   - Results linked to simulation triggers
   - Natural language → SPARQL translation (basic)

### Phase 3: Real Models
**Goal**: Replace stubs with real physics

1. **QSDsan Integration**
   - Implement WTP model
   - Implement WWTP models
   - Connect to ontology descriptions

2. **Ribasim Integration**
   - Implement river model
   - Implement water balance calculations

3. **PeePyPoo Integration** (if applicable)
   - Research package capabilities
   - Implement relevant models

### Phase 4: Agent Support
**Goal**: Enable autonomous optimization agents

1. **Agent API**
   - Decision variable discovery endpoint
   - Batch simulation endpoint
   - Objective function definition

2. **Example Agent**
   - Simple optimization agent
   - Demonstrates discovery → optimize → report

3. **Documentation**
   - Agent developer guide
   - API reference
   - Example notebooks

---

## 7. Dependencies to Add

```toml
[project.dependencies]
# Existing...

# New for case study system
fastapi = ">=0.115"
uvicorn = ">=0.34"
streamlit = ">=1.41"
folium = ">=0.19"
streamlit-folium = ">=0.23"
httpx = ">=0.28"          # Async HTTP client
pydantic = ">=2.10"       # Data validation

# Future model backends
# qsdsan = ">=1.3"        # Uncomment when needed
# ribasim = ">=2024.11"   # Uncomment when needed
# peepypoo = ">=x.x"      # Research version
```

---

## 8. Success Criteria

The system is successful when:

1. **Ontology Adequacy**:
   - [ ] All 12 entities in Ghent system have complete TTL descriptions
   - [ ] Flow topology queryable via SPARQL (upstream/downstream relationships)
   - [ ] Model capabilities described in ontology using capability taxonomy

2. **Model-Entity Mapping**:
   - [ ] Each entity has a corresponding model with its own API
   - [ ] Model describes itself using waterFRAME ontology terms
   - [ ] Bidirectional linking (entity ↔ model)

3. **Human Query Interface**:
   - [ ] User can run SPARQL queries and get results
   - [ ] User can ask natural language questions (LLM translation)
   - [ ] Simulation triggered automatically when needed
   - [ ] Results displayed clearly with provenance

4. **Agent Discovery**:
   - [ ] Agent can enumerate all entities via API
   - [ ] Agent can discover decision variables and their bounds
   - [ ] Agent can query model capabilities
   - [ ] Agent can run simulations and get results

5. **Foreign Ontology Integration**:
   - [ ] At least one model describes itself using non-waterFRAME ontology
   - [ ] Mapping agent correctly translates to waterFRAME vocabulary
   - [ ] Unified knowledge graph includes all models regardless of source ontology

---

## 9. Open Questions

1. **PeePyPoo Package**: Need to research capabilities and determine which models it should implement. What specific water system components does it model?

2. **Legislation Data**: Should Flemish water quality regulations be encoded in the ontology, or loaded from external source?

3. **Simulation Persistence**: Should simulation results be persisted in a database for historical queries?

4. **Multi-Model Coordination**: When a query requires multiple models (e.g., "What is the river quality after all discharges?"), how should they be coordinated?

5. **Error Handling**: How should model failures be reported in the ontology/API?

---

## Appendix A: Flemish Water Quality Standards (VLAREM II)

| Parameter | Surface Water Discharge Limit |
|-----------|-------------------------------|
| BOD₅ | 25 mg/L |
| COD | 125 mg/L |
| TSS | 35 mg/L |
| Total N | 15 mg/L |
| Total P | 2 mg/L |
| pH | 6.5 - 9.0 |
| Temperature | < 30°C |

Source: VLAREM II (Vlaams reglement betreffende de milieuvergunning)

---

## Appendix B: Entity Coordinates for Map

### Upstream Zone (Dampoort)

| Entity ID | Latitude | Longitude | Icon | Zone |
|-----------|----------|-----------|------|------|
| lieve_river_upstream | 51.0630 | 3.7280 | 🌊 | Upstream |
| dwp1 | 51.0620 | 3.7300 | 💧 | Upstream |
| dampoort_residential | 51.0600 | 3.7320 | 🏠 | Upstream |
| texfin | 51.0585 | 3.7340 | 👔 | Upstream |
| foodpro | 51.0575 | 3.7360 | 🍕 | Upstream |
| wwtp1 | 51.0560 | 3.7400 | 🚰 | Upstream |

### Downstream Zone (Muide)

| Entity ID | Latitude | Longitude | Icon | Zone |
|-----------|----------|-----------|------|------|
| lieve_river_midstream | 51.0545 | 3.7430 | 🌊 | Downstream |
| dwp2 | 51.0540 | 3.7450 | 💧 | Downstream |
| muide_residential | 51.0520 | 3.7470 | 🏠 | Downstream |
| chiptech | 51.0510 | 3.7490 | 💻 | Downstream |
| pharmagen | 51.0500 | 3.7510 | 💊 | Downstream |
| brewco | 51.0495 | 3.7530 | 🍺 | Downstream |
| wwtp2 | 51.0480 | 3.7560 | 🚰 | Downstream |
| lieve_river_downstream | 51.0470 | 3.7580 | 🌊 | Downstream |

### Flow Connections (for map lines)

| From | To | Type |
|------|-----|------|
| lieve_river_upstream | dwp1 | intake |
| dwp1 | dampoort_residential | supply |
| dwp1 | texfin | supply |
| dwp1 | foodpro | supply |
| dampoort_residential | wwtp1 | wastewater |
| texfin | wwtp1 | wastewater |
| foodpro | wwtp1 | wastewater |
| wwtp1 | lieve_river_midstream | discharge |
| lieve_river_midstream | dwp2 | intake |
| dwp2 | muide_residential | supply |
| dwp2 | chiptech | supply |
| dwp2 | pharmagen | supply |
| dwp2 | brewco | supply |
| muide_residential | wwtp2 | wastewater |
| chiptech | wwtp2 | wastewater |
| pharmagen | wwtp2 | wastewater |
| brewco | wwtp2 | wastewater |
| wwtp2 | lieve_river_downstream | discharge |
