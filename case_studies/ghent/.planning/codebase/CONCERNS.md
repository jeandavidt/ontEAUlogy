# Codebase Concerns

**Analysis Date:** 2026-01-19

## Tech Debt

**Model Simulations Are Stubs:**
- Issue: All model simulations in `src/ghent_water/models/stubs/` are stub implementations using configurable removal rates with random variance, not actual physics or water treatment models.
- Files: `src/ghent_water/models/stubs/dwp.py`, `src/ghent_water/models/stubs/wwtp.py`, `src/ghent_water/models/stubs/industry.py`, `src/ghent_water/models/stubs/river.py`, `src/ghent_water/models/stubs/residential.py`
- Impact: Simulation results are not scientifically accurate or based on real treatment physics. System is only suitable for demonstration, not production water system modeling.
- Fix approach: Replace stubs with actual physics-based models or integrate with existing simulation frameworks (SWMM, EPANET, BioWin, etc.).

**Hardcoded Configuration:**
- Issue: `localhost` hardcoded in 20+ locations throughout the codebase. Port numbers hardcoded in model stubs and map components.
- Files: `src/ghent_water/frontend/components/map_view.py:761`, `src/ghent_water/frontend/services/websocket_client.py:17`, `src/ghent_water/orchestrator/routers/simulation.py:62`, `src/ghent_water/models/base.py:75`
- Impact: System cannot be deployed to different environments (dev, staging, production) without code changes. Testing with non-localhost endpoints requires extensive code modifications.
- Fix approach: Extract all URLs, ports, and endpoints to environment variables or configuration files. Use service discovery or configuration injection.

**Large Files (Code Complexity):**
- Issue: `map_view.py` is 881 lines, `llm_sparql.py` is 665 lines. These files handle multiple responsibilities.
- Files: `src/ghent_water/frontend/components/map_view.py`, `src/ghent_water/orchestrator/services/llm_sparql.py`
- Impact: Difficult to maintain, test, and understand. Changes risk introducing bugs due to interdependent code.
- Fix approach: Split into smaller modules: map rendering, data fetching, entity management, connection logic separate.

**Global State Management:**
- Issue: Global caches and singleton instances used across modules.
- Files: `src/ghent_water/frontend/components/map_view.py:405-406`, `src/ghent_water/orchestrator/services/sensor_generator.py:315`, `src/ghent_water/orchestrator/services/llm_sparql.py:647`
- Impact: Hard to test, creates coupling between components, can cause state corruption in concurrent scenarios. Makes dependency injection impossible.
- Fix approach: Use dependency injection pattern, pass instances as parameters, or use proper DI frameworks (FastAPI's Depends, dependency-injector).

## Known Bugs

**None identified** - No explicit bug markers (TODO, FIXME, BUG) found in codebase.

## Security Considerations

**Exposed API Keys in Version Control:**
- Risk: `.env` file contains real API key (`OPENROUTER_API_KEY="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"`).
- Files: `.env:2`
- Current mitigation: None - No `.gitignore` file present. `.env` is committed to repository.
- Recommendations: 1) Add `.gitignore` with `.env` pattern, 2) Revoke exposed API key immediately, 3) Rotate to new key, 4) Use environment variable management (Vault, AWS Secrets Manager, 1Password CLI), 5) Add pre-commit hook to prevent committing secrets.

**No Authentication/Authorization:**
- Risk: All API endpoints are publicly accessible. No authentication on orchestrator or model services.
- Files: `src/ghent_water/orchestrator/main.py`, `src/ghent_water/models/stubs/*.py`
- Current mitigation: None
- Recommendations: Add FastAPI security dependencies (OAuth2, JWT, API keys) to protect endpoints, especially simulation and query endpoints that could be resource-intensive.

**Hardcoded URLs in Code:**
- Risk: `localhost:8080`, `http://localhost:8000` etc. exposed in client code.
- Files: Throughout `src/ghent_water/frontend/`, `src/ghent_water/orchestrator/`
- Current mitigation: None
- Recommendations: All URLs should be configurable via environment variables.

## Performance Bottlenecks

**In-Memory Job Storage:**
- Problem: `ModelRegistry` stores jobs in memory dictionary with no persistence or size limits.
- Files: `src/ghent_water/orchestrator/services/model_registry.py:14-15`
- Cause: Jobs accumulate indefinitely in `_jobs` dict, consuming memory.
- Improvement path: Add TTL/expiration for completed jobs, persist jobs to database, implement pagination for job listing.

**No HTTP Connection Pooling:**
- Problem: New HTTP client created for each request in `OrchestratorClient._get_client()` if previous is closed.
- Files: `src/ghent_water/frontend/services/api_client.py:19-23`
- Cause: Connection overhead on every API call, no reuse of connections.
- Improvement path: Use single persistent httpx.AsyncClient with proper connection limits, or implement connection pooling with httpx limits.

**Unbounded Global Caches:**
- Problem: Frontend caches entities, sensors, connections with no size limits or invalidation strategy.
- Files: `src/ghent_water/frontend/components/map_view.py:44-48`
- Cause: Caches grow indefinitely as ontology changes or app runs long-term.
- Improvement path: Add cache size limits, TTL-based invalidation, manual cache refresh triggers.

**SPARQL Query Performance:**
- Problem: No query optimization, indexing, or result caching for SPARQL queries against RDF graph.
- Files: `src/ghent_water/orchestrator/services/sparql_engine.py`
- Cause: Complex queries scan entire graph each time.
- Improvement path: Implement query result caching, add graph statistics for optimization, consider SPARQL endpoint with indexing (Virtuoso, Blazegraph) for production.

**Blocking `time.sleep` in Frontend:**
- Problem: `time.sleep(refresh_interval)` in simulation status polling blocks UI thread.
- Files: `src/ghent_water/frontend/components/simulation_status.py:116`
- Cause: Synchronous sleep prevents UI updates during waiting period.
- Improvement path: Use Streamlit's `st.runtime.scriptrunner.add_rerun_callback` or async polling pattern with st.empty().

## Fragile Areas

**Ontology Loading Chain:**
- Files: `src/ghent_water/orchestrator/services/ontology_store.py:52-137`
- Why fragile: Complex loading sequence from multiple directories (`ontology_base`, `case_data_path`, nested modules, bridges). Path construction uses relative paths that break with different project structures.
- Safe modification: Add validation for required paths, provide clear error messages for missing files, make paths configurable via settings.
- Test coverage: No tests for ontology loading logic. Unknown what happens if critical ontology files are missing.

**WebSocket Reconnection Logic:**
- Files: `src/ghent_water/frontend/services/websocket_client.py:143-157`
- Why fragile: Reconnection uses simple exponential backoff? No circuit breaker, no max retry limits. Can cause infinite connection attempts if service permanently down.
- Safe modification: Add max retry limit, circuit breaker pattern, explicit reconnection control.
- Test coverage: No tests for WebSocket failure scenarios, network interruption handling.

**LLM SPARQL Translation:**
- Files: `src/ghent_water/orchestrator/services/llm_sparql.py`
- Why fragile: Depends on external LLM API with rate limits, cost, and potential hallucination. Validation logic is regex-based, not full SPARQL parser. No fallback when LLM fails.
- Safe modification: Add comprehensive SPARQL parsing library (SPARQLWrapper, rdflib.query), implement fallback query templates, add monitoring for LLM failures.
- Test coverage: No tests for SPARQL generation, validation, or LLM error handling.

**Empty Error Returns:**
- Files: `src/ghent_water/frontend/services/websocket_client.py:172,251,261`, `src/ghent_water/frontend/services/api_client.py:132,202,204,221,223,274`, `src/ghent_water/orchestrator/services/ontology_store.py:162,188`
- Why fragile: Methods return `None` on errors but callers may not handle None properly. Can cause NoneType exceptions downstream.
- Safe modification: Raise exceptions instead of returning None, or document that None is expected return value.
- Test coverage: Unknown how many callers handle None properly.

## Scaling Limits

**In-Memory Ontology Graph:**
- Current capacity: RDF graph loaded entirely in memory using rdflib. Suitable for small ontologies (<100,000 triples).
- Limit: Will crash or become extremely slow with large ontologies (>1M triples). No pagination for entity retrieval.
- Scaling path: Use SPARQL endpoint with database backend (Virtuoso, Blazegraph, GraphDB), implement streaming/pagination for large result sets.

**Single-Threaded Sensor Generation:**
- Current capacity: Sensor data generated sequentially in `SensorDataGenerator`.
- Limit: Bottleneck with many sensors or high sampling rates.
- Scaling path: Parallel generation with asyncio or multiprocessing, batch insertion for RDF updates.

**No Horizontal Scaling Support:**
- Current capacity: Single orchestrator instance with in-memory state.
- Limit: Cannot distribute load across multiple instances. State (jobs, registry) not shared.
- Scaling path: Add database for persistence (PostgreSQL, Redis), use distributed job queue (Celery, RQ), implement session affinity for WebSockets.

**WebSocket Broadcast Scalability:**
- Current capacity: `broadcast_sensor_data()` in router maintains connection list in memory.
- Limit: Will fail with thousands of concurrent connections. No load balancing for WebSocket connections.
- Scaling path: Use Redis pub/sub for message broadcasting, separate WebSocket service from API gateway.

## Dependencies at Risk

**Deprecated `datetime.utcnow()`:**
- Risk: `datetime.utcnow()` deprecated in Python 3.12, will be removed in future version.
- Impact: Application will fail when upgrading to Python 3.14+.
- Migration plan: Replace all `datetime.utcnow()` with `datetime.now(tz=timezone.utc)` throughout codebase. 15 occurrences found in:
  - `src/ghent_water/frontend/components/sensor_panel.py:200`
  - `src/ghent_water/frontend/app.py:325`
  - `src/ghent_water/models/base.py:216,220`
  - `src/ghent_water/orchestrator/routers/sensors.py:31,225,251`
  - `src/ghent_water/orchestrator/schemas/models.py:25,86,120`
  - `src/ghent_water/orchestrator/services/sensor_generator.py:216`
  - `src/ghent_water/orchestrator/services/model_registry.py:31,69,70,106,110,112`

**Optional Dependency on NumPy:**
- Risk: `numpy` import is optional. Sensor generation falls back to `random` module if NumPy not available.
- Impact: Reduced simulation quality, different behavior depending on installation. Random generation patterns will differ.
- Migration plan: Make NumPy a required dependency (`pyproject.toml` line 18), or document clearly that sensor data quality varies with NumPy availability.

## Missing Critical Features

**No Persistence Layer:**
- Problem: All data (jobs, model registry, sensor readings) stored in memory. Lost on restart.
- Blocks: Job history, audit trails, long-running simulations, analytics, debugging production issues.
- Files: `src/ghent_water/orchestrator/services/model_registry.py` (in-memory `_jobs`, `_models` dicts)

**No Test Coverage:**
- Problem: No test directory, no unit tests, integration tests, or E2E tests found in codebase.
- Blocks: Refactoring confidence, regression prevention, CI/CD quality gates.
- Impact: 9,881 lines of Python code have zero test coverage.

**No Authentication/Authorization:**
- Problem: All endpoints publicly accessible, no user management, no RBAC.
- Blocks: Production deployment, multi-tenant usage, audit trails, security compliance.

**No Configuration Management:**
- Problem: Configuration scattered across `.env`, hardcoded values, and code.
- Blocks: Environment-specific configs (dev/staging/prod), feature flags, runtime configuration updates.

**No Monitoring/Logging Infrastructure:**
- Problem: Only basic logging to stdout/console. No metrics, tracing, or alerting.
- Blocks: Production observability, performance debugging, incident response.

## Test Coverage Gaps

**No Test Directory:**
- What's not tested: Entire codebase (9,881 lines of Python code across 30+ files)
- Files: All files in `src/ghent_water/`
- Risk: Refactoring will break code, regressions undetected, bugs shipped to production.
- Priority: High - Foundation for reliable development.

**Simulation Logic Untested:**
- What's not tested: Model simulation calculations in stub files (dwp.py, wwtp.py, industry.py, river.py, residential.py)
- Files: `src/ghent_water/models/stubs/`
- Risk: Bugs in removal efficiency calculations, scenario modifiers, random variance logic.
- Priority: High - Core business logic.

**Ontology Queries Untested:**
- What's not tested: SPARQL queries, entity extraction, flow connections, sensor mappings
- Files: `src/ghent_water/orchestrator/services/sparql_engine.py`, `src/ghent_water/frontend/components/map_view.py`
- Risk: Wrong query results break frontend display, incorrect entity relationships.
- Priority: Medium - Critical for correct data retrieval.

**LLM Integration Untested:**
- What's not tested: Natural language to SPARQL translation, validation logic, fallback behavior
- Files: `src/ghent_water/orchestrator/services/llm_sparql.py`
- Risk: LLM hallucinations produce invalid SPARQL, validation misses syntax errors, fallback not tested.
- Priority: Medium - Important feature with external dependency.

**WebSocket Handling Untested:**
- What's not tested: Connection lifecycle, reconnection, error handling, message broadcast
- Files: `src/ghent_water/frontend/services/websocket_client.py`, `src/ghent_water/orchestrator/routers/websocket.py`
- Risk: Connection failures not handled properly, reconnection loops, memory leaks from unclosed connections.
- Priority: Medium - Real-time data feature.

**API Endpoints Untested:**
- What's not tested: All FastAPI endpoints, request validation, error responses
- Files: `src/ghent_water/orchestrator/routers/*.py`
- Risk: Invalid inputs crash services, incorrect status codes, missing error handling.
- Priority: Medium - Core API contract.

**Frontend Components Untested:**
- What's not tested: Streamlit components, user interactions, state management
- Files: `src/ghent_water/frontend/components/*.py`, `src/ghent_water/frontend/app.py`
- Risk: UI bugs, state corruption, poor user experience.
- Priority: Low - Can be manually tested, but automation would help.

---

*Concerns audit: 2026-01-19*
