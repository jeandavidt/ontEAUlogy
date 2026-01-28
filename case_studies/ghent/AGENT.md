# AGENT.md - Ghent Water System Case Study

## Quick Overview

This is a **lab bench demonstration** of the waterFRAME ontology applied to a synthetic urban water system based on Ghent, Belgium. It showcases how semantic web technologies can model complex water infrastructure networks and support decision-making.

**Purpose**: Explore and validate the waterFRAME ontology through a working prototype with simulations, SPARQL queries, and natural language interfaces.

---

## Project Location Context

```
ontEAUlogy/                           # Root project
├── data/ontology/                    # waterFRAME ontology definitions
│   ├── waterframe.ttl               # Main ontology file
│   └── modules/                     # Modular ontology components
│       ├── core/material_entities.ttl
│       ├── core/properties.ttl
│       ├── information.ttl
│       ├── capabilities.ttl
│       ├── qualities.ttl           # Water quality parameters
│       ├── sampling.ttl
│       └── compliance.ttl          # Regulatory compliance
└── case_studies/ghent/              # THIS PROJECT
```

---

## Directory Structure

```
ghent/
├── src/ghent_water/
│   ├── frontend/                    # Streamlit web UI
│   │   ├── app.py                  # Main entry point
│   │   ├── config.py               # Frontend settings
│   │   ├── components/
│   │   │   ├── map_view.py         # Interactive Pydeck map
│   │   │   ├── entity_details.py   # Entity info panel
│   │   │   ├── query_panel.py      # SPARQL & NL query interface
│   │   │   ├── results_display.py  # Results visualization
│   │   │   └── simulation_status.py # Job tracking
│   │   └── services/
│   │       └── api_client.py       # HTTP client for orchestrator
│   │
│   ├── orchestrator/                # FastAPI backend
│   │   ├── main.py                 # FastAPI app entry
│   │   ├── config.py               # Backend settings
│   │   ├── routers/
│   │   │   ├── query.py            # SPARQL & NL query endpoints
│   │   │   ├── simulation.py       # Model simulation endpoints
│   │   │   ├── discovery.py        # Model discovery
│   │   │   └── ontology.py         # Ontology management
│   │   ├── services/
│   │   │   ├── ontology_store.py   # RDF graph management
│   │   │   ├── sparql_engine.py    # SPARQL executor (if exists)
│   │   │   ├── model_registry.py   # Model & job tracking
│   │   │   ├── llm_sparql.py       # NL to SPARQL translation
│   │   │   └── mapping_agent.py    # Entity-model mapping
│   │   └── schemas/
│   │       └── models.py           # Pydantic schemas
│   │
│   └── models/                      # Simulation models
│       ├── base.py                 # Abstract BaseWaterModel
│       ├── config.py               # Entity configurations (12 entities)
│       ├── runners/
│       │   └── model_runner.py     # CLI runner for models
│       └── stubs/                  # Stub implementations
│           ├── dwp.py              # Drinking Water Plant
│           ├── wwtp.py             # Wastewater Treatment Plant
│           ├── river.py            # River segment
│           ├── residential.py      # Residential districts
│           └── industry.py         # Industrial facilities
│
├── scripts/
│   ├── run_all.py                  # Master launcher (all components)
│   └── run_orchestrator.py         # Orchestrator-only launcher
│
├── data/
│   ├── system.ttl                  # Master RDF import file
│   └── instances/                  # Entity TTL definitions
│       ├── dwp1.ttl, dwp2.ttl
│       ├── wwtp1.ttl, wwtp2.ttl
│       ├── lieve_river.ttl
│       ├── dampoort_residential.ttl, muide_residential.ttl
│       └── [5 industry files]
│
├── pyproject.toml                  # Dependencies
├── README.md                       # User documentation
├── lab_bench_water_system_plan.md  # Implementation roadmap
└── AGENT.md                        # This file
```

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (Streamlit :8501)                    │
│  ┌─────────┐ ┌─────────────┐ ┌─────────┐ ┌───────────────────┐ │
│  │   Map   │ │ Query Panel │ │ Results │ │ Simulation Status │ │
│  └─────────┘ └─────────────┘ └─────────┘ └───────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Orchestrator (FastAPI :8080)                    │
│  ┌─────────────┐ ┌──────────────┐ ┌─────────────────────────┐  │
│  │ RDF Graph   │ │ Model        │ │ Services                │  │
│  │ (waterFRAME)│ │ Registry     │ │ - SPARQL Engine         │  │
│  └─────────────┘ └──────────────┘ │ - LLM Translator        │  │
│                                   │ - Mapping Agent         │  │
│                                   └─────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
   ┌────────────┐     ┌────────────┐     ┌────────────┐
   │ DWP Models │     │WWTP Models │     │Other Models│
   │ :8001-8002 │     │ :8003-8004 │     │ :8005-8012 │
   └────────────┘     └────────────┘     └────────────┘
```

---

## 12 Simulated Entities

| ID | Type | Port | Description |
|----|------|------|-------------|
| `dwp1` | Drinking Water Plant | 8001 | Raw water treatment (2,000 m³/day) |
| `dwp2` | Drinking Water Plant | 8002 | Raw water treatment (2,500 m³/day) |
| `wwtp1` | Wastewater Plant | 8003 | Effluent treatment (2,000 m³/day) |
| `wwtp2` | Wastewater Plant | 8004 | Effluent treatment (2,500 m³/day) |
| `texfin` | Industry (Textile) | 8005 | 500 m³/day, high COD |
| `foodpro` | Industry (Food) | 8006 | 800 m³/day, high BOD |
| `chiptech` | Industry (Electronics) | 8007 | 200 m³/day, ultra-pure |
| `pharmagen` | Industry (Pharma) | 8008 | 400 m³/day |
| `brewco` | Industry (Brewery) | 8009 | 600 m³/day, high BOD |
| `river` | River (Lieve) | 8010 | Central transport pathway |
| `dampoort` | Residential | 8011 | Upstream district (3,000 people) |
| `muide` | Residential | 8012 | Downstream district (5,000 people) |

---

## Key Entry Points

### Running the System

```bash
# From ghent/ directory

# Option 1: Start everything at once
python scripts/run_all.py

# Option 2: Start components separately
# Terminal 1 - Orchestrator
python scripts/run_orchestrator.py

# Terminal 2+ - Individual models
python -m ghent_water.models.runners.model_runner --model dwp1 --port 8001
python -m ghent_water.models.runners.model_runner --model wwtp1 --port 8003

# Terminal N - Frontend
cd src/ghent_water/frontend && streamlit run app.py
```

### URLs When Running
- **Frontend**: http://localhost:8501
- **Orchestrator API**: http://localhost:8080
- **API Docs**: http://localhost:8080/docs
- **Model Health**: http://localhost:{port}/health

---

## Ontology Reference

**Namespace**: `https://w3id.org/waterframe/`

**Key Prefixes**:
```turtle
@prefix wf:    <https://w3id.org/waterframe/> .
@prefix cap:   <https://w3id.org/waterframe/capability/> .
@prefix ghent: <https://w3id.org/waterframe/case/ghent/> .
```

**Core Classes**:
- `wf:WaterSystem` - Top-level system
- `wf:DrinkingWaterPlant` - DWP facilities
- `wf:WastewaterTreatmentPlant` - WWTP facilities
- `wf:ResidentialArea` - Housing districts
- `wf:IndustrialFacility` - Industrial sites
- `wf:RiverSegment` - River sections

**Water Quality Parameters** (from `qualities.ttl`):
- BOD, COD, TSS, TN (Total Nitrogen), TP (Total Phosphorus)
- pH, Temperature, Dissolved Oxygen
- Flow rate, Capacity

---

## Regulatory Context

**Framework**: VLAREM II (Flemish Environmental Regulations)

**Discharge Limits**:
| Parameter | Limit |
|-----------|-------|
| BOD | 25 mg/L |
| COD | 125 mg/L |
| TSS | 35 mg/L |
| Total N | 15 mg/L |
| Total P | 2 mg/L |

---

## API Endpoints (Orchestrator)

### Query
- `POST /api/v1/query/sparql` - Execute SPARQL query
- `POST /api/v1/query/natural` - Natural language → SPARQL → results
- `POST /api/v1/query/translate` - Just translate NL to SPARQL

### Simulation
- `POST /simulation/models/{model_id}/run` - Start simulation
- `GET /simulation/jobs/{job_id}` - Get job status
- `GET /simulation/models/{model_id}/state` - Get model state

### Discovery
- `GET /discovery/models` - List registered models
- `GET /health` - System health

---

## Known Issues (Current State)

See [lab_bench_water_system_plan.md](lab_bench_water_system_plan.md) for full details.

**UI Issues**:
1. SPARQL example selector doesn't populate query field
2. NL example questions don't populate input
3. "Run Simulation" button lacks visual feedback

**Backend Issues**:
1. LLM translation falls back to demo data on API failure
2. Job status tracking may not update reliably

---

## Key Files to Modify

| Task | Primary Files |
|------|---------------|
| Fix UI callbacks | `frontend/components/query_panel.py` |
| Simulation logic | `models/stubs/*.py` |
| API endpoints | `orchestrator/routers/*.py` |
| LLM translation | `orchestrator/services/llm_sparql.py` |
| Entity config | `models/config.py` |
| RDF data | `data/instances/*.ttl` |

---

## Development Commands

```bash
# Install dependencies
cd case_studies/ghent
uv sync

# Run tests (if configured)
pytest

# Type checking
mypy src/

# Format code
ruff format src/
ruff check src/ --fix
```

---

## Useful SPARQL Queries

```sparql
# List all entities
SELECT ?entity ?type ?name WHERE {
    ?entity a ?type ;
            rdfs:label ?name .
    FILTER(STRSTARTS(STR(?entity), "https://w3id.org/waterframe/case/ghent/"))
}

# Get WWTP connections
SELECT ?wwtp ?input ?output WHERE {
    ?wwtp a wf:WastewaterTreatmentPlant ;
          wf:hasInput ?input ;
          wf:hasOutput ?output .
}

# Find entities by zone
SELECT ?entity ?zone WHERE {
    ?entity wf:locatedInZone ?zone .
}
```

---

## File Modification Guidelines

When modifying this case study:

1. **Models** (`models/stubs/`): Each stub has a `/simulate` endpoint that returns realistic parameter ranges. Follow the existing pattern.

2. **Frontend** (`frontend/`): Streamlit components use session state. Be careful with callback timing.

3. **Orchestrator** (`orchestrator/`): FastAPI routers follow RESTful patterns. Services contain business logic.

4. **RDF Data** (`data/instances/`): Turtle format. Maintain consistency with waterFRAME ontology namespaces.

---

## Related Documentation

- [Implementation Plan](lab_bench_water_system_plan.md) - Detailed roadmap with code examples
- [README.md](README.md) - User-facing documentation
- [waterFRAME Ontology](../../data/ontology/) - Parent ontology definitions
