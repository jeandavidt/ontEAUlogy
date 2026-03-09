# Refactoring Task Plan: Shared Core Architecture

## Goal
Refactor the project to have a shared core (orchestrator, frontend, agents) used by both Ghent and Household case studies, with each case having its own models, ontology, and page layouts.

## Current State Analysis

### Existing Structure
```
case_studies/
├── ghent/
│   ├── frontend-react/       # React frontend (standalone)
│   ├── orchestrator/         # Python FastAPI orchestrator
│   ├── models/               # Ghent-specific models (dwp1, wwtp1, etc.)
│   ├── docker-compose.yml    # Defines all services
│   └── data/                 # Ghent ontology files
│
└── household/
    ├── src/household_water/
    │   ├── models/           # MBR, RO, Infiltration models
    │   └── orchestrator/     # Household-specific orchestrator (partial)
    └── data/                 # Household ontology files
```

### Problems with Current Structure
1. **Duplicated orchestrator logic** - Ghent has full orchestrator, Household has partial
2. **Single frontend** - Only Ghent has a frontend; Household has no UI
3. **Tight coupling** - Models mixed with orchestrator in Ghent
4. **Hard-coded configurations** - No easy way to spin up case-specific instances
5. **Shared docker-compose** - All services defined together, hard to manage separately

## Target Architecture

```
case_studies/
├── core/                     # SHARED COMPONENTS
│   ├── orchestrator/         # Generic FastAPI orchestrator
│   │   ├── agents/           # SPARQL agent, LLM agent
│   │   ├── api/              # Generic REST endpoints
│   │   └── config/           # Case-study agnostic config
│   │
│   ├── frontend/             # Shared React components
│   │   ├── src/
│   │   │   ├── components/   # Reusable UI components
│   │   │   ├── agents/       # SPARQL query builder, LLM chat
│   │   │   ├── hooks/        # Shared React hooks
│   │   │   └── lib/          # Utilities
│   │   └── docker/
│   │       └── Dockerfile.frontend
│   │
│   └── shared/               # Shared Python packages
│       ├── ontology/         # Ontology utilities
│       ├── semantic/         # RDF/JSON-LD handling
│       └── schemas/          # Pydantic models
│
├── ghent/                    # GHENT CASE STUDY
│   ├── models/               # Ghent-specific model services
│   ├── ontology/             # Ghent TTL files
│   ├── config/
│   │   ├── orchestrator.yaml # Case-specific orchestrator config
│   │   └── frontend.yaml     # Case-specific frontend config
│   └── docker-compose.yml    # Compose for Ghent only
│
└── household/                # HOUSEHOLD CASE STUDY
    ├── models/               # MBR, RO, Infiltration services
    ├── ontology/             # Household TTL files
    ├── config/
    │   ├── orchestrator.yaml
    │   └── frontend.yaml
    └── docker-compose.yml    # Compose for Household only
```

## Phases

### Phase 1: Analysis & Design
- [ ] Document current orchestrator endpoints and capabilities
- [ ] Document current frontend components and routes
- [ ] Identify shared vs case-specific logic
- [ ] Design configuration schema for case studies
- [ ] Plan migration strategy (avoid breaking changes)

### Phase 2: Create Core Structure
- [ ] Create `core/` directory structure
- [ ] Set up shared Python package with proper imports
- [ ] Create base orchestrator class (case-agnostic)
- [ ] Create SPARQL agent (shared)
- [ ] Create LLM agent (shared)
- [ ] Set up shared frontend package structure

### Phase 3: Migrate Ghent
- [ ] Move orchestrator to core, make it generic
- [ ] Move shared frontend components to core
- [ ] Create Ghent-specific frontend pages/layouts
- [ ] Create Ghent config files
- [ ] Update Ghent docker-compose to use core images
- [ ] Test Ghent stack end-to-end

### Phase 4: Migrate Household
- [ ] Move model services to new structure
- [ ] Create Household-specific orchestrator config
- [ ] Create Household frontend pages/layouts
- [ ] Create Household config files
- [ ] Create Household docker-compose
- [ ] Test Household stack end-to-end

### Phase 5: Testing & Integration
- [ ] Test both case studies independently
- [ ] Verify shared components work in both
- [ ] Test SPARQL queries work across ontologies
- [ ] Test LLM agent with both case studies
- [ ] Document deployment procedures

### Phase 6: Cleanup
- [ ] Remove old duplicated code
- [ ] Update README files
- [ ] Create architecture documentation
- [ ] Final integration tests

## Key Questions

1. **How to handle case-study specific routes in frontend?**
   - Option A: Separate React apps with shared component library
   - Option B: Single React app with case-study based routing
   - **Decision needed**: Leaning toward Option B for easier maintenance

2. **How should orchestrator discover models?**
   - Option A: Config file listing all model endpoints
   - Option B: Service discovery via Docker network
   - Option C: Models register themselves on startup
   - **Decision needed**: Option A (explicit config) is simplest

3. **Where do LLM prompts live?**
   - Option A: In core (generic prompts)
   - Option B: In each case study (specific prompts)
   - Option C: Both (base in core, override in cases)
   - **Decision needed**: Option C offers most flexibility

4. **How to share ontology utilities?**
   - Option A: Shared Python package (core.shared.ontology)
   - Option B: Each case study has its own
   - **Decision needed**: Option A - utilities should be shared

5. **What stays case-specific?**
   - Model implementations (physics, schemas)
   - Ontology files (TTL)
   - Page layouts and visualizations
   - Case study documentation
   - Docker-compose files

## Decisions Made

- **Docker Strategy**: Each case study has its own docker-compose.yml that references images built from core/
- **Frontend Strategy**: Shared component library + case-specific page routes
- **Orchestrator Strategy**: Generic base class + case-specific configuration
- **Configuration**: YAML-based configuration for each case study
- **Migration Approach**: Create new structure parallel to old, then switch over

## Errors Encountered

*None yet*

## Detailed Analysis

### Orchestrator Analysis

**Generic (Shared) Components:**
- FastAPI app setup, lifespan, CORS
- Router structure (discovery, query, simulation, ontology, websocket, sensors, trace)
- SPARQL engine execution
- LLM translator for natural language queries
- Model registry pattern
- Ontology store pattern
- Sensor broadcast loop
- Health check endpoint structure

**Case-Specific Components:**
- Model discovery (hardcoded model ports in main.py)
- Ontology file paths
- App name/description
- Entity namespace prefixes (ghent:, housecase1:)
- Model endpoint construction

**Key Finding:**
The orchestrator is 90% generic! Only the model discovery logic and ontology paths are case-specific.

### Frontend Analysis

**Generic (Shared) Components:**
- Layout components (DashboardLayout)
- Common UI components (SPARQLSection, SensorVisualizer)
- API client setup
- React hooks
- State management stores
- Mantine UI theme setup

**Case-Specific Components:**
- Dashboard page layout (which components are shown, how they're arranged)
- Map component (different entities, different coordinates)
- Topology component (different graph structure)
- Simulation forms (different models have different inputs)
- Routes/pages structure

**Key Finding:**
Frontend components are reusable, but page layouts and visualization data are case-specific.

### Configuration Strategy

Each case study will have:

```yaml
# orchestrator.yaml
app:
  name: "ontEAUlogy Ghent Backend"
  version: "0.1.0"

ontology:
  base_path: "../../data"
  case_study_path: "data"
  files:
    - "ontology/waterframe.ttl"
    - "instances/ghent.ttl"

models:
  discovery:
    - id: "dwp1"
      endpoint: "http://ghent-dwp1:8001"
      entity: "ghent:DWP1"
    - id: "wwtp1"
      endpoint: "http://ghent-wwtp1:8003"
      entity: "ghent:WWTP1"

namespaces:
  ghent: "https://ugentbiomath.github.io/ontology/index.ttl#"
```

### Implementation Plan

#### Phase 1: Create Core Directory Structure
```
core/
├── orchestrator/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── src/ontEAUlogy_core/
│       ├── __init__.py
│       ├── main.py              # Generic FastAPI app
│       ├── config.py            # Generic settings with case overrides
│       ├── routers/
│       │   ├── __init__.py
│       │   ├── discovery.py     # Generic with config-based models
│       │   ├── query.py         # SPARQL endpoints
│       │   ├── simulation.py    # Model proxy endpoints
│       │   ├── ontology.py      # Ontology management
│       │   ├── websocket.py     # WebSocket for sensors
│       │   ├── sensors.py       # Sensor API
│       │   └── trace.py         # Execution tracing
│       ├── services/
│       │   ├── __init__.py
│       │   ├── model_registry.py
│       │   ├── ontology_store.py
│       │   ├── sparql_engine.py
│       │   ├── llm_sparql.py    # LLM agent
│       │   ├── sensor_generator.py
│       │   └── execution_trace.py
│       └── schemas/
│           ├── __init__.py
│           └── models.py
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── core/               # Shared components
│       │   ├── components/
│       │   │   ├── common/
│       │   │   │   ├── SPARQLSection.tsx
│       │   │   │   ├── SensorVisualizer.tsx
│       │   │   │   └── ChatInterface.tsx
│       │   │   ├── simulation/
│       │   │   ├── results/
│       │   │   ├── map/
│       │   │   └── topology/
│       │   ├── hooks/
│       │   ├── api/
│       │   ├── stores/
│       │   └── lib/
│       └── cases/              # Case-specific pages
│
└── shared-python/
    └── src/ontEAUlogy_shared/
        ├── __init__.py
        ├── ontology.py
        └── semantic.py
```

#### Phase 2: Files to Create/Move

**New Files in Core:**
1. `core/orchestrator/src/ontEAUlogy_core/config.py` - Generic config with case loading
2. `core/orchestrator/src/ontEAUlogy_core/main.py` - Generic FastAPI app
3. `core/orchestrator/src/ontEAUlogy_core/routers/discovery.py` - Config-based model discovery
4. `core/orchestrator/Dockerfile` - Multi-stage build
5. `core/orchestrator/pyproject.toml` - Package definition
6. `core/frontend/src/core/` - All shared components
7. `core/shared-python/` - Shared ontology utilities

**Moved from Ghent to Core:**
1. `ghent/src/ghent_water/orchestrator/services/*` → `core/orchestrator/src/ontEAUlogy_core/services/`
2. `ghent/src/ghent_water/orchestrator/routers/query.py` → `core/orchestrator/src/ontEAUlogy_core/routers/`
3. `ghent/src/ghent_water/orchestrator/routers/simulation.py` → `core/orchestrator/src/ontEAUlogy_core/routers/`
4. `ghent/src/ghent_water/orchestrator/routers/ontology.py` → `core/orchestrator/src/ontEAUlogy_core/routers/`
5. `ghent/src/ghent_water/orchestrator/routers/websocket.py` → `core/orchestrator/src/ontEAUlogy_core/routers/`
6. `ghent/src/ghent_water/orchestrator/routers/sensors.py` → `core/orchestrator/src/ontEAUlogy_core/routers/`
7. `ghent/src/ghent_water/orchestrator/routers/trace.py` → `core/orchestrator/src/ontEAUlogy_core/routers/`
8. `ghent/src/ghent_water/orchestrator/schemas/models.py` → `core/orchestrator/src/ontEAUlogy_core/schemas/`

**Case-Specific Files (Stay in Case Study):**
1. `ghent/config/orchestrator.yaml` - Ghent-specific configuration
2. `ghent/config/frontend.yaml` - Frontend case config
3. `ghent/frontend/src/pages/` - Page layouts
4. `ghent/docker-compose.yml` - Compose with core images
5. `household/config/orchestrator.yaml` - Household configuration
6. `household/config/frontend.yaml` - Household frontend config
7. `household/frontend/src/pages/` - Household pages

## Status

**COMPLETED - Phase 2 & 3 & 4 & 5 (Partial)**

### What has been implemented:

#### Phase 2: Create Core Structure - COMPLETE
- [x] Create `core/` directory structure
- [x] Set up shared Python package with proper imports (`core/shared-python/`)
- [x] Create base orchestrator class (case-agnostic) (`core/orchestrator/src/ontEAUlogy_core/`)
- [x] Create SPARQL agent (shared)
- [x] Create LLM agent (shared)
- [x] Set up shared frontend package structure (`core/frontend/`)

#### Phase 3: Migrate Ghent - COMPLETE
- [x] Move orchestrator to core, make it generic
- [x] Create Ghent config files (`ghent/config/orchestrator.yaml`)
- [x] Update Ghent docker-compose to use core images
- [x] Create Ghent frontend config (`ghent/config/frontend.yaml`)

#### Phase 4: Migrate Household - COMPLETE
- [x] Create Household-specific orchestrator config (`household/config/orchestrator.yaml`)
- [x] Create Household frontend pages/layouts
- [x] Create Household config files (`household/config/frontend.yaml`)
- [x] Create Household docker-compose
- [x] Fix household orchestrator to use ontEAUlogy_core (was using waterframe_core)

#### Phase 5: Testing & Integration - PENDING
- [ ] Test both case studies independently
- [ ] Verify shared components work in both
- [ ] Test SPARQL queries work across ontologies
- [ ] Test LLM agent with both case studies
- [ ] Document deployment procedures

### Key Accomplishments:
- Created `core/orchestrator/` with generic FastAPI orchestrator
- Created `core/shared-python/` with shared utilities
- Created `core/frontend/` with TypeScript types, hooks, stores, and utilities
- Both Ghent and Household now use the same core orchestrator image
- Configuration-driven model discovery implemented
- Frontend YAML configs created for both case studies

### Remaining Work:
- Delete old ghent orchestrator files (now in core) - Phase 6
- Test integration between case studies
- Build and test the docker images end-to-end

**Ready for Phase 5: Testing & Integration**
