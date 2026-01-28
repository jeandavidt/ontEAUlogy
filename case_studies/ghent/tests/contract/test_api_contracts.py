"""Contract tests for API endpoints to ensure response shapes remain consistent."""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
import json
from typing import Dict, Any, List

from src.ghent_water.orchestrator.main import app
from src.ghent_water.orchestrator.schemas.models import (
    OntologyInfo,
    EntityTriplesResponse,
    SparqlQueryResponse,
    NaturalLanguageQueryResponse,
    SimulationResponse,
    JobResponse,
    ValidationResponse,
)


class TestAPIContracts:
    """Test contract compliance for critical API endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    @pytest.fixture
    async def async_client(self):
        """Create an async test client."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac

    def test_ontology_info_contract(self, client):
        """Test /api/v1/ontology/ returns correct shape."""
        response = client.get("/api/v1/ontology/")

        assert response.status_code == 200
        data = response.json()

        # Validate required fields
        required_fields = ["graph_size", "namespaces", "entities_count"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # Validate field types
        assert isinstance(data["graph_size"], int)
        assert isinstance(data["namespaces"], list)
        assert isinstance(data["entities_count"], dict)

        # Validate Pydantic model can deserialize
        ontology_info = OntologyInfo(**data)
        assert ontology_info.graph_size >= 0

    def test_ontology_entities_contract(self, client):
        """Test /api/v1/ontology/entities returns correct shape."""
        response = client.get("/api/v1/ontology/entities")

        assert response.status_code == 200
        data = response.json()

        # Validate required fields
        required_fields = ["entities", "count"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # Validate field types
        assert isinstance(data["entities"], list)
        assert isinstance(data["count"], int)
        assert data["count"] >= 0

        # Validate entity structure if any entities exist
        if data["entities"]:
            entity = data["entities"][0]
            entity_required_fields = [
                "uri",
                "id",
                "label",
                "type",
                "raw_type",
                "description",
                "lat",
                "lon",
                "zone",
                "capacity",
                "population",
                "observes",
                "monitorsPort",
                "attachedTo",
            ]
            for field in entity_required_fields:
                assert field in entity, f"Missing entity field: {field}"

            # Validate types
            assert isinstance(entity["uri"], str)
            assert isinstance(entity["id"], str)
            assert isinstance(entity["label"], str)
            assert isinstance(entity["type"], str)
            assert isinstance(entity["lat"], (int, float))
            assert isinstance(entity["lon"], (int, float))

    def test_ontology_entity_by_id_contract(self, client):
        """Test /api/v1/ontology/entities/{entity_id} returns correct shape."""
        # Get a list of entities first to find a valid ID
        entities_response = client.get("/api/v1/ontology/entities")
        entities_data = entities_response.json()

        if entities_data["entities"]:
            entity_id = entities_data["entities"][0]["id"]
            response = client.get(f"/api/v1/ontology/entities/{entity_id}")

            assert response.status_code == 200
            data = response.json()

            # Validate entity structure
            entity_required_fields = [
                "uri",
                "id",
                "label",
                "type",
                "raw_type",
                "description",
                "lat",
                "lon",
                "zone",
                "capacity",
                "population",
                "observes",
                "monitorsPort",
                "attachedTo",
            ]
            for field in entity_required_fields:
                assert field in data, f"Missing entity field: {field}"

    def test_sparql_query_contract(self, client):
        """Test /api/v1/query/sparql returns standard SPARQL JSON format."""
        sparql_request = {
            "query": """
                SELECT ?entity ?label WHERE {
                    ?entity a ?type ;
                           rdfs:label ?label .
                    FILTER(STRSTARTS(STR(?entity), "https://w3id.org/waterframe/case/ghent/"))
                } LIMIT 5
            """,
            "format": "json",
        }

        response = client.post("/api/v1/query/sparql", json=sparql_request)

        assert response.status_code == 200
        data = response.json()

        # Validate required fields
        required_fields = ["head", "results", "format", "query_time_ms"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # Validate field types
        assert isinstance(data["head"], dict)
        assert isinstance(data["results"], dict)
        assert isinstance(data["format"], str)
        assert isinstance(data["query_time_ms"], (int, float))
        assert data["query_time_ms"] >= 0

        # Validate SPARQL results structure
        if "bindings" in data["results"]:
            assert isinstance(data["results"]["bindings"], list)

            # Validate binding structure if any bindings exist
            if data["results"]["bindings"]:
                binding = data["results"]["bindings"][0]
                for var_name, var_data in binding.items():
                    assert "value" in var_data
                    assert isinstance(var_data["value"], str)
                    if "type" in var_data:
                        assert isinstance(var_data["type"], str)

        # Validate Pydantic model can deserialize
        sparql_response = SparqlQueryResponse(**data)

    def test_natural_language_query_contract(self, client):
        """Test /api/v1/query/natural returns correct shape."""
        nl_request = {
            "question": "What entities exist in the ontology?",
            "target_format": "results",
        }

        response = client.post("/api/v1/query/natural", json=nl_request)

        # This might fail if LLM is not configured, but response shape should be consistent
        assert response.status_code in [200, 400, 500]
        data = response.json()

        if response.status_code == 200:
            # Validate successful response structure
            required_fields = [
                "original_question",
                "generated_sparql",
                "results",
                "execution_plan",
                "simulation_required",
                "suggested_models",
            ]
            for field in required_fields:
                assert field in data, f"Missing field: {field}"

            # Validate field types
            assert isinstance(data["original_question"], str)
            assert isinstance(data["simulation_required"], bool)
            assert isinstance(data["suggested_models"], list)

            # Validate Pydantic model can deserialize
            nl_response = NaturalLanguageQueryResponse(**data)

    def test_simulation_models_list_contract(self, client):
        """Test /api/v1/simulation/models returns correct shape."""
        response = client.get("/api/v1/simulation/models")

        assert response.status_code == 200
        data = response.json()

        # Validate required fields
        required_fields = ["models", "count"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # Validate field types
        assert isinstance(data["models"], list)
        assert isinstance(data["count"], int)
        assert data["count"] >= 0

        # Validate model structure if any models exist
        if data["models"]:
            model = data["models"][0]
            model_required_fields = [
                "id",
                "name",
                "description",
                "endpoint",
                "capabilities",
                "entities",
                "registered_at",
            ]
            for field in model_required_fields:
                assert field in model, f"Missing model field: {field}"

    def test_simulation_run_contract(self, client):
        """Test /api/v1/simulation/models/{id}/run returns correct shape."""
        # First get available models
        models_response = client.get("/api/v1/simulation/models")
        models_data = models_response.json()

        if models_data["models"]:
            model_id = models_data["models"][0]["id"]
            simulation_request = {
                "entity_ids": [],
                "scenario": {},
                "parameters": {},
                "wait_for_result": False,  # Don't wait for actual results
                "timeout_seconds": 10,
            }

            response = client.post(
                f"/api/v1/simulation/models/{model_id}/run", json=simulation_request
            )

            # Should return job submission response
            assert response.status_code == 200
            data = response.json()

            # Validate job response structure
            required_fields = ["job_id", "model_id", "status", "message"]
            for field in required_fields:
                assert field in data, f"Missing field: {field}"

            # Validate field types
            assert isinstance(data["job_id"], str)
            assert isinstance(data["model_id"], str)
            assert isinstance(data["status"], str)
            assert isinstance(data["message"], str)

            # Validate Pydantic model can deserialize
            job_response = JobResponse(**data)

    def test_ontology_validation_contract(self, client):
        """Test /api/v1/ontology/validate returns correct shape."""
        validation_request = {
            "data_graph": "PREFIX ex: <http://example.org/> ex:Test ex:name 'test'."
        }

        response = client.post("/api/v1/ontology/validate", json=validation_request)

        assert response.status_code == 200
        data = response.json()

        # Validate required fields
        required_fields = ["conforms", "results"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # Validate field types
        assert isinstance(data["conforms"], bool)
        assert isinstance(data["results"], list)

        # Validate Pydantic model can deserialize
        validation_response = ValidationResponse(**data)

    def test_error_response_consistency(self, client):
        """Test that error responses have consistent shape."""
        # Test with invalid entity ID
        response = client.get("/api/v1/ontology/entities/nonexistententity")

        assert response.status_code == 404
        data = response.json()

        # Error responses should have 'detail' field (FastAPI default)
        assert "detail" in data
        assert isinstance(data["detail"], str)

        # Test with invalid SPARQL query
        invalid_sparql = {"query": "INVALID SPARQL QUERY", "format": "json"}

        response = client.post("/api/v1/query/sparql", json=invalid_sparql)
        assert response.status_code in [400, 422]
        data = response.json()
        assert "detail" in data


class TestSchemaRegression:
    """Test that Pydantic models can deserialize actual API responses."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    def test_ontology_info_model_deserialization(self, client):
        """Test OntologyInfo model can deserialize actual response."""
        response = client.get("/api/v1/ontology/")
        assert response.status_code == 200

        # Should not raise an exception
        ontology_info = OntologyInfo(**response.json())
        assert isinstance(ontology_info.graph_size, int)

    def test_entity_triples_response_model_deserialization(self, client):
        """Test EntityTriplesResponse model can deserialize actual response."""
        # Get a valid entity first
        entities_response = client.get("/api/v1/ontology/entities")
        entities_data = entities_response.json()

        if entities_data["entities"]:
            entity_id = entities_data["entities"][0]["id"]
            response = client.get(f"/api/v1/ontology/entities/{entity_id}/triplets")
            assert response.status_code == 200

            # Should not raise an exception
            entity_triples = EntityTriplesResponse(**response.json())
            assert isinstance(entity_triples.uri, str)
            assert isinstance(entity_triples.triples, list)

    def test_sparql_response_model_deserialization(self, client):
        """Test SparqlQueryResponse model can deserialize actual response."""
        sparql_request = {
            "query": "SELECT ?entity WHERE { ?entity a ?type } LIMIT 1",
            "format": "json",
        }

        response = client.post("/api/v1/query/sparql", json=sparql_request)
        assert response.status_code == 200

        # Should not raise an exception
        sparql_response = SparqlQueryResponse(**response.json())
        assert isinstance(sparql_response.format, str)
        assert isinstance(sparql_response.query_time_ms, (int, float))

    def test_validation_response_model_deserialization(self, client):
        """Test ValidationResponse model can deserialize actual response."""
        validation_request = {
            "data_graph": "PREFIX ex: <http://example.org/> ex:Test ex:name 'test'."
        }

        response = client.post("/api/v1/ontology/validate", json=validation_request)
        assert response.status_code == 200

        # Should not raise an exception
        validation_response = ValidationResponse(**response.json())
        assert isinstance(validation_response.conforms, bool)
        assert isinstance(validation_response.results, list)


@pytest.mark.asyncio
class TestAsyncContractTests:
    """Async contract tests for endpoints that might need async handling."""

    async def test_async_client_setup(self):
        """Test async client setup works."""
        from httpx import ASGITransport

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.get("/api/v1/ontology/")
            assert response.status_code == 200
            data = response.json()
            assert "graph_size" in data
