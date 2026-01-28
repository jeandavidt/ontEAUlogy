# Testing Strategy for Ghent Water System

## Table of Contents

1. [Overview](#overview)
2. [Architecture Summary](#architecture-summary)
3. [Testing Tools and Frameworks](#testing-tools-and-frameworks)
4. [Backend Testing Strategy](#backend-testing-strategy)
5. [Frontend Testing Strategy](#frontend-testing-strategy)
6. [Integration Testing](#integration-testing)
7. [End-to-End Testing](#end-to-end-testing)
8. [Test Organization](#test-organization)
9. [Coverage Goals and Metrics](#coverage-goals-and-metrics)
10. [CI/CD Integration](#cicd-integration)
11. [Maintenance Guidelines](#maintenance-guidelines)
12. [Best Practices](#best-practices)

---

## Overview

This document outlines the comprehensive testing strategy for the Ghent Water System project, a multi-service application consisting of:
- **Frontend**: React application with TypeScript (Vite, TanStack Query, Zustand)
- **Backend**: FastAPI orchestrator service with multiple routers and services
- **Model Services**: 12 distributed water system model services

The testing strategy emphasizes:
- **Quality**: Maintaining high code coverage (>90% target)
- **Reliability**: Preventing regressions through comprehensive test suites
- **Maintainability**: Clear patterns and structures for adding new tests
- **Performance**: Fast test execution for rapid feedback
- **Integration**: Seamless CI/CD pipeline integration

---

## Architecture Summary

### Backend Architecture (Python/FastAPI)

```
src/ghent_water/orchestrator/
├── main.py                    # Application entry point with lifespan management
├── config.py                  # Configuration management
├── routers/                   # API endpoint handlers
│   ├── discovery.py           # Model discovery endpoints
│   ├── query.py              # SPARQL & natural language query endpoints
│   ├── simulation.py         # Simulation orchestration endpoints
│   ├── ontology.py           # Ontology management endpoints
│   ├── sensors.py            # Sensor data endpoints
│   └── websocket.py          # WebSocket for real-time data
├── services/                  # Business logic layer
│   ├── ontology_store.py     # RDF graph management
│   ├── sparql_engine.py      # SPARQL query execution
│   ├── llm_sparql.py         # NL to SPARQL translation
│   ├── sensor_config.py      # Sensor configuration
│   ├── sensor_generator.py   # Synthetic sensor data generation
│   ├── model_registry.py     # Model service registry
│   └── mapping_agent.py      # Entity-model mapping
└── schemas/
    └── models.py             # Pydantic models for requests/responses
```

### Frontend Architecture (React/TypeScript)

```
frontend-react/src/
├── api/                      # API client layer
│   ├── client.ts            # Axios configuration
│   ├── queries.ts           # TanStack Query hooks
│   ├── types.ts             # TypeScript interfaces
│   ├── mockData.ts          # Mock data for development/testing
│   └── webSocket.ts         # WebSocket client
├── components/              # React components
│   ├── common/              # Reusable components
│   ├── map/                 # Map visualization
│   ├── topology/            # Topology graph
│   ├── simulation/          # Simulation forms
│   └── results/             # Result displays
├── stores/                  # Zustand state management
│   └── useSelectionStore.ts # Entity selection state
├── layouts/                 # Layout components
├── pages/                   # Page components
└── utils/                   # Utility functions
```

---

## Testing Tools and Frameworks

### Backend Testing Stack

| Tool | Purpose | Version |
|------|---------|---------|
| **pytest** | Test framework | >=8.0 |
| **pytest-asyncio** | Async test support | >=0.24 |
| **httpx** | HTTP client for API testing | >=0.28 |
| **pytest-cov** | Coverage reporting | Latest |
| **pytest-mock** | Mocking utilities | Latest |
| **rdflib** | RDF/SPARQL testing | >=7.0 |
| **fastapi.testclient** | FastAPI endpoint testing | Built-in |

### Frontend Testing Stack

| Tool | Purpose | Version |
|------|---------|---------|
| **Vitest** | Test framework & runner | ^4.0.17 |
| **@testing-library/react** | React component testing | ^16.3.2 |
| **@testing-library/jest-dom** | DOM matchers | ^6.9.1 |
| **jsdom** | DOM environment | ^27.4.0 |
| **@vitest/coverage-v8** | Coverage reporting | Built-in |
| **MSW (Mock Service Worker)** | API mocking | Recommended |

---

## Backend Testing Strategy

### Unit Testing

#### Service Layer Testing

**Location**: `tests/unit/orchestrator/services/`

**Scope**: Test individual service classes in isolation with mocked dependencies.

**Example Structure**:

```python
# tests/unit/orchestrator/services/test_sparql_engine.py

import pytest
from ghent_water.orchestrator.services.sparql_engine import SparqlEngine
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS

@pytest.fixture
def sample_graph():
    """Create a sample RDF graph for testing."""
    g = Graph()
    wf = Namespace("https://w3id.org/waterframe/")
    g.bind("wf", wf)
    
    # Add test data
    g.add((wf.DWP1, RDF.type, wf.DrinkingWaterPlant))
    g.add((wf.DWP1, RDFS.label, Literal("DWP1")))
    g.add((wf.DWP1, wf.hasCapacity, Literal(2000)))
    
    return g

@pytest.fixture
def engine(sample_graph):
    """Create SPARQL engine with test graph."""
    engine = SparqlEngine(sample_graph)
    return engine

def test_execute_simple_select_query(engine):
    """Test executing a basic SELECT query."""
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX wf: <https://w3id.org/waterframe/>
    
    SELECT ?plant WHERE {
        ?plant rdf:type wf:DrinkingWaterPlant .
    }
    """
    
    result = engine.execute_query(query, format="json")
    
    assert result["format"] == "json"
    assert "results" in result
    assert "bindings" in result["results"]
    assert len(result["results"]["bindings"]) > 0
    assert result["query_time_ms"] >= 0

def test_execute_query_with_filter(engine):
    """Test query with FILTER clause."""
    query = """
    PREFIX wf: <https://w3id.org/waterframe/>
    
    SELECT ?plant ?capacity WHERE {
        ?plant wf:hasCapacity ?capacity .
        FILTER(?capacity > 1500)
    }
    """
    
    result = engine.execute_query(query)
    bindings = result["results"]["bindings"]
    
    assert len(bindings) > 0
    for binding in bindings:
        assert int(binding["capacity"]["value"]) > 1500

def test_execute_query_no_graph():
    """Test error handling when no graph is set."""
    engine = SparqlEngine()
    
    with pytest.raises(RuntimeError, match="No graph set"):
        engine.execute_query("SELECT * WHERE { ?s ?p ?o }")

def test_format_results_csv(engine):
    """Test CSV formatting of query results."""
    query = "SELECT * WHERE { ?s ?p ?o } LIMIT 5"
    result = engine.execute_query(query, format="csv")
    
    assert result["format"] == "csv"
    assert isinstance(result["results"], str)
    assert "\n" in result["results"]  # Contains rows

def test_validate_query_syntax(engine):
    """Test query validation."""
    valid_query = "SELECT ?s WHERE { ?s ?p ?o }"
    invalid_query = "INVALID SPARQL SYNTAX"
    
    valid_result = engine.validate_query(valid_query)
    assert valid_result["valid"] is True
    assert valid_result["error"] is None
    
    invalid_result = engine.validate_query(invalid_query)
    assert invalid_result["valid"] is False
    assert invalid_result["error"] is not None
```

**Key Service Test Files to Create**:

1. `test_sparql_engine.py` - SPARQL execution, validation, formatting
2. `test_ontology_store.py` - Graph loading, entity retrieval, caching
3. `test_llm_sparql.py` - NL to SPARQL translation, validation
4. `test_sensor_generator.py` - Sensor data generation, timing
5. `test_model_registry.py` - Model registration, lookup, health checks
6. `test_sensor_config.py` - Sensor configuration management

**Coverage Targets**:
- Service classes: >95%
- Business logic methods: 100%
- Error handling: 100%

#### Router Testing

**Location**: `tests/unit/orchestrator/routers/`

**Scope**: Test router endpoints with mocked services.

**Example Structure**:

```python
# tests/unit/orchestrator/routers/test_query_router.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from ghent_water.orchestrator.main import app

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

@pytest.fixture
def mock_sparql_engine():
    """Mock SPARQL engine service."""
    with patch("ghent_water.orchestrator.routers.query.sparql_engine") as mock:
        mock.execute_query.return_value = {
            "head": {"vars": ["entity"]},
            "results": {"bindings": [{"entity": {"type": "uri", "value": "http://example.org/DWP1"}}]},
            "format": "json",
            "query_time_ms": 45.2
        }
        yield mock

def test_sparql_endpoint_success(client, mock_sparql_engine):
    """Test successful SPARQL query execution."""
    query = "SELECT ?s WHERE { ?s ?p ?o } LIMIT 10"
    
    response = client.post(
        "/api/v1/query/sparql",
        json={"query": query, "format": "json"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "bindings" in data["results"]
    assert "query_time_ms" in data

def test_sparql_endpoint_query_too_long(client):
    """Test rejection of excessively long queries."""
    long_query = "SELECT * WHERE { ?s ?p ?o }" * 1000  # Exceed MAX_QUERY_LENGTH
    
    response = client.post(
        "/api/v1/query/sparql",
        json={"query": long_query, "format": "json"}
    )
    
    assert response.status_code == 400
    assert "too long" in response.json()["detail"].lower()

def test_sparql_endpoint_forbidden_operations(client):
    """Test rejection of write operations."""
    forbidden_queries = [
        "INSERT DATA { <http://example.org/s> <http://example.org/p> <http://example.org/o> }",
        "DELETE WHERE { ?s ?p ?o }",
        "DROP GRAPH <http://example.org/graph>"
    ]
    
    for query in forbidden_queries:
        response = client.post(
            "/api/v1/query/sparql",
            json={"query": query, "format": "json"}
        )
        assert response.status_code == 400
        assert "not allowed" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_natural_language_query_success(client):
    """Test natural language query endpoint."""
    with patch("ghent_water.orchestrator.routers.query.get_llm_sparql_translator") as mock_translator:
        translator_instance = AsyncMock()
        translator_instance._initialized = True
        translator_instance.execute_query.return_value = {
            "generated_sparql": "SELECT ?dwp WHERE { ?dwp a wf:DrinkingWaterPlant }",
            "results": {"bindings": [{"dwp": {"value": "DWP1"}}]},
            "execution_plan": "Query successful"
        }
        mock_translator.return_value = translator_instance
        
        response = client.post(
            "/api/v1/query/natural",
            json={"question": "What are the drinking water plants?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "original_question" in data
        assert "generated_sparql" in data
        assert "results" in data

def test_query_timeout(client, mock_sparql_engine):
    """Test query timeout handling."""
    import asyncio
    mock_sparql_engine.execute_query.side_effect = asyncio.TimeoutError()
    
    response = client.post(
        "/api/v1/query/sparql",
        json={"query": "SELECT * WHERE { ?s ?p ?o }", "format": "json"}
    )
    
    assert response.status_code == 408
    assert "timeout" in response.json()["detail"].lower()
```

**Key Router Test Files to Create**:

1. `test_query_router.py` - SPARQL/NL query endpoints
2. `test_ontology_router.py` - Entity retrieval, triplet queries
3. `test_simulation_router.py` - Simulation orchestration
4. `test_discovery_router.py` - Model discovery
5. `test_sensor_router.py` - Sensor data endpoints
6. `test_websocket_router.py` - WebSocket connections

**Coverage Targets**:
- Router endpoints: >90%
- Request validation: 100%
- Error responses: 100%

#### Schema/Model Testing

**Location**: `tests/unit/orchestrator/schemas/`

**Scope**: Test Pydantic models for validation.

```python
# tests/unit/orchestrator/schemas/test_models.py

import pytest
from pydantic import ValidationError
from ghent_water.orchestrator.schemas.models import (
    SparqlQueryRequest,
    ModelRegistrationRequest,
    SimulationRequest
)

def test_sparql_query_request_valid():
    """Test valid SPARQL query request."""
    request = SparqlQueryRequest(
        query="SELECT ?s WHERE { ?s ?p ?o }",
        format="json"
    )
    assert request.query is not None
    assert request.format == "json"

def test_sparql_query_request_invalid_format():
    """Test invalid format rejection."""
    with pytest.raises(ValidationError):
        SparqlQueryRequest(
            query="SELECT ?s WHERE { ?s ?p ?o }",
            format="invalid_format"
        )

def test_model_registration_required_fields():
    """Test model registration requires all fields."""
    with pytest.raises(ValidationError):
        ModelRegistrationRequest(
            id="test",
            name="Test Model"
            # Missing required fields: endpoint, capabilities, entities
        )

def test_simulation_request_validation():
    """Test simulation request validation."""
    valid_request = SimulationRequest(
        entity_ids=["DWP1", "WWTP1"],
        scenario={"duration": 3600, "timestep": 60},
        parameters={"initial_flow": 100}
    )
    assert len(valid_request.entity_ids) == 2
    assert valid_request.scenario["duration"] == 3600
```

### Integration Testing

**Location**: `tests/integration/`

**Scope**: Test interactions between components with real dependencies (but isolated from external services).

#### Router Integration Tests

```python
# tests/integration/test_query_router_integration.py

import pytest
from fastapi.testclient import TestClient
from ghent_water.orchestrator.main import app
from ghent_water.orchestrator.services.ontology_store import ontology_store

@pytest.fixture(scope="module")
async def setup_ontology():
    """Load actual ontology for integration tests."""
    await ontology_store.load_ontology()
    yield
    # Cleanup if needed

@pytest.mark.integration
def test_sparql_query_against_real_ontology(setup_ontology):
    """Test SPARQL query execution against loaded ontology."""
    client = TestClient(app)
    
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX wf: <https://w3id.org/waterframe/>
    
    SELECT ?entity ?type WHERE {
        ?entity rdf:type ?type .
        FILTER(CONTAINS(STR(?type), "WaterFrame"))
    } LIMIT 10
    """
    
    response = client.post(
        "/api/v1/query/sparql",
        json={"query": query, "format": "json"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]["bindings"]) > 0

@pytest.mark.integration
def test_entity_retrieval_workflow():
    """Test complete entity retrieval workflow."""
    client = TestClient(app)
    
    # 1. Get all entities
    response = client.get("/api/v1/ontology/entities")
    assert response.status_code == 200
    entities = response.json()["entities"]
    assert len(entities) > 0
    
    # 2. Get specific entity details
    entity_id = entities[0]["id"]
    response = client.get(f"/api/v1/ontology/entities/{entity_id}")
    assert response.status_code == 200
    entity_detail = response.json()
    
    # 3. Get entity triplets
    response = client.get(f"/api/v1/ontology/entities/{entity_id}/triplets")
    assert response.status_code == 200
    triplets = response.json()["triples"]
    assert isinstance(triplets, list)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_model_discovery_and_registration():
    """Test model discovery integration."""
    client = TestClient(app)
    
    # Check health endpoint includes model registry
    response = client.get("/health")
    assert response.status_code == 200
    health = response.json()
    assert "model_registry" in health["components"]
    
    # Check discovery endpoint
    response = client.get("/api/v1/discovery/models")
    assert response.status_code == 200
    models = response.json()["models"]
    # May be empty if no models running, but should not error
    assert isinstance(models, list)
```

**Key Integration Test Files**:

1. `test_query_router_integration.py` - Query workflows
2. `test_simulation_integration.py` - End-to-end simulation
3. `test_ontology_loading_integration.py` - Ontology lifecycle
4. `test_sensor_streaming_integration.py` - Sensor data flow
5. `test_model_discovery_integration.py` - Model registration

**Coverage Targets**:
- Critical workflows: 100%
- Integration points: >90%

### Testing Fixtures and Utilities

**Location**: `tests/conftest.py`

**Current Fixtures**:
- `fresh_registry` - Clean model registry
- `mock_httpx_client` - HTTP client mock
- `sample_rdf_graph` - Test RDF data
- `app_client` - FastAPI test client

**Additional Recommended Fixtures**:

```python
# tests/conftest.py additions

@pytest.fixture
def mock_llm_service():
    """Mock LLM service for NL query testing."""
    from ghent_water.orchestrator.services.llm_sparql import LLMService
    with patch.object(LLMService, 'translate') as mock:
        mock.return_value = {
            "is_valid": True,
            "sparql": "SELECT ?s WHERE { ?s ?p ?o }",
            "validation_error": None
        }
        yield mock

@pytest.fixture
def temp_ontology_file(tmp_path):
    """Create temporary ontology file for testing."""
    ontology_content = """
    @prefix wf: <https://w3id.org/waterframe/> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    
    wf:DWP1 a wf:DrinkingWaterPlant ;
        rdfs:label "DWP1" .
    """
    file_path = tmp_path / "test_ontology.ttl"
    file_path.write_text(ontology_content)
    return str(file_path)

@pytest.fixture
async def running_app():
    """Start app with lifespan for full integration tests."""
    from ghent_water.orchestrator.main import app
    from httpx import AsyncClient, ASGITransport
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

@pytest.fixture
def mock_sensor_readings():
    """Generate mock sensor readings."""
    return [
        {
            "sensor_id": "SENSOR_DWP1_FLOW",
            "timestamp": "2024-01-20T10:00:00Z",
            "value": 125.5,
            "unit": "m3/h"
        },
        # ... more readings
    ]
```

---

## Frontend Testing Strategy

### Unit Testing Components

**Location**: `frontend-react/src/components/**/*.test.tsx`

**Scope**: Test individual React components in isolation.

**Example Structure**:

```typescript
// frontend-react/src/components/common/EntityDetails.test.tsx

import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import EntityDetails from './EntityDetails';

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('EntityDetails', () => {
  it('renders entity information correctly', () => {
    const entity = {
      id: 'DWP1',
      label: 'Drinking Water Plant 1',
      type: 'DrinkingWaterPlant',
      coordinates: [51.05, 3.72],
      capacity: 2000,
      description: 'Main drinking water plant'
    };
    
    render(<EntityDetails entity={entity} />, { wrapper: createWrapper() });
    
    expect(screen.getByText('Drinking Water Plant 1')).toBeInTheDocument();
    expect(screen.getByText(/DrinkingWaterPlant/i)).toBeInTheDocument();
    expect(screen.getByText(/2000/)).toBeInTheDocument();
  });

  it('handles null entity gracefully', () => {
    render(<EntityDetails entity={null} />, { wrapper: createWrapper() });
    
    expect(screen.getByText(/no entity selected/i)).toBeInTheDocument();
  });

  it('displays loading state while fetching triplets', async () => {
    const entity = {
      id: 'DWP1',
      label: 'DWP1',
      type: 'DrinkingWaterPlant'
    };
    
    render(<EntityDetails entity={entity} />, { wrapper: createWrapper() });
    
    // Should show loading indicator
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });
});
```

**Component Test Coverage**:

1. **Common Components** (`components/common/`)
   - `EntityDetails.test.tsx` - Entity display, null handling
   - `SPARQLSection.test.tsx` - Query input, result display
   - `SensorVisualizer.test.tsx` - Chart rendering, data formatting

2. **Map Components** (`components/map/`)
   - `WaterMap.test.tsx` - Map initialization, marker placement, interactions

3. **Topology Components** (`components/topology/`)
   - `WaterTopology.test.tsx` - Graph rendering, node/edge interactions
   - `Breadcrumbs.test.tsx` - Navigation history

4. **Simulation Components** (`components/simulation/`)
   - `SimulationForm.test.tsx` - Form validation, submission

5. **Results Components** (`components/results/`)
   - `SimulationCharts.test.tsx` - Chart rendering, data visualization

### Testing Custom Hooks (API Layer)

**Location**: `frontend-react/src/api/__tests__/`

```typescript
// frontend-react/src/api/__tests__/queries.test.ts

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useEntities, useSparqlQuery } from '../queries';
import client from '../client';

vi.mock('../client');

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('useEntities', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('fetches and transforms entities correctly', async () => {
    const mockResponse = {
      data: {
        entities: [
          {
            id: 'DWP1',
            label: 'DWP1',
            type: 'DrinkingWaterPlant',
            lat: 51.05,
            lon: 3.72,
            capacity: 2000
          }
        ]
      }
    };
    
    vi.mocked(client.get).mockResolvedValueOnce(mockResponse);
    
    const { result } = renderHook(() => useEntities(), {
      wrapper: createWrapper()
    });
    
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    
    expect(result.current.data).toHaveLength(1);
    expect(result.current.data[0].id).toBe('DWP1');
    expect(result.current.data[0].coordinates).toEqual([51.05, 3.72]);
  });

  it('handles API errors gracefully', async () => {
    vi.mocked(client.get).mockRejectedValueOnce(new Error('Network error'));
    
    const { result } = renderHook(() => useEntities(), {
      wrapper: createWrapper()
    });
    
    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error).toBeDefined();
  });
});

describe('useSparqlQuery', () => {
  it('sends SPARQL query and returns results', async () => {
    const mockResponse = {
      data: {
        results: {
          bindings: [
            { entity: { value: 'DWP1', type: 'uri' } }
          ]
        },
        query_time_ms: 45.2
      }
    };
    
    vi.mocked(client.post).mockResolvedValueOnce(mockResponse);
    
    const { result } = renderHook(() => useSparqlQuery(), {
      wrapper: createWrapper()
    });
    
    result.current.mutate({
      query: 'SELECT ?entity WHERE { ?entity a wf:DrinkingWaterPlant }',
      format: 'json'
    });
    
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    
    expect(result.current.data).toEqual(mockResponse.data);
  });
});
```

### Testing State Management (Zustand)

**Location**: `frontend-react/src/stores/__tests__/`

```typescript
// frontend-react/src/stores/__tests__/useSelectionStore.test.ts

import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useSelectionStore } from '../useSelectionStore';

describe('useSelectionStore', () => {
  beforeEach(() => {
    // Reset store before each test
    const { result } = renderHook(() => useSelectionStore());
    act(() => {
      result.current.setSelectedEntityId(null);
    });
  });

  it('initializes with null selection', () => {
    const { result } = renderHook(() => useSelectionStore());
    
    expect(result.current.selectedEntityId).toBeNull();
    expect(result.current.history).toEqual([]);
  });

  it('sets selected entity and updates history', () => {
    const { result } = renderHook(() => useSelectionStore());
    
    act(() => {
      result.current.setSelectedEntityId('DWP1');
    });
    
    expect(result.current.selectedEntityId).toBe('DWP1');
    expect(result.current.history).toEqual(['DWP1']);
  });

  it('pushes new selection to history', () => {
    const { result } = renderHook(() => useSelectionStore());
    
    act(() => {
      result.current.setSelectedEntityId('DWP1');
      result.current.pushSelection('WWTP1');
    });
    
    expect(result.current.selectedEntityId).toBe('WWTP1');
    expect(result.current.history).toEqual(['DWP1', 'WWTP1']);
  });

  it('pops selection from history', () => {
    const { result } = renderHook(() => useSelectionStore());
    
    act(() => {
      result.current.setSelectedEntityId('DWP1');
      result.current.pushSelection('WWTP1');
      result.current.popSelection();
    });
    
    expect(result.current.selectedEntityId).toBe('DWP1');
    expect(result.current.history).toEqual(['DWP1']);
  });

  it('handles navigation through topology history', () => {
    const { result } = renderHook(() => useSelectionStore());
    
    act(() => {
      result.current.setSelectedEntityId('DWP1');
      result.current.pushSelection('WWTP1');
      result.current.pushSelection('LIEVE_RIVER');
      result.current.jumpToHistoryStep(1); // Jump to WWTP1
    });
    
    expect(result.current.topologyAnchorId).toBe('WWTP1');
    expect(result.current.topologyHistory).toEqual(['DWP1', 'WWTP1']);
  });
});
```

### API Mocking with MSW (Recommended)

**Setup Location**: `frontend-react/src/test/mocks/`

```typescript
// frontend-react/src/test/mocks/handlers.ts

import { http, HttpResponse } from 'msw';

export const handlers = [
  // Mock entities endpoint
  http.get('/api/v1/ontology/entities', () => {
    return HttpResponse.json({
      entities: [
        {
          id: 'DWP1',
          label: 'Drinking Water Plant 1',
          type: 'DrinkingWaterPlant',
          lat: 51.05,
          lon: 3.72,
          capacity: 2000
        },
        // ... more entities
      ]
    });
  }),

  // Mock SPARQL endpoint
  http.post('/api/v1/query/sparql', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({
      results: {
        bindings: [
          { entity: { value: 'DWP1', type: 'uri' } }
        ]
      },
      query_time_ms: 45.2
    });
  }),

  // Mock simulation endpoint
  http.post('/api/v1/simulation/run', async ({ request }) => {
    return HttpResponse.json({
      simulation_id: 'sim-123',
      status: 'completed',
      results: {
        // ... simulation results
      }
    });
  })
];

// frontend-react/src/test/mocks/server.ts

import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);

// frontend-react/src/test/setup.ts (update)

import '@testing-library/jest-dom';
import { expect, afterEach, beforeAll, afterAll } from 'vitest';
import { cleanup } from '@testing-library/react';
import { server } from './mocks/server';

// Establish API mocking before all tests
beforeAll(() => server.listen());

// Reset handlers after each test
afterEach(() => {
  cleanup();
  server.resetHandlers();
});

// Clean up after all tests
afterAll(() => server.close());
```

### Coverage Targets (Frontend)

- **Components**: >85% coverage
- **Custom Hooks**: >90% coverage
- **State Management**: >95% coverage
- **API Client**: >90% coverage
- **Utilities**: 100% coverage

---

## Integration Testing

### Backend-Frontend Integration Tests

**Location**: `tests/e2e/`

**Scope**: Test complete workflows across frontend and backend.

**Approach**: Use Playwright or Cypress for browser automation.

```typescript
// tests/e2e/query-workflow.spec.ts (Playwright example)

import { test, expect } from '@playwright/test';

test.describe('Query Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  test('user can execute SPARQL query', async ({ page }) => {
    // Navigate to query page
    await page.click('text=Query');
    
    // Enter SPARQL query
    await page.fill('[data-testid="sparql-input"]', 
      'SELECT ?s WHERE { ?s ?p ?o } LIMIT 10'
    );
    
    // Execute query
    await page.click('[data-testid="execute-query"]');
    
    // Wait for results
    await page.waitForSelector('[data-testid="query-results"]');
    
    // Verify results displayed
    const results = await page.locator('[data-testid="result-row"]').count();
    expect(results).toBeGreaterThan(0);
  });

  test('user can execute natural language query', async ({ page }) => {
    await page.click('text=Query');
    
    // Switch to natural language mode
    await page.click('[data-testid="nl-query-tab"]');
    
    // Enter question
    await page.fill('[data-testid="nl-input"]', 
      'What are the drinking water plants?'
    );
    
    // Submit query
    await page.click('[data-testid="submit-nl-query"]');
    
    // Wait for translation and results
    await page.waitForSelector('[data-testid="generated-sparql"]');
    await page.waitForSelector('[data-testid="query-results"]');
    
    // Verify SPARQL was generated
    const sparql = await page.locator('[data-testid="generated-sparql"]').textContent();
    expect(sparql).toContain('SELECT');
  });

  test('user can view entity details from query results', async ({ page }) => {
    await page.click('text=Query');
    
    // Execute query
    await page.fill('[data-testid="sparql-input"]', 
      'SELECT ?entity WHERE { ?entity a wf:DrinkingWaterPlant }'
    );
    await page.click('[data-testid="execute-query"]');
    
    // Click on result to view details
    await page.click('[data-testid="result-row"]:first-child');
    
    // Verify entity details displayed
    await page.waitForSelector('[data-testid="entity-details"]');
    expect(await page.locator('[data-testid="entity-label"]').textContent())
      .toBeTruthy();
  });
});
```

### Service Integration Tests

**Location**: `tests/integration/`

Test interactions between orchestrator and model services.

```python
# tests/integration/test_model_service_integration.py

import pytest
import httpx
from ghent_water.orchestrator.services.model_registry import registry

@pytest.mark.integration
@pytest.mark.asyncio
async def test_model_service_discovery():
    """Test discovering and registering model services."""
    async with httpx.AsyncClient() as client:
        # Try to reach a model service
        try:
            response = await client.get("http://localhost:8001/describe", timeout=5.0)
            if response.status_code == 200:
                description = response.json()
                assert "@graph" in description
                assert len(description["@graph"]) > 0
        except httpx.ConnectError:
            pytest.skip("Model service not running on port 8001")

@pytest.mark.integration
@pytest.mark.asyncio
async def test_simulation_execution_with_model():
    """Test executing simulation through orchestrator to model service."""
    from fastapi.testclient import TestClient
    from ghent_water.orchestrator.main import app
    
    client = TestClient(app)
    
    # Check if any models registered
    models_response = client.get("/api/v1/discovery/models")
    models = models_response.json()["models"]
    
    if len(models) == 0:
        pytest.skip("No model services available")
    
    # Run simulation
    simulation_request = {
        "entity_ids": [models[0]["entities"][0]],
        "scenario": {
            "duration": 3600,
            "timestep": 60
        },
        "parameters": {
            "initial_flow": 100
        }
    }
    
    response = client.post("/api/v1/simulation/run", json=simulation_request)
    assert response.status_code in [200, 202]  # Success or accepted
```

---

## End-to-End Testing

### E2E Testing Strategy

**Tool**: Playwright (recommended) or Cypress

**Location**: `tests/e2e/` or `frontend-react/e2e/`

**Setup**:

```bash
# Install Playwright
npm install -D @playwright/test

# Initialize Playwright
npx playwright install
```

**Configuration**:

```typescript
// playwright.config.ts

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

**E2E Test Scenarios**:

1. **User Journey: Exploring Water System**
   - Load application
   - View map with all entities
   - Select entity from map
   - View entity details and sensors
   - Navigate topology graph

2. **User Journey: Running Queries**
   - Execute SPARQL query
   - Execute natural language query
   - View and export results

3. **User Journey: Running Simulation**
   - Select entities for simulation
   - Configure simulation parameters
   - Execute simulation
   - View results and charts

4. **Real-time Data Visualization**
   - Connect to WebSocket
   - Verify sensor data updates
   - Check chart updates

---

## Test Organization

### Directory Structure

```
/Users/jeandavidt/Developer/jeandavidt/ontEAUlogy/case_studies/ghent/
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # Shared fixtures
│   ├── pytest.ini                     # pytest configuration
│   │
│   ├── unit/                          # Backend unit tests
│   │   ├── __init__.py
│   │   ├── orchestrator/
│   │   │   ├── __init__.py
│   │   │   ├── routers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── test_query_router.py
│   │   │   │   ├── test_ontology_router.py
│   │   │   │   ├── test_simulation_router.py
│   │   │   │   ├── test_discovery_router.py
│   │   │   │   ├── test_sensor_router.py
│   │   │   │   └── test_websocket_router.py
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── test_ontology_store.py
│   │   │   │   ├── test_sparql_engine.py
│   │   │   │   ├── test_llm_sparql.py
│   │   │   │   ├── test_sensor_generator.py
│   │   │   │   ├── test_model_registry.py
│   │   │   │   └── test_sensor_config.py
│   │   │   └── schemas/
│   │   │       ├── __init__.py
│   │   │       └── test_models.py
│   │   └── models/
│   │       └── # Model-specific tests
│   │
│   ├── integration/                   # Integration tests
│   │   ├── __init__.py
│   │   ├── test_query_router_integration.py
│   │   ├── test_simulation_integration.py
│   │   ├── test_ontology_loading_integration.py
│   │   ├── test_sensor_streaming_integration.py
│   │   └── test_model_service_integration.py
│   │
│   └── e2e/                           # End-to-end tests
│       ├── test_user_journey.py
│       ├── test_query_workflow.spec.ts
│       ├── test_simulation_workflow.spec.ts
│       └── fixtures/
│
├── frontend-react/
│   ├── src/
│   │   ├── api/
│   │   │   └── __tests__/
│   │   │       ├── queries.test.ts
│   │   │       ├── client.test.ts
│   │   │       └── webSocket.test.ts
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── EntityDetails.test.tsx
│   │   │   │   ├── SPARQLSection.test.tsx
│   │   │   │   └── SensorVisualizer.test.tsx
│   │   │   ├── map/
│   │   │   │   └── WaterMap.test.tsx
│   │   │   ├── topology/
│   │   │   │   ├── WaterTopology.test.tsx
│   │   │   │   └── Breadcrumbs.test.tsx
│   │   │   ├── simulation/
│   │   │   │   └── SimulationForm.test.tsx
│   │   │   └── results/
│   │   │       └── SimulationCharts.test.tsx
│   │   ├── stores/
│   │   │   └── __tests__/
│   │   │       └── useSelectionStore.test.ts
│   │   ├── utils/
│   │   │   └── __tests__/
│   │   │       └── # Utility function tests
│   │   └── test/
│   │       ├── setup.ts
│   │       └── mocks/
│   │           ├── handlers.ts
│   │           └── server.ts
│   │
│   └── vitest.config.ts
│
├── playwright.config.ts               # E2E test configuration
└── TESTING_STRATEGY.md               # This document
```

### Naming Conventions

**Backend (Python)**:
- Unit test files: `test_<module_name>.py`
- Integration test files: `test_<feature>_integration.py`
- Test functions: `test_<what_is_being_tested>`
- Test classes: `Test<ClassName>` (if grouping related tests)

**Frontend (TypeScript)**:
- Unit test files: `<ComponentName>.test.tsx` or `<moduleName>.test.ts`
- Test descriptions: `describe('<ComponentName>', () => { ... })`
- Test cases: `it('should <expected behavior>', () => { ... })`

### Test Markers (pytest)

Use markers to categorize and selectively run tests:

```python
# pytest.ini

[pytest]
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (slower, may require services)
    e2e: End-to-end tests (slowest, full system)
    slow: Slow-running tests
    requires_llm: Tests requiring LLM service
    requires_models: Tests requiring model services running
```

**Usage**:

```bash
# Run only unit tests
pytest -m unit

# Run unit and integration tests
pytest -m "unit or integration"

# Skip slow tests
pytest -m "not slow"

# Run tests requiring LLM
pytest -m requires_llm
```

---

## Coverage Goals and Metrics

### Target Coverage Levels

| Test Type | Coverage Target | Priority |
|-----------|----------------|----------|
| Backend Services | >95% | Critical |
| Backend Routers | >90% | Critical |
| Backend Schemas | >95% | High |
| Frontend Components | >85% | High |
| Frontend Hooks | >90% | High |
| Frontend Stores | >95% | Critical |
| Integration Tests | Key workflows 100% | Critical |
| E2E Tests | Critical paths 100% | High |

### Coverage Collection

**Backend Coverage**:

```bash
# Run tests with coverage
pytest --cov=src/ghent_water/orchestrator --cov-report=html --cov-report=term

# Generate coverage report
pytest --cov=src/ghent_water/orchestrator --cov-report=html
# View report at htmlcov/index.html

# Check coverage threshold
pytest --cov=src/ghent_water/orchestrator --cov-fail-under=90
```

**Frontend Coverage**:

```bash
# Run tests with coverage
npm run test:coverage

# View coverage report
# Opens coverage/index.html
```

### Coverage Configuration

**Backend (`.coveragerc` or `pyproject.toml`)**:

```toml
# pyproject.toml

[tool.coverage.run]
source = ["src/ghent_water/orchestrator"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__pycache__/*",
    "*/venv/*",
]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false

exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]

[tool.coverage.html]
directory = "htmlcov"
```

**Frontend (vite.config.ts)**:

```typescript
// Already configured in vite.config.ts

test: {
  globals: true,
  environment: 'jsdom',
  setupFiles: './src/test/setup.ts',
  coverage: {
    provider: 'v8',
    reporter: ['text', 'json', 'html'],
    exclude: [
      'node_modules/',
      'src/test/',
      '**/*.test.ts',
      '**/*.test.tsx',
      '**/*.spec.ts',
      '**/*.spec.tsx',
    ],
    thresholds: {
      lines: 85,
      functions: 85,
      branches: 80,
      statements: 85,
    },
  },
},
```

### Monitoring Coverage Over Time

**Track Coverage in CI**:
- Store coverage reports as artifacts
- Display coverage badges in README
- Set minimum coverage thresholds
- Fail builds if coverage drops below threshold

**Coverage Tracking Tools**:
- Codecov (recommended)
- Coveralls
- SonarQube

---

## CI/CD Integration

### GitHub Actions Workflow Example

```yaml
# .github/workflows/test.yml

name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      # Add any required services (e.g., database, Redis)
      
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev,test]"
      
      - name: Run unit tests
        run: |
          pytest tests/unit -v --cov=src/ghent_water/orchestrator --cov-report=xml
      
      - name: Run integration tests
        run: |
          pytest tests/integration -v
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: backend
          name: backend-coverage

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend-react/package-lock.json
      
      - name: Install dependencies
        working-directory: ./frontend-react
        run: npm ci
      
      - name: Run unit tests
        working-directory: ./frontend-react
        run: npm run test:run
      
      - name: Run coverage
        working-directory: ./frontend-react
        run: npm run test:coverage
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./frontend-react/coverage/coverage-final.json
          flags: frontend
          name: frontend-coverage

  e2e-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
          cd frontend-react && npm ci
          npx playwright install --with-deps
      
      - name: Start backend
        run: |
          uvicorn ghent_water.orchestrator.main:app --host 0.0.0.0 --port 8080 &
          sleep 10
      
      - name: Start frontend
        working-directory: ./frontend-react
        run: |
          npm run dev &
          sleep 10
      
      - name: Run E2E tests
        run: npx playwright test
      
      - name: Upload Playwright report
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 30

  coverage-check:
    needs: [backend-tests, frontend-tests]
    runs-on: ubuntu-latest
    
    steps:
      - name: Check coverage thresholds
        run: |
          # Download coverage reports and verify thresholds
          echo "Coverage check passed"
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml

repos:
  - repo: local
    hooks:
      - id: pytest-unit
        name: Run unit tests
        entry: pytest tests/unit -v
        language: system
        pass_filenames: false
        always_run: true
      
      - id: frontend-tests
        name: Run frontend tests
        entry: bash -c 'cd frontend-react && npm run test:run'
        language: system
        pass_filenames: false
        always_run: true
```

### Docker-based Testing

```dockerfile
# Dockerfile.test

FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./
RUN pip install -e ".[dev,test]"

COPY src/ ./src/
COPY tests/ ./tests/

CMD ["pytest", "-v", "--cov=src/ghent_water/orchestrator"]
```

```bash
# Run tests in Docker
docker build -f Dockerfile.test -t ghent-water-tests .
docker run --rm ghent-water-tests
```

---

## Maintenance Guidelines

### Adding Tests for New Features

**When adding a new backend router endpoint**:

1. Create unit test in `tests/unit/orchestrator/routers/test_<router>.py`
2. Test success case, error cases, and edge cases
3. Mock all service dependencies
4. Add integration test if endpoint interacts with multiple services
5. Update E2E tests if user-facing feature

**Example Checklist**:
```python
# New endpoint: GET /api/v1/ontology/entities/{id}/connections

# tests/unit/orchestrator/routers/test_ontology_router.py
def test_get_entity_connections_success(client, mock_ontology_store):
    """Test successful retrieval of entity connections."""
    # ... test implementation

def test_get_entity_connections_not_found(client, mock_ontology_store):
    """Test 404 when entity doesn't exist."""
    # ... test implementation

def test_get_entity_connections_invalid_id(client):
    """Test 400 when entity ID is invalid."""
    # ... test implementation

# tests/integration/test_ontology_integration.py
def test_entity_connections_with_real_graph():
    """Test connection retrieval against real ontology."""
    # ... test implementation
```

**When adding a new frontend component**:

1. Create `<ComponentName>.test.tsx` next to component file
2. Test rendering, props, user interactions, edge cases
3. Mock API calls with MSW or manual mocks
4. Test accessibility (aria labels, keyboard navigation)
5. Update E2E tests if part of critical user journey

**Example Checklist**:
```typescript
// New component: ConnectionsGraph.tsx

// ConnectionsGraph.test.tsx
describe('ConnectionsGraph', () => {
  it('renders connections correctly', () => { ... });
  it('handles empty connections gracefully', () => { ... });
  it('allows node selection', () => { ... });
  it('displays loading state', () => { ... });
  it('displays error state', () => { ... });
  it('is keyboard accessible', () => { ... });
});
```

### Refactoring Tests

**When refactoring code that breaks tests**:

1. Update test expectations, not just to make them pass
2. Ensure test still validates original requirements
3. Add tests for new behavior introduced by refactor
4. Verify coverage hasn't decreased

**When refactoring tests themselves**:

1. Extract common setup into fixtures/helper functions
2. Use parameterized tests for similar test cases
3. Consolidate redundant tests
4. Improve test names for clarity

### Test Data Management

**Backend Test Data**:
- Store sample RDF/Turtle files in `tests/fixtures/ontology/`
- Use `pytest.fixture` for reusable test graphs
- Keep test data minimal but representative

**Frontend Test Data**:
- Define mock data in `src/api/mockData.ts` (already exists)
- Use MSW handlers in `src/test/mocks/handlers.ts`
- Keep mock responses realistic

### Handling Flaky Tests

**Common causes**:
- Timing issues (async operations)
- Shared state between tests
- External dependencies
- Random data generation

**Solutions**:
```python
# Use deterministic fixtures
@pytest.fixture
def fixed_random_seed():
    random.seed(42)
    yield
    random.seed(None)

# Add retries for integration tests
@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_external_api_integration():
    # ... test that may occasionally fail due to network
```

```typescript
// Use fake timers in frontend tests
import { vi } from 'vitest';

it('debounces input', () => {
  vi.useFakeTimers();
  
  // ... test with controlled time
  
  vi.runAllTimers();
  vi.useRealTimers();
});
```

### Test Documentation

**Document test purpose**:
```python
def test_sparql_query_with_complex_filter():
    """Test SPARQL execution with nested FILTER clauses.
    
    This test verifies that the engine correctly handles:
    - Multiple FILTER conditions
    - Nested logical operators (AND, OR, NOT)
    - Type casting in filters
    
    Regression test for issue #123.
    """
```

**Document test data**:
```python
@pytest.fixture
def complex_water_network():
    """Create a realistic water network graph for testing.
    
    Network structure:
        DWP1 -> Pipe1 -> Residential1
        DWP1 -> Pipe2 -> Residential2
        Residential1 -> Sewer1 -> WWTP1
        Residential2 -> Sewer2 -> WWTP1
        WWTP1 -> Outfall -> River
    
    Includes 2 DWPs, 2 residential zones, 1 WWTP, 1 river segment.
    Total entities: 8, Total connections: 7
    """
```

---

## Best Practices

### General Testing Principles

1. **Arrange-Act-Assert Pattern**
   ```python
   def test_feature():
       # Arrange: Set up test data and mocks
       entity = create_test_entity()
       
       # Act: Execute the code being tested
       result = process_entity(entity)
       
       # Assert: Verify expected outcome
       assert result.status == "success"
   ```

2. **Test One Thing Per Test**
   - Each test should validate a single behavior
   - Makes failures easier to diagnose
   - Improves test maintainability

3. **Use Descriptive Test Names**
   ```python
   # Good
   def test_query_returns_400_when_syntax_invalid():
       pass
   
   # Bad
   def test_query():
       pass
   ```

4. **Keep Tests Independent**
   - Tests should not depend on execution order
   - Each test should set up its own state
   - Clean up after each test

5. **Mock External Dependencies**
   - Don't make real API calls in unit tests
   - Mock file system operations
   - Mock random number generators for deterministic tests

### Backend-Specific Practices

1. **Use FastAPI TestClient for Router Tests**
   ```python
   from fastapi.testclient import TestClient
   from ghent_water.orchestrator.main import app
   
   client = TestClient(app)
   response = client.get("/api/v1/ontology/entities")
   ```

2. **Test Async Code Properly**
   ```python
   @pytest.mark.asyncio
   async def test_async_function():
       result = await async_operation()
       assert result is not None
   ```

3. **Use Fixtures for Complex Setup**
   ```python
   @pytest.fixture
   def configured_engine(sample_graph):
       engine = SparqlEngine(sample_graph)
       engine.set_timeout(30)
       return engine
   ```

4. **Test Both Success and Failure Paths**
   ```python
   def test_query_success():
       # Test successful query execution
       pass
   
   def test_query_invalid_syntax():
       # Test handling of invalid SPARQL
       pass
   
   def test_query_timeout():
       # Test timeout handling
       pass
   ```

### Frontend-Specific Practices

1. **Use Testing Library Queries Effectively**
   ```typescript
   // Prefer accessible queries
   screen.getByRole('button', { name: /submit/i })
   screen.getByLabelText(/email/i)
   
   // Avoid implementation details
   // Bad: screen.getByClassName('submit-button')
   ```

2. **Test User Interactions**
   ```typescript
   import { userEvent } from '@testing-library/user-event';
   
   it('submits form on button click', async () => {
     const user = userEvent.setup();
     render(<SimulationForm />);
     
     await user.type(screen.getByLabelText(/duration/i), '3600');
     await user.click(screen.getByRole('button', { name: /run/i }));
     
     expect(screen.getByText(/simulation started/i)).toBeInTheDocument();
   });
   ```

3. **Wait for Async Updates**
   ```typescript
   it('displays query results', async () => {
     render(<QueryResults />);
     
     // Wait for data to load
     await waitFor(() => {
       expect(screen.getByText(/dwp1/i)).toBeInTheDocument();
     });
   });
   ```

4. **Test Accessibility**
   ```typescript
   it('is keyboard navigable', async () => {
     const user = userEvent.setup();
     render(<NavigableComponent />);
     
     await user.tab(); // Focus first element
     expect(screen.getByRole('button')).toHaveFocus();
   });
   ```

### Test Performance

1. **Keep Unit Tests Fast**
   - Target: <1 second per unit test
   - Use mocks to avoid slow operations
   - Avoid unnecessary database/file operations

2. **Optimize Test Setup**
   ```python
   # Use session-scoped fixtures for expensive setup
   @pytest.fixture(scope="session")
   def loaded_ontology():
       ontology = load_full_ontology()  # Slow operation
       return ontology
   ```

3. **Run Tests in Parallel**
   ```bash
   # Backend
   pytest -n auto  # Requires pytest-xdist
   
   # Frontend
   vitest --threads  # Vitest runs in parallel by default
   ```

4. **Use Test Markers to Skip Slow Tests**
   ```python
   @pytest.mark.slow
   def test_full_system_simulation():
       # Long-running test
       pass
   ```

### Continuous Improvement

1. **Regular Test Reviews**
   - Review tests during code reviews
   - Refactor tests as code evolves
   - Remove obsolete tests

2. **Monitor Test Metrics**
   - Track test execution time
   - Monitor flaky test rate
   - Track coverage trends

3. **Update Documentation**
   - Keep this strategy document current
   - Document new testing patterns
   - Share learnings with team

4. **Invest in Test Infrastructure**
   - Improve test fixtures
   - Build test utilities
   - Maintain CI/CD pipeline

---

## Appendix

### Useful Commands

**Backend Testing**:
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/orchestrator/services/test_sparql_engine.py

# Run specific test
pytest tests/unit/orchestrator/services/test_sparql_engine.py::test_execute_simple_select_query

# Run tests matching pattern
pytest -k "sparql"

# Run with coverage
pytest --cov=src/ghent_water/orchestrator --cov-report=html

# Run with verbose output
pytest -v

# Run and show print statements
pytest -s

# Run in parallel
pytest -n auto

# Run only marked tests
pytest -m unit
pytest -m "unit and not slow"
```

**Frontend Testing**:
```bash
# Run all tests
npm run test

# Run tests in watch mode
npm run test

# Run tests once (CI mode)
npm run test:run

# Run with UI
npm run test:ui

# Run with coverage
npm run test:coverage

# Run specific test file
npm run test -- EntityDetails.test.tsx

# Run tests matching pattern
npm run test -- -t "renders entity"
```

**E2E Testing (Playwright)**:
```bash
# Run all E2E tests
npx playwright test

# Run specific test file
npx playwright test query-workflow.spec.ts

# Run in headed mode (see browser)
npx playwright test --headed

# Run in debug mode
npx playwright test --debug

# Generate code from actions
npx playwright codegen http://localhost:3000

# Show test report
npx playwright show-report
```

### Resources

**Backend Testing**:
- [pytest documentation](https://docs.pytest.org/)
- [FastAPI testing guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [RDFLib testing examples](https://rdflib.readthedocs.io/)

**Frontend Testing**:
- [Vitest documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Testing Library queries](https://testing-library.com/docs/queries/about)
- [MSW (Mock Service Worker)](https://mswjs.io/)

**E2E Testing**:
- [Playwright documentation](https://playwright.dev/)
- [Playwright best practices](https://playwright.dev/docs/best-practices)

**General Testing**:
- [Test Driven Development (TDD)](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
- [Testing Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2024-01-23 | 1.0 | Initial testing strategy document |

---

## Maintenance

This document should be reviewed and updated:
- When new testing patterns are introduced
- When testing tools are upgraded
- When new services or features are added
- Quarterly as part of technical debt review

**Document Owner**: QA/Development Team
**Last Review**: 2024-01-23
**Next Review**: 2024-04-23
