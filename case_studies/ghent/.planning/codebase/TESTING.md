# Testing Patterns

**Analysis Date:** 2026-01-19

## Test Framework

**Runner:**
- **pytest** [8.0+] - Listed in pyproject.toml as dev dependency
- **pytest-asyncio** [0.24+] - For async test support
- **httpx** [0.28+] - Listed in dev dependencies for HTTP mocking

**Config:**
- No pytest configuration file detected (no `pytest.ini`, `pyproject.toml` pytest section, or `setup.cfg`)
- No conftest.py found in project root

**Run Commands:**
```bash
# Run all tests (assumed - no actual tests exist)
pytest

# Run with async support (assumed)
pytest -p pytest_asyncio

# Run with coverage (assumed - not configured)
pytest --cov=ghent_water
```

## Test File Organization

**Location:**
- **No test files found** in the codebase
- No `tests/` directory exists in project root
- No co-located test files (e.g., `test_*.py` or `*_test.py`) in `src/`

**Naming:**
- Not applicable (no tests present)

**Structure:**
```
# Expected structure (not currently implemented)
tests/
├── unit/
│   ├── test_ontology_store.py
│   ├── test_model_registry.py
│   └── test_sparql_engine.py
├── integration/
│   ├── test_api_endpoints.py
│   └── test_simulation_flow.py
└── conftest.py
```

## Test Structure

**Suite Organization:**
- Not applicable (no tests present)

**Patterns:**
- Not applicable (no tests present)

**Setup pattern:** Not established

**Teardown pattern:** Not established

**Assertion pattern:** Not established

## Mocking

**Framework:** None detected (no `unittest.mock` imports found, no pytest-mock configured)

**Patterns:** Not applicable (no tests present)

**What to Mock:** Not established

**What NOT to Mock:** Not established

## Fixtures and Factories

**Test Data:**
- No test fixtures found
- No test data factories implemented

**Location:**
- Not applicable (no tests present)

## Coverage

**Requirements:** None enforced

**View Coverage:**
```bash
# Command not configured
# Would typically be: pytest --cov=ghent_water --cov-report=html
```

**Current status:**
- 0% code coverage (no tests exist)

## Test Types

**Unit Tests:**
- **Not implemented**

**Integration Tests:**
- **Not implemented**

**E2E Tests:**
- **Not implemented**

## Common Patterns

**Async Testing:**
- pytest-asyncio is available in dependencies
- No async test examples found
- Pattern not established

**Error Testing:**
- No error testing patterns found
- Pattern not established

## Recommendations

**Testing Infrastructure Needed:**

1. **Create test configuration** (`pyproject.toml` or `pytest.ini`):
```ini
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
```

2. **Create tests directory structure:**
```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests
│   ├── __init__.py
│   ├── test_ontology_store.py
│   ├── test_sparql_engine.py
│   └── test_model_registry.py
├── integration/             # Integration tests
│   ├── __init__.py
│   ├── test_api_endpoints.py
│   └── test_simulation_flow.py
└── e2e/                     # End-to-end tests
    ├── __init__.py
    └── test_full_system.py
```

3. **Key areas to test:**
   - `src/ghent_water/orchestrator/services/ontology_store.py` - Ontology loading, SPARQL queries
   - `src/ghent_water/orchestrator/services/model_registry.py` - Model registration, job management
   - `src/ghent_water/orchestrator/routers/` - API endpoints, error handling
   - `src/ghent_water/models/stubs/` - Model simulations, compliance checking
   - `src/ghent_water/frontend/services/api_client.py` - API client methods

4. **Fixtures to create:**
   - Mock ontology graph fixture
   - Mock FastAPI app fixture
   - Mock model endpoints fixture
   - Test data generators for entities and sensors

---

*Testing analysis: 2026-01-19*
