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
            "results": {
                "bindings": [
                    {"entity": {"type": "uri", "value": "http://example.org/DWP1"}}
                ]
            },
            "format": "json",
            "query_time_ms": 45.2,
        }
        yield mock


def test_sparql_endpoint_success(client, mock_sparql_engine):
    """Test successful SPARQL query execution."""
    query = "SELECT ?s WHERE { ?s ?p ?o } LIMIT 10"

    response = client.post(
        "/api/v1/query/sparql", json={"query": query, "format": "json"}
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
        "/api/v1/query/sparql", json={"query": long_query, "format": "json"}
    )

    assert response.status_code == 400
    assert "too long" in response.json()["detail"].lower()


def test_sparql_endpoint_forbidden_operations(client):
    """Test rejection of write operations."""
    forbidden_queries = [
        "INSERT DATA { <http://example.org/s> <http://example.org/p> <http://example.org/o> }",
        "DELETE WHERE { ?s ?p ?o }",
        "DROP GRAPH <http://example.org/graph>",
    ]

    for query in forbidden_queries:
        response = client.post(
            "/api/v1/query/sparql", json={"query": query, "format": "json"}
        )
        assert response.status_code == 400
        assert "not allowed" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_natural_language_query_success(client):
    """Test natural language query endpoint."""
    with patch(
        "ghent_water.orchestrator.routers.query.get_llm_sparql_translator"
    ) as mock_translator:
        translator_instance = AsyncMock()
        translator_instance._initialized = True
        translator_instance.execute_query.return_value = {
            "generated_sparql": "SELECT ?dwp WHERE { ?dwp a wf:DrinkingWaterPlant }",
            "results": {"bindings": [{"dwp": {"value": "DWP1"}}]},
            "execution_plan": "Query successful",
        }
        mock_translator.return_value = translator_instance

        response = client.post(
            "/api/v1/query/natural",
            json={"question": "What are the drinking water plants?"},
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
        json={"query": "SELECT * WHERE { ?s ?p ?o }", "format": "json"},
    )

    assert response.status_code == 408
    assert "timeout" in response.json()["detail"].lower()
