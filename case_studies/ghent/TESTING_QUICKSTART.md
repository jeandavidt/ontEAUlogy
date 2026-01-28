# Testing Quickstart Guide

This guide provides quick instructions for running tests to verify backend-frontend communication.

## Prerequisites

```bash
# Backend dependencies
pip install -e ".[dev,test]"

# Frontend dependencies
cd frontend-react
npm install
```

## Running Backend Tests

### All Backend Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/ghent_water/orchestrator --cov-report=html
```

### Backend-Frontend Integration Tests

These tests verify that the backend API returns data in the format expected by the frontend:

```bash
# Run integration tests only
pytest tests/integration/test_backend_frontend_integration.py -v

# Run specific test class
pytest tests/integration/test_backend_frontend_integration.py::TestFrontendBackendCommunication -v
```

### Backend Unit Tests

```bash
# Run all unit tests
pytest tests/unit -v

# Run specific service tests
pytest tests/unit/orchestrator/services/test_sparql_engine.py -v
pytest tests/unit/orchestrator/services/test_ontology_store.py -v

# Run specific router tests
pytest tests/unit/orchestrator/routers/test_query_router.py -v
pytest tests/unit/orchestrator/routers/test_ontology_router.py -v
```

## Running Frontend Tests

### All Frontend Tests

```bash
cd frontend-react

# Run tests in watch mode (development)
npm run test

# Run tests once (CI mode)
npm run test:run

# Run with coverage
npm run test:coverage

# Run with UI
npm run test:ui
```

### Frontend API Communication Tests

These tests verify that the frontend API hooks correctly communicate with the backend:

```bash
cd frontend-react

# Run API query tests
npm run test:run -- src/api/__tests__/queries.test.ts

# Run API client tests
npm run test:run -- src/api/__tests__/client.test.ts
```

## Testing Backend-Frontend Communication

### Quick Verification

To quickly verify that backend and frontend can communicate:

1. **Start the backend:**
   ```bash
   uvicorn ghent_water.orchestrator.main:app --host 0.0.0.0 --port 8080
   ```

2. **Run integration tests:**
   ```bash
   pytest tests/integration/test_backend_frontend_integration.py -v
   ```

3. **Run frontend tests with MSW mocking:**
   ```bash
   cd frontend-react
   npm run test:run
   ```

### Manual End-to-End Test

1. **Start backend:**
   ```bash
   uvicorn ghent_water.orchestrator.main:app --host 0.0.0.0 --port 8080
   ```

2. **Start frontend:**
   ```bash
   cd frontend-react
   npm run dev
   ```

3. **Open browser** to `http://localhost:3000` and verify:
   - Entities load on the map
   - SPARQL queries execute
   - Entity details display when clicking entities

## Test Coverage

### Backend Coverage

```bash
# Generate HTML coverage report
pytest --cov=src/ghent_water/orchestrator --cov-report=html

# View report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Frontend Coverage

```bash
cd frontend-react

# Generate coverage report
npm run test:coverage

# View report
open coverage/index.html  # macOS
```

## Common Test Scenarios

### Testing a Specific API Endpoint

**Backend:**
```bash
# Test SPARQL endpoint
pytest tests/integration/test_backend_frontend_integration.py::TestFrontendBackendCommunication::test_sparql_query_endpoint_matches_frontend_format -v
```

**Frontend:**
```bash
cd frontend-react
# Test SPARQL query hook
npm run test:run -- -t "executes SPARQL query successfully"
```

### Testing Error Handling

**Backend:**
```bash
pytest tests/integration/test_backend_frontend_integration.py::TestFrontendBackendCommunication::test_sparql_error_format_matches_frontend_expectations -v
```

**Frontend:**
```bash
cd frontend-react
npm run test:run -- -t "handles invalid SPARQL syntax"
```

### Testing Data Transformations

**Backend:**
```bash
pytest tests/integration/test_backend_frontend_integration.py::TestDataTypeCompatibility -v
```

**Frontend:**
```bash
cd frontend-react
npm run test:run -- -t "fetches and transforms entities correctly"
```

## Debugging Tests

### Backend Debugging

```bash
# Run tests with print statements visible
pytest -s tests/integration/test_backend_frontend_integration.py

# Run with detailed error output
pytest -vv tests/integration/test_backend_frontend_integration.py

# Drop into debugger on failure
pytest --pdb tests/integration/test_backend_frontend_integration.py
```

### Frontend Debugging

```bash
cd frontend-react

# Run with detailed output
npm run test:run -- --reporter=verbose

# Run in watch mode for debugging
npm run test

# Run with UI for interactive debugging
npm run test:ui
```

## Continuous Integration

### GitHub Actions Workflow

Example workflow for CI:

```yaml
name: Test Backend-Frontend Communication

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -e ".[dev,test]"
      - run: pytest tests/integration/test_backend_frontend_integration.py -v

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - working-directory: ./frontend-react
        run: |
          npm ci
          npm run test:run
```

## Troubleshooting

### Backend Tests Failing

**Issue:** `No ontology loaded`
- **Solution:** Ensure ontology files are in the correct location or use test fixtures

**Issue:** `Model services not available`
- **Solution:** These tests are skipped if models aren't running. Start model services or mark as expected skip.

**Issue:** `ImportError` for test modules
- **Solution:** Ensure you've installed test dependencies: `pip install -e ".[dev,test]"`

### Frontend Tests Failing

**Issue:** `Cannot find module 'msw'`
- **Solution:** Run `npm install` in `frontend-react/` directory

**Issue:** `ReferenceError: fetch is not defined`
- **Solution:** Ensure `jsdom` is installed and vitest config includes `environment: 'jsdom'`

**Issue:** Tests timeout
- **Solution:** Increase timeout in vitest config or individual tests

### Integration Tests Failing

**Issue:** Response format doesn't match
- **Solution:** Check [TESTING_STRATEGY.md](./TESTING_STRATEGY.md) for expected formats. Backend and frontend may need alignment.

**Issue:** CORS errors
- **Solution:** In development, ensure vite proxy is configured correctly in `vite.config.ts`

## What Each Test File Tests

### Backend Integration Tests
- **`test_backend_frontend_integration.py`**: Verifies API response formats match frontend expectations

### Backend Unit Tests
- **`test_query_router.py`**: Query endpoint logic
- **`test_ontology_router.py`**: Ontology endpoint logic
- **`test_sparql_engine.py`**: SPARQL execution engine
- **`test_ontology_store.py`**: RDF graph management
- **`test_llm_sparql.py`**: Natural language to SPARQL translation

### Frontend Tests
- **`queries.test.ts`**: API query hooks (useEntities, useSparqlQuery, etc.)
- **`client.test.ts`**: Axios client configuration

## Key Test Insights

### Data Flow
1. Frontend makes request via axios client (`client.ts`)
2. Request goes through vite proxy to backend
3. Backend router receives request
4. Backend service processes request
5. Backend returns response in expected format
6. Frontend hook transforms response for components
7. Component receives typed data

### What Makes Tests Pass
- ✅ Backend returns correct HTTP status codes
- ✅ Backend response includes all required fields
- ✅ Data types match (numbers, strings, booleans)
- ✅ Nested structures match (e.g., `results.bindings`)
- ✅ Error responses include `detail` field
- ✅ URIs are consistently formatted
- ✅ IDs can be extracted from URIs

### Common Gotchas
- Frontend expects `lat`/`lon`, not `latitude`/`longitude`
- Numbers in RDF may come as strings and need conversion
- Empty values should be empty strings `""`, not `null`
- SPARQL results have nested structure: `results.bindings`
- Error responses must include `detail` field for axios interceptor

## Next Steps

After tests pass:
1. Review [TESTING_STRATEGY.md](./TESTING_STRATEGY.md) for comprehensive testing approach
2. Add component tests for frontend UI components
3. Add E2E tests with Playwright
4. Set up coverage monitoring in CI
5. Configure automated test runs on PR

## Getting Help

- See [TESTING_STRATEGY.md](./TESTING_STRATEGY.md) for detailed strategy
- Check test files for examples of specific scenarios
- Run tests with `-v` or `--verbose` for detailed output
- Use `--pdb` (pytest) or `test:ui` (vitest) for interactive debugging
