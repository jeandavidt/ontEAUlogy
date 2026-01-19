# External Integrations

**Analysis Date:** 2026-01-19

## APIs & External Services

**LLM Services:**
- OpenRouter - Multi-provider LLM API gateway
  - Purpose: Natural language to SPARQL translation
  - SDK/Client: pydantic-ai with OpenAI-compatible interface
  - Auth env var: `OPENROUTER_API_KEY`
  - Implementation: `src/ghent_water/orchestrator/services/llm_sparql.py`

- LM Studio - Local LLM inference server (optional)
  - Purpose: Local LLM alternative to cloud services
  - Connection: HTTP endpoint configured via `LLM_BASE_URL`
  - No API key required (local)
  - Auto-detection: Tries LM Studio first, falls back to OpenRouter

- Anthropic Claude (via OpenRouter) - LLM provider option
  - Purpose: Natural language processing
  - Package: anthropic>=0.40 (optional dependency)

- OpenAI GPT (via OpenRouter) - LLM provider option
  - Purpose: Natural language processing
  - Package: openai>=1.0 (optional dependency)

## Data Storage

**Databases:**
- RDFLib In-Memory Graph - Primary data store
  - Connection: Loaded from `.ttl` (Turtle) files at startup
  - Client: rdflib Graph
  - Data files: `data/system.ttl`, `data/instances/*.ttl`, `data/instances/sensors/*.ttl`
  - Query: SPARQL via `rdflib.query()`
  - Implementation: `src/ghent_water/orchestrator/services/ontology_store.py`

**Optional SPARQL Endpoint:**
- External SPARQL endpoint (if configured)
  - Connection: Via `sparql_endpoint` env var
  - Currently not used (None by default)

**File Storage:**
- Local filesystem - Ontology and instance data
  - Data directory: `data/`
  - Instance files: `data/instances/*.ttl`
  - Sensor data: `data/instances/sensors/*.ttl`
  - System file: `data/system.ttl` (master import file)

**Caching:**
- None - All data loaded fresh from files at startup

## Authentication & Identity

**Auth Provider:**
- Custom - No external authentication
  - Implementation: None (CORS enabled for all origins)
  - No user accounts or sessions
  - Access control: Open to all (localhost development)

## Monitoring & Observability

**Error Tracking:**
- None - No external error tracking service

**Logs:**
- Python logging module
  - Log file: `orchestrator.log` in project root
  - Level: INFO (configurable via `log_level` env var)
  - Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
  - Outputs: File + StreamHandler

**Health Checks:**
- Internal health endpoint
  - Path: `/health`
  - Checks: ontology loaded, sparql_engine ready
  - Returns: JSON with status, version, components

## CI/CD & Deployment

**Hosting:**
- Local development - No cloud hosting configured
  - Orchestrator: localhost:8080
  - Streamlit frontend: localhost:8501
  - Model services: localhost:8001-8012

**CI Pipeline:**
- None - No CI/CD configuration detected

## Environment Configuration

**Required env vars:**
- `OPENROUTER_API_KEY` - API key for OpenRouter LLM service
  - Required if using OpenRouter provider

**Optional env vars:**
- `LLM_PROVIDER` - "auto", "openrouter", or "lmstudio" (default: "auto")
- `LLM_MODEL` - Model identifier (e.g., "mistralai/devstral-2512:free")
- `LLM_BASE_URL` - Custom LLM endpoint (for LM Studio)
- `LLM_MAX_RETRIES` - Maximum retry attempts for invalid SPARQL (default: 3)
- `SPARQL_ENDPOINT` - External SPARQL endpoint URL (default: None)
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8080)
- `DEBUG` - Debug mode (default: False)
- `LOG_LEVEL` - Logging level (default: INFO)

**Secrets location:**
- `.env` file in project root
- Not committed to git (in .gitignore)

## Webhooks & Callbacks

**Incoming:**
- None - No webhook endpoints defined

**Outgoing:**
- None - No external webhooks called by the system

## Internal Service Communication

**Model Discovery (Service-to-Service):**
- Model services register with orchestrator at startup
  - Orchestrator: HTTP GET requests to `localhost:8001-8012/describe`
  - Response: JSON-LD self-description from models
  - Implementation: `src/ghent_water/orchestrator/main.py::discover_and_register_models()`

**Model Service Ports:**
| Port | Model | Description |
|------|-------|-------------|
| 8001 | dwp1 | Drinking Water Plant 1 |
| 8002 | dwp2 | Drinking Water Plant 2 |
| 8003 | wwtp1 | Wastewater Treatment Plant 1 |
| 8004 | wwtp2 | Wastewater Treatment Plant 2 |
| 8005 | texfin | Textile Industry |
| 8006 | foodpro | Food Processing |
| 8007 | chiptech | Electronics Manufacturing |
| 8008 | pharmagen | Pharmaceutical |
| 8009 | brewco | Brewery |
| 8010 | lieve_river | Lieve River |
| 8011 | dampoort | Residential District (upstream) |
| 8012 | muide | Residential District (downstream) |

**Model Service Endpoints:**
- `GET /describe` - JSON-LD self-description
- `GET /describe/turtle` - Turtle (TTL) self-description
- `POST /simulate` - Run simulation with inputs
- `GET /state` - Current model state
- `GET /health` - Health check

**Frontend to Orchestrator:**
- HTTP client: `src/ghent_water/frontend/services/api_client.py`
- Base URL: `http://localhost:8000` (configurable)
- Key endpoints:
  - `GET /api/v1/models/` - List available models
  - `GET /api/v1/models/{id}/describe` - Get model description
  - `POST /api/v1/query/sparql` - Execute SPARQL query
  - `POST /api/v1/query/natural` - Natural language query
  - `POST /api/v1/simulation/run` - Run simulation
  - `GET /api/v1/simulation/jobs/{id}` - Get job status
  - `GET /ws/sensor-data` - WebSocket for real-time sensor data

**Real-time Data:**
- WebSocket server (orchestrator)
  - Path: `/ws/sensor-data`
  - Client: `src/ghent_water/frontend/services/websocket_client.py`
  - Protocol: JSON messages

---

*Integration audit: 2026-01-19*
