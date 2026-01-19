# Technology Stack

**Analysis Date:** 2026-01-19

## Languages

**Primary:**
- Python 3.11+ - All application code (orchestrator, models, frontend)

**Secondary:**
- Turtle/TTL (RDF) - Ontology and instance data files in `data/`

## Runtime

**Environment:**
- Python 3.11+ (specified in `pyproject.toml`)

**Package Manager:**
- uv (lockfile: `uv.lock` present)
- pip (via `pip install -e .` for development)

**Virtual Environment:**
- `.venv/` (Python virtual environment)

## Frameworks

**Core:**
- FastAPI 0.115+ - REST API backend for orchestrator
  - Location: `src/ghent_water/orchestrator/`
  - Serves: `/api/v1/` endpoints for queries, simulation, discovery
- Streamlit 1.53.0+ - Interactive web frontend
  - Location: `src/ghent_water/frontend/`
  - Serves: Dashboard UI for water system exploration

**Web Server:**
- Uvicorn 0.34+ - ASGI server for FastAPI
  - Runs orchestrator on port 8080
  - Used in `scripts/run_orchestrator.py`

**Testing:**
- pytest 8.0+ - Test framework (optional dependency)
- pytest-asyncio 0.24+ - Async test support

**Build/Dev:**
- Hatchling - Build backend (specified in `pyproject.toml`)

## Key Dependencies

**Critical:**
- rdflib 7.0+ - RDF graph library for ontology management
  - Loads Turtle/TTL files from `data/ontology/` and `data/instances/`
  - Executes SPARQL queries via in-memory graph
  - Used in: `src/ghent_water/orchestrator/services/ontology_store.py`

**Infrastructure:**
- httpx 0.28+ - Async HTTP client
  - Model discovery: checks localhost:8001-8012 for model services
  - API client for orchestrator communication
  - Used in: `src/ghent_water/orchestrator/main.py`, `src/ghent_water/frontend/services/api_client.py`

- pydantic 2.10+ - Data validation and settings
  - Settings management via `pydantic-settings`
  - Pydantic AI for LLM integration
  - Used throughout: `src/ghent_water/orchestrator/config.py`

- pydantic-ai 0.0+ - LLM agent framework
  - Natural language to SPARQL translation
  - Type-safe LLM interactions with OpenAI-compatible APIs
  - Used in: `src/ghent_water/orchestrator/services/llm_sparql.py`

**Frontend:**
- streamlit 1.53.0+ - Web UI framework
  - Main app: `src/ghent_water/frontend/app.py`
  - Components: `src/ghent_water/frontend/components/`

- folium 0.15+ + streamlit-folium 0.26+ - Interactive maps
  - Map visualization of water system entities
  - Used in: `src/ghent_water/frontend/components/map_view.py`

- websockets - WebSocket client
  - Real-time sensor data streaming
  - Used in: `src/ghent_water/frontend/services/websocket_client.py`

**Utilities:**
- python-dotenv 1.0+ - Environment variable loading from `.env`
- numpy 1.24+ - Numerical operations (likely for simulation data)

**Optional LLM Providers:**
- anthropic 0.40+ - Anthropic Claude API (via pydantic-ai)
- openai 1.0+ - OpenAI API (via pydantic-ai)

## Configuration

**Environment:**
- `.env` file for environment variables
  - `OPENROUTER_API_KEY` - API key for LLM service
  - `LLM_PROVIDER` - "auto", "openrouter", or "lmstudio"
  - `LLM_MODEL` - Model identifier (e.g., "mistralai/devstral-2512:free")
  - `LLM_BASE_URL` - Custom endpoint for local LM Studio
- Settings managed via `src/ghent_water/orchestrator/config.py`

**Build:**
- `pyproject.toml` - Project metadata and dependencies
- `uv.lock` - Lock file for uv package manager
- Build system: hatchling

## Platform Requirements

**Development:**
- Python 3.11+
- uv (recommended) or pip
- Optional: LM Studio for local LLM inference

**Production:**
- Python 3.11+ environment
- 12 model service ports: 8001-8012
- Orchestrator port: 8080
- Streamlit port: 8501

---

*Stack analysis: 2026-01-19*
