# Architecture

**Analysis Date:** 2026-01-19

## Pattern Overview

**Overall:** Microservices Orchestrator with Knowledge Graph Integration

**Key Characteristics:**
- Service-oriented architecture with model microservices
- Central orchestrator for coordination and ontology management
- Knowledge graph-driven data model (RDF/SPARQL)
- LLM-powered natural language interface
- Dynamic model discovery and registration
- Websocket-based real-time updates

## Layers

**Orchestrator Layer:**
- Purpose: Central coordination service for ontology queries, model orchestration, and API gateway
- Location: `src/ghent_water/orchestrator/`
- Contains: FastAPI application, routers, schemas, business services
- Depends on: RDF ontology, model microservices, LLM APIs
- Used by: Frontend, model microservices

**Model Layer:**
- Purpose: Individual water system simulation models running as autonomous microservices
- Location: `src/ghent_water/models/`
- Contains: Model stub implementations (DWP, WWTP, Industry, Residential, River), base model class
- Depends on: `BaseWaterModel`, rdflib, FastAPI
- Used by: Orchestrator (via HTTP endpoints)

**Frontend Layer:**
- Purpose: Interactive web interface for visualization and query execution
- Location: `src/ghent_water/frontend/`
- Contains: Streamlit application, UI components, API client
- Depends on: Orchestrator API, Folium maps, Streamlit
- Used by: End users

**Data Layer:**
- Purpose: Knowledge graph containing water system ontology and case study instances
- Location: `data/`
- Contains: Turtle files for ontology, entities, sensors
- Depends on: waterFRAME ontology standard
- Used by: Orchestrator, Frontend

## Data Flow

**Ontology Query Flow:**

1. Frontend submits SPARQL query via `OrchestratorClient`
2. Request hits `/api/v1/query/sparql` endpoint
3. `sparql_engine.execute_query()` processes query against in-memory RDF graph
4. Results formatted as JSON/CSV/JSON-LD and returned to frontend
5. Frontend displays results in query panel

**Natural Language Query Flow:**

1. User submits natural language question in frontend
2. Request hits `/api/v1/query/natural` endpoint
3. `LLM_SPARQL_Translator.translate()` generates SPARQL from question
4. Generated SPARQL executed via `sparql_engine`
5. Results returned with original question, generated SPARQL, and query results
6. Frontend shows translation and results

**Model Discovery Flow:**

1. Orchestrator startup calls `discover_and_register_models()`
2. Iterates through known model endpoints (ports 8001-8012)
3. For each endpoint, calls GET `/describe` to fetch model self-description
4. Model description (JSON-LD) parsed to extract capabilities and entities
5. `ModelRegistry.register_model()` stores model metadata
6. Models available for simulation via `/simulation/models/{model_id}/run`

**Simulation Execution Flow:**

1. User triggers simulation from frontend for an entity
2. Frontend calls `/simulation/models/{model_id}/run` with parameters
3. Orchestrator creates job in `ModelRegistry`, returns job_id
4. Background task (`execute_simulation()`) calls model's `/simulate` endpoint
5. Model executes simulation with given parameters
6. Results stored in job, status updated to "completed"
7. Frontend polls job status via WebSocket or `/simulation/jobs/{job_id}`
8. Display results when job completes

**State Management:**
- Model registry: In-memory dict in `ModelRegistry` instance
- Ontology graph: In-memory rdflib Graph in `OntologyStore`
- Jobs: In-memory dict in `ModelRegistry`
- Frontend state: Streamlit `st.session_state`
- WebSocket connections: Real-time updates for simulation status

## Key Abstractions

**BaseWaterModel:**
- Purpose: Abstract base class defining interface for all water system models
- Examples: `src/ghent_water/models/stubs/dwp.py`, `src/ghent_water/models/stubs/wwtp.py`
- Pattern: Template method pattern with abstract `describe()` and `simulate()` methods
- Common capabilities: Self-description (JSON-LD/Turtle), health checks, state management

**ModelRegistry:**
- Purpose: Central registry for tracking available models and simulation jobs
- Location: `src/ghent_water/orchestrator/services/model_registry.py`
- Pattern: Singleton service with global `registry` instance
- Responsibilities: Model registration/unregistration, job lifecycle management

**OntologyStore:**
- Purpose: Manages RDF knowledge graph loading and querying
- Location: `src/ghent_water/orchestrator/services/ontology_store.py`
- Pattern: Singleton service with global `ontology_store` instance
- Responsibilities: Load Turtle files, merge graphs, execute SPARQL queries

**SparqlEngine:**
- Purpose: Executes SPARQL queries against RDF graphs
- Location: `src/ghent_water/orchestrator/services/sparql_engine.py`
- Pattern: Engine wrapper around rdflib query capabilities
- Responsibilities: Query execution, result formatting (JSON/CSV/JSON-LD)

**LLM_SPARQL_Translator:**
- Purpose: Translates natural language questions to SPARQL queries
- Location: `src/ghent_water/orchestrator/services/llm_sparql.py`
- Pattern: PydanticAI agent with type-safe responses
- Responsibilities: NL translation, query validation, retry logic

## Entry Points

**Orchestrator (FastAPI):**
- Location: `src/ghent_water/orchestrator/main.py`
- Triggers: `python -m uvicorn ghent_water.orchestrator.main:app` or `scripts/run_orchestrator.py`
- Responsibilities: API server, router registration, model discovery, ontology loading, WebSocket handling

**Frontend (Streamlit):**
- Location: `src/ghent_water/frontend/app.py`
- Triggers: `streamlit run src/ghent_water/frontend/app.py`
- Responsibilities: Web UI, map visualization, query interface, simulation status display

**Model Runner (CLI):**
- Location: `src/ghent_water/models/runners/model_runner.py`
- Triggers: `python -m ghent_water.models.runners.model_runner --model dwp1 --port 8001`
- Responsibilities: Run individual model microservices as FastAPI servers

## Error Handling

**Strategy:** Layered error handling with HTTP status codes and logging

**Patterns:**
- API routers raise `HTTPException` with appropriate status codes (400, 404, 500, 503)
- Services log errors with traceback before raising
- Frontend displays error messages in UI with expandable details
- Model services return error responses with descriptive messages
- Simulation jobs track errors in job state for later retrieval

## Cross-Cutting Concerns

**Logging:** Python standard logging module configured in `orchestrator/main.py` to file and console

**Validation:** Pydantic models for request/response validation in `orchestrator/schemas/models.py`

**Authentication:** Not implemented (open API, CORS enabled for all origins)

**Configuration:** Pydantic Settings with environment variable support in `orchestrator/config.py`

---

*Architecture analysis: 2026-01-19*
