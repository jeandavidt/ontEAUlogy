# Codebase Structure

**Analysis Date:** 2026-01-19

## Directory Layout

```
case_studies/ghent/
├── .claude/          # Claude AI configuration
├── .planning/        # Planning documents (this file)
├── .venv/            # Python virtual environment
├── data/             # Knowledge graph data (RDF/Turtle files)
│   ├── instances/     # Case study entity instances
│   │   ├── sensors/   # Sensor instance data
│   │   ├── dwp1.ttl, dwp2.ttl, wwtp1.ttl, etc.
│   ├── ontology/      # Ontology structure
│   └── system.ttl    # System definition
├── plans/            # Planning documents
├── scripts/          # Utility scripts
│   ├── run_orchestrator.py
│   └── run_all.py
├── src/ghent_water/  # Main package
│   ├── frontend/      # Streamlit UI
│   ├── models/        # Model microservices
│   └── orchestrator/  # FastAPI backend
├── .env              # Environment variables
├── pyproject.toml    # Python package config
├── README.md         # Documentation
└── TESTING_PLAN.md   # Testing documentation
```

## Directory Purposes

**data/:**
- Purpose: Knowledge graph storage in RDF/Turtle format
- Contains: Ontology definitions, entity instances, sensor data
- Key files: `data/system.ttl`, `data/instances/*.ttl`, `data/instances/sensors/*.ttl`

**src/ghent_water/frontend/:**
- Purpose: Streamlit web interface for user interaction
- Contains: Main app, UI components, API clients, static assets
- Key files: `src/ghent_water/frontend/app.py`, `src/ghent_water/frontend/components/*.py`

**src/ghent_water/models/:**
- Purpose: Water system simulation models (microservices)
- Contains: Model stubs, base model class, model runner
- Key files: `src/ghent_water/models/base.py`, `src/ghent_water/models/stubs/*.py`, `src/ghent_water/models/runners/model_runner.py`

**src/ghent_water/orchestrator/:**
- Purpose: Central API server and orchestration service
- Contains: FastAPI app, routers, schemas, business logic services
- Key files: `src/ghent_water/orchestrator/main.py`, `src/ghent_water/orchestrator/routers/*.py`, `src/ghent_water/orchestrator/services/*.py`

**scripts/:**
- Purpose: Utility scripts for running services
- Contains: Orchestrator launcher, batch runner
- Key files: `scripts/run_orchestrator.py`, `scripts/run_all.py`

## Key File Locations

**Entry Points:**
- `src/ghent_water/orchestrator/main.py`: FastAPI orchestrator application
- `src/ghent_water/frontend/app.py`: Streamlit frontend application
- `src/ghent_water/models/runners/model_runner.py`: CLI for running individual model microservices

**Configuration:**
- `pyproject.toml`: Python package dependencies and project configuration
- `.env`: Environment variables (API keys, service URLs)
- `src/ghent_water/orchestrator/config.py`: Orchestrator settings using Pydantic
- `src/ghent_water/frontend/config.py`: Frontend configuration

**Core Logic:**
- `src/ghent_water/orchestrator/services/sparql_engine.py`: SPARQL query execution
- `src/ghent_water/orchestrator/services/ontology_store.py`: RDF graph management
- `src/ghent_water/orchestrator/services/llm_sparql.py`: NL to SPARQL translation
- `src/ghent_water/orchestrator/services/model_registry.py`: Model and job tracking
- `src/ghent_water/models/base.py`: Abstract base class for all models

**API Layer:**
- `src/ghent_water/orchestrator/routers/`: API endpoint definitions
- `src/ghent_water/orchestrator/schemas/models.py`: Pydantic models for request/response
- `src/ghent_water/frontend/services/api_client.py`: Frontend HTTP client

**Testing:**
- `TESTING_PLAN.md`: Testing strategy document

## Naming Conventions

**Files:**
- Python modules: `snake_case.py` (e.g., `sparql_engine.py`, `ontology_store.py`)
- Classes: `PascalCase` (e.g., `SparqlEngine`, `BaseWaterModel`, `ModelRegistry`)
- Functions/methods: `snake_case` (e.g., `execute_query`, `load_ontology`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `ENTITY_PORTS`, `MODEL_PORTS`)
- RDF/Turtle files: `lowercase_with_underscores.ttl` (e.g., `dwp1.ttl`, `weather_sensors.ttl`)

**Directories:**
- Python packages: `lowercase_with_underscores` (e.g., `ghent_water`, `orchestrator`)
- Subdirectories: `lowercase_with_underscores` (e.g., `components`, `services`, `routers`)

## Where to Add New Code

**New API Endpoint:**
- Router: `src/ghent_water/orchestrator/routers/{domain}.py`
- Schema: `src/ghent_water/orchestrator/schemas/models.py`
- Service: `src/ghent_water/orchestrator/services/{domain}_service.py`
- Register: Add `app.include_router(router)` in `src/ghent_water/orchestrator/main.py`

**New Model (Water System Entity):**
- Stub: `src/ghent_water/models/stubs/{entity}.py`
- Base: Extend `BaseWaterModel` from `src/ghent_water/models/base.py`
- Register: Add to `MODEL_REGISTRY` in `src/ghent_water/models/runners/model_runner.py`
- Instance data: `data/instances/{entity}.ttl`

**New Frontend Component:**
- Component: `src/ghent_water/frontend/components/{component_name}.py`
- Import: Add to `src/ghent_water/frontend/app.py`
- Use: Render in `main()` function with appropriate layout

**New Ontology Concept:**
- Definition: Add to `data/ontology/` or appropriate module file
- Instance: Add to `data/instances/{entity}.ttl`
- Prefix: Register in `src/ghent_water/orchestrator/services/namespace_manager.py`

**New Service:**
- Service: `src/ghent_water/orchestrator/services/{service}.py`
- Export: Add to `src/ghent_water/orchestrator/services/__init__.py`
- Use: Import and instantiate in routers that need it

## Special Directories

**.venv/:**
- Purpose: Python virtual environment
- Generated: Yes
- Committed: No

**src/ghent_water/__pycache__/ and all subdirectories:**
- Purpose: Python bytecode cache
- Generated: Yes
- Committed: No

**data/:**
- Purpose: Knowledge graph data (RDF/Turtle)
- Generated: No
- Committed: Yes

**src/ghent_water/frontend/static/:**
- Purpose: Static assets (CSS, JS, images)
- Generated: No
- Committed: Yes
- Contains: `styles.css`

---

*Structure analysis: 2026-01-19*
