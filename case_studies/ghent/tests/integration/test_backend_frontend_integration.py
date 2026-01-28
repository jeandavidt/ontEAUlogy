"""
Integration tests to verify backend-frontend communication.

These tests ensure that:
1. Backend endpoints return data in the format expected by frontend
2. Data transformations are compatible
3. Error handling works across the stack
"""

import pytest
from fastapi.testclient import TestClient
from ghent_water.orchestrator.main import app


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    return TestClient(app)


class TestFrontendBackendCommunication:
    """Tests verifying backend API matches frontend expectations."""

    def test_entities_endpoint_matches_frontend_format(self, client):
        """Verify /ontology/entities returns format expected by frontend useEntities hook."""
        response = client.get("/api/v1/ontology/entities")

        assert response.status_code == 200
        data = response.json()

        # Frontend expects: { entities: [...], count: number }
        assert "entities" in data
        assert "count" in data
        assert isinstance(data["entities"], list)
        assert isinstance(data["count"], int)

        if len(data["entities"]) > 0:
            entity = data["entities"][0]

            # Frontend expects these fields for useEntities transformation
            required_fields = ["id", "label", "type", "lat", "lon"]
            for field in required_fields:
                assert field in entity, f"Missing required field: {field}"

            # Verify data types
            assert isinstance(entity["id"], str)
            assert isinstance(entity["label"], str)
            assert isinstance(entity["type"], str)

            # Frontend transforms [lat, lon] to coordinates array
            # Backend should provide numeric lat/lon
            if entity["lat"]:
                lat = float(entity["lat"]) if isinstance(entity["lat"], str) else entity["lat"]
                lon = float(entity["lon"]) if isinstance(entity["lon"], str) else entity["lon"]
                assert isinstance(lat, (int, float))
                assert isinstance(lon, (int, float))

    def test_entity_triplets_endpoint_matches_frontend_format(self, client):
        """Verify entity triplets endpoint returns format expected by frontend."""
        # First get an entity ID
        entities_response = client.get("/api/v1/ontology/entities")
        assert entities_response.status_code == 200

        entities = entities_response.json()["entities"]
        if len(entities) == 0:
            pytest.skip("No entities available for testing")

        entity_id = entities[0]["id"]

        # Now get triplets
        response = client.get(f"/api/v1/ontology/entities/{entity_id}/triplets")

        assert response.status_code == 200
        data = response.json()

        # Frontend expects: { uri: string, triples: [...] }
        assert "uri" in data
        assert "triples" in data
        assert isinstance(data["triples"], list)

        if len(data["triples"]) > 0:
            triple = data["triples"][0]
            # Each triple should have subject, predicate, object
            assert "subject" in triple
            assert "predicate" in triple
            assert "object" in triple

    def test_sparql_query_endpoint_matches_frontend_format(self, client):
        """Verify SPARQL endpoint returns format expected by frontend useSparqlQuery."""
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?type WHERE { ?s a ?type } LIMIT 1
        """

        response = client.post(
            "/api/v1/query/sparql",
            json={"query": query, "format": "json"}
        )

        assert response.status_code == 200
        data = response.json()

        # Frontend expects SparqlQueryResponse with these fields
        assert "head" in data
        assert "results" in data
        assert "format" in data
        assert "query_time_ms" in data

        # Verify head structure
        if data["head"]:
            assert "vars" in data["head"]

        # Verify results structure
        assert "bindings" in data["results"]
        assert isinstance(data["results"]["bindings"], list)

        # Verify query_time_ms is a number
        assert isinstance(data["query_time_ms"], (int, float))
        assert data["query_time_ms"] >= 0

    def test_sparql_error_format_matches_frontend_expectations(self, client):
        """Verify error responses match frontend error handling."""
        # Invalid SPARQL query
        response = client.post(
            "/api/v1/query/sparql",
            json={"query": "INVALID SPARQL QUERY", "format": "json"}
        )

        # Should return 400 Bad Request
        assert response.status_code == 400

        # Frontend axios error handler expects: { detail: string }
        error_data = response.json()
        assert "detail" in error_data
        assert isinstance(error_data["detail"], str)
        assert len(error_data["detail"]) > 0

    def test_natural_language_query_matches_frontend_format(self, client):
        """Verify NL query endpoint returns format expected by frontend useNaturalLanguageQuery."""
        response = client.post(
            "/api/v1/query/natural",
            json={"question": "What are the drinking water plants?"}
        )

        assert response.status_code == 200
        data = response.json()

        # Frontend expects NaturalLanguageQueryResponse
        required_fields = [
            "original_question",
            "generated_sparql",
            "results",
            "execution_plan",
            "simulation_required",
            "suggested_models"
        ]

        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        # Verify data types
        assert isinstance(data["original_question"], str)
        assert data["generated_sparql"] is None or isinstance(data["generated_sparql"], str)
        assert isinstance(data["results"], list)
        assert isinstance(data["execution_plan"], str)
        assert isinstance(data["simulation_required"], bool)
        assert isinstance(data["suggested_models"], list)

    def test_relationships_query_compatibility(self, client):
        """Verify SPARQL results for relationships can be transformed by frontend."""
        # This is the exact query used by frontend useRelationships hook
        query = """
            PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT ?sourceId ?targetId ?label
            WHERE {
                ?sourceEntity wf:hasOutputPort ?out .
                ?out wf:flowsTo ?in .
                ?targetEntity wf:hasInputPort ?in .
                OPTIONAL { ?out rdfs:label ?label . }

                BIND(REPLACE(STR(?sourceEntity), "^.*[/|#]", "") AS ?sourceId)
                BIND(REPLACE(STR(?targetEntity), "^.*[/|#]", "") AS ?targetId)
            }
        """

        response = client.post(
            "/api/v1/query/sparql",
            json={"query": query, "format": "json"}
        )

        assert response.status_code == 200
        data = response.json()

        # Frontend expects to access: data.results?.bindings or data.results
        # Let's verify both structures work
        assert "results" in data

        # Check if it's the nested structure (preferred)
        if isinstance(data["results"], dict) and "bindings" in data["results"]:
            bindings = data["results"]["bindings"]
        else:
            # Or flat structure (backward compatibility)
            bindings = data["results"]

        # Verify bindings structure
        assert isinstance(bindings, list)

        # If we have results, verify they match frontend expectations
        for binding in bindings:
            # Frontend expects: { sourceId: {value: string}, targetId: {value: string}, label?: {value: string} }
            assert "sourceId" in binding or "targetId" in binding
            if "sourceId" in binding:
                assert "value" in binding["sourceId"]
            if "targetId" in binding:
                assert "value" in binding["targetId"]

    def test_simulation_endpoint_format(self, client):
        """Verify simulation endpoint returns format expected by frontend."""
        # Note: This test may fail if no model services are running
        # We're primarily testing the response format, not execution

        simulation_request = {
            "entity_ids": ["DWP1"],
            "scenario": {
                "duration": 3600,
                "timestep": 60
            },
            "parameters": {
                "initial_flow": 100
            }
        }

        response = client.post(
            "/api/v1/simulation/run",
            json=simulation_request
        )

        # May return 200 (success) or error if models not available
        # We just check format consistency
        if response.status_code == 200:
            data = response.json()

            # Frontend expects SimulationResult type
            expected_fields = ["simulation_id", "status", "results"]
            for field in expected_fields:
                assert field in data, f"Missing field: {field}"

            # Verify status is a valid string
            assert isinstance(data["status"], str)

    def test_cors_and_content_type_headers(self, client):
        """Verify backend sets correct headers for frontend communication."""
        response = client.get("/api/v1/ontology/entities")

        assert response.status_code == 200

        # Verify Content-Type is JSON
        assert "application/json" in response.headers.get("content-type", "")

    def test_error_status_codes_are_appropriate(self, client):
        """Verify backend returns appropriate HTTP status codes for different errors."""
        # 400 Bad Request - Invalid query
        response = client.post(
            "/api/v1/query/sparql",
            json={"query": "INSERT DATA { <s> <p> <o> }", "format": "json"}
        )
        assert response.status_code == 400

        # 400 Bad Request - Query too long
        long_query = "SELECT * WHERE { ?s ?p ?o }" * 1000
        response = client.post(
            "/api/v1/query/sparql",
            json={"query": long_query, "format": "json"}
        )
        assert response.status_code == 400

        # Verify error messages are informative
        error_data = response.json()
        assert "detail" in error_data
        assert len(error_data["detail"]) > 0

    def test_query_response_timing_included(self, client):
        """Verify backend includes query timing information for performance monitoring."""
        query = "SELECT * WHERE { ?s ?p ?o } LIMIT 1"

        response = client.post(
            "/api/v1/query/sparql",
            json={"query": query, "format": "json"}
        )

        assert response.status_code == 200
        data = response.json()

        # Frontend uses this for performance monitoring
        assert "query_time_ms" in data
        assert isinstance(data["query_time_ms"], (int, float))
        assert data["query_time_ms"] >= 0

    def test_pagination_and_limits_compatibility(self, client):
        """Verify backend respects LIMIT clauses in SPARQL for frontend performance."""
        # Frontend might use LIMIT for pagination
        query_with_limit = "SELECT ?s WHERE { ?s ?p ?o } LIMIT 10"

        response = client.post(
            "/api/v1/query/sparql",
            json={"query": query_with_limit, "format": "json"}
        )

        assert response.status_code == 200
        data = response.json()

        # Should not return more than requested limit
        bindings = data["results"]["bindings"]
        assert len(bindings) <= 10


class TestDataTypeCompatibility:
    """Tests ensuring data type compatibility between backend and frontend."""

    def test_numeric_values_are_properly_typed(self, client):
        """Verify numeric values from backend can be used in frontend calculations."""
        response = client.get("/api/v1/ontology/entities")
        assert response.status_code == 200

        entities = response.json()["entities"]

        for entity in entities:
            # If lat/lon exist, they should be convertible to float
            if entity.get("lat"):
                try:
                    lat = float(entity["lat"])
                    assert isinstance(lat, float)
                except (ValueError, TypeError):
                    pytest.fail(f"Entity {entity['id']}: lat value '{entity['lat']}' cannot be converted to float")

            if entity.get("lon"):
                try:
                    lon = float(entity["lon"])
                    assert isinstance(lon, float)
                except (ValueError, TypeError):
                    pytest.fail(f"Entity {entity['id']}: lon value '{entity['lon']}' cannot be converted to float")

    def test_null_vs_empty_string_handling(self, client):
        """Verify consistent handling of null/empty values."""
        response = client.get("/api/v1/ontology/entities")
        assert response.status_code == 200

        entities = response.json()["entities"]

        for entity in entities:
            # Optional fields should be either empty string or have a value
            # Frontend handles both, but consistency is important
            optional_fields = ["zone", "capacity", "population", "description"]

            for field in optional_fields:
                if field in entity:
                    value = entity[field]
                    # Value should be either empty string or non-empty string
                    assert isinstance(value, str), f"Field {field} should be string, got {type(value)}"

    def test_uri_format_consistency(self, client):
        """Verify URIs are consistently formatted for frontend ID extraction."""
        response = client.get("/api/v1/ontology/entities")
        assert response.status_code == 200

        entities = response.json()["entities"]

        for entity in entities:
            uri = entity.get("uri")
            entity_id = entity.get("id")

            if uri and entity_id:
                # Frontend extracts ID from URI using split("/")[-1] or split("#")[-1]
                # Verify backend ID matches what frontend would extract
                extracted_id = uri.split("/")[-1].split("#")[-1]
                assert entity_id == extracted_id, \
                    f"Entity ID '{entity_id}' doesn't match URI-extracted ID '{extracted_id}' from URI: {uri}"


class TestEndpointAvailability:
    """Tests ensuring all endpoints required by frontend are available."""

    def test_all_frontend_required_endpoints_exist(self, client):
        """Verify all endpoints called by frontend exist and respond."""
        # List of endpoints used by frontend
        endpoints = [
            ("GET", "/api/v1/ontology/entities"),
            ("GET", "/api/v1/ontology/prefixes"),
            ("POST", "/api/v1/query/sparql"),
            ("POST", "/api/v1/query/natural"),
            # Note: Some endpoints require parameters, tested separately
        ]

        for method, path in endpoints:
            if method == "GET":
                response = client.get(path)
            elif method == "POST":
                # Provide minimal valid payload
                if "sparql" in path:
                    response = client.post(path, json={"query": "SELECT * WHERE { ?s ?p ?o } LIMIT 1"})
                elif "natural" in path:
                    response = client.post(path, json={"question": "test question"})
                else:
                    response = client.post(path, json={})

            # Should not return 404
            assert response.status_code != 404, \
                f"Endpoint {method} {path} not found (required by frontend)"

            # Should return valid response (200 or error with detail)
            assert response.status_code in [200, 400, 500], \
                f"Unexpected status code {response.status_code} for {method} {path}"
