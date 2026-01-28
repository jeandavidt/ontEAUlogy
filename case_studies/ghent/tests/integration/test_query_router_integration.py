"""Integration tests for the query router."""

import pytest
from fastapi.testclient import TestClient
from ghent_water.orchestrator.main import app

def test_execute_sparql_query_endpoint():
    """Test the /sparql endpoint with a simple query."""
    client = TestClient(app)
    
    # Simple query to list types (should work against loaded ontology)
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT DISTINCT ?type WHERE { ?s a ?type } LIMIT 1
    """
    
    response = client.post(
        "/api/v1/query/sparql",
        json={"query": query, "format": "json"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "bindings" in data["results"]
    assert "query_time_ms" in data

def test_execute_sparql_query_invalid_syntax():
    """Test the /sparql endpoint with invalid query string."""
    client = TestClient(app)
    
    response = client.post(
        "/api/v1/query/sparql",
        json={"query": "INVALID QUERY", "format": "json"}
    )
    
    assert response.status_code == 400
    assert "SPARQL execution failed" in response.json()["detail"]

def test_get_ontology_entities():
    """Test the /ontology/entities endpoint."""
    client = TestClient(app)
    
    response = client.get("/api/v1/ontology/entities")
    
    assert response.status_code == 200
    data = response.json()
    assert "entities" in data
    assert len(data["entities"]) > 0
    
    # Check for specific Ghent entity fields
    entity = data["entities"][0]
    assert "id" in entity
    assert "type" in entity
    assert "uri" in entity
