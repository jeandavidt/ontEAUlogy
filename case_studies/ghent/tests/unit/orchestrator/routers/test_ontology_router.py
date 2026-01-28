# tests/unit/orchestrator/routers/test_ontology_router.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from ghent_water.orchestrator.main import app
from ghent_water.orchestrator.schemas.models import (
    OntologyInfo,
    EntityTriplesResponse,
    ValidationRequest,
)
from ghent_water.orchestrator.services.ontology_store import (
    OntologyStore,
)  # Import for type hinting in mock


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_ontology_store():
    """Mock the ontology_store service."""
    with patch(
        "ghent_water.orchestrator.routers.ontology.ontology_store"
    ) as mock_store:
        mock_store.load_ontology = AsyncMock()
        mock_store.get_namespaces.return_value = {"wf": "https://w3id.org/waterframe/"}
        mock_store.get_entity_count.return_value = {"triples": 100, "entities": 10}
        mock_store.get_triples_for_entity.return_value = []
        mock_store.query_sparql.return_value = {"results": {"bindings": []}}
        mock_store.serialize.return_value = "serialized_data"
        mock_store.merge_model_description = AsyncMock(return_value=5)
        mock_store.reload = AsyncMock()
        yield mock_store


@pytest.fixture
def mock_namespace_manager():
    """Mock the namespace_manager service."""
    with patch(
        "ghent_water.orchestrator.routers.ontology.namespace_manager", autospec=True
    ) as mock_manager:
        mock_manager.is_loaded.return_value = True
        mock_manager.load_namespaces = MagicMock()
        mock_manager.get_sparql_prefixes.return_value = (
            "PREFIX wf: <https://w3id.org/waterframe/>"
        )
        mock_manager.get_all_prefixes.return_value = {
            "wf": "https://w3id.org/waterframe/"
        }
        yield mock_manager


@pytest.fixture
def mock_mapping_agent():
    """Mock the mapping_agent service."""
    with patch(
        "ghent_water.orchestrator.routers.ontology.mapping_agent", autospec=True
    ) as mock_agent:
        mock_agent.detect_ontology.return_value = ["waterframe"]
        mock_agent.translate_to_waterframe.return_value = "translated_rdf_data"
        yield mock_agent


@pytest.mark.asyncio
async def test_get_ontology_info_success(client, mock_ontology_store):
    """Test successful retrieval of ontology information."""
    # Arrange
    mock_ontology_store.get_entity_count.return_value = {
        "triples": 150,
        "entities": 15,
        "DrinkingWaterPlant": 5,
    }
    mock_ontology_store.get_namespaces.return_value = {
        "wf": "https://w3id.org/waterframe/",
        "ex": "http://example.org/",
    }

    # Act
    response = client.get("/api/v1/ontology/")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["graph_size"] == 150
    assert "wf" in data["namespaces"]
    assert "ex" in data["namespaces"]
    assert data["entities_count"] == {
        "triples": 150,
        "entities": 15,
        "DrinkingWaterPlant": 5,
    }
    mock_ontology_store.load_ontology.assert_called_once()


@pytest.mark.asyncio
async def test_get_ontology_info_error(client, mock_ontology_store):
    """Test error handling during ontology info retrieval."""
    # Arrange
    mock_ontology_store.load_ontology.side_effect = Exception("Test error")

    # Act
    response = client.get("/api/v1/ontology/")

    # Assert
    assert response.status_code == 500
    assert "Test error" in response.json()["detail"]
    mock_ontology_store.load_ontology.assert_called_once()


@pytest.mark.asyncio
async def test_get_entity_triples_success(client, mock_ontology_store):
    """Test successful retrieval of entity triples."""
    # Arrange
    entity_uri = "http://example.org/entity1"
    mock_ontology_store.get_triples_for_entity.return_value = [
        {"s": "entity1", "p": "prop1", "o": "val1"},
        {"s": "entity1", "p": "prop2", "o": "val2"},
    ]

    # Act
    response = client.get(f"/api/v1/ontology/entity/{entity_uri}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["uri"] == entity_uri
    assert len(data["triples"]) == 2
    mock_ontology_store.load_ontology.assert_called()
    mock_ontology_store.get_triples_for_entity.assert_called_with(entity_uri)


@pytest.mark.asyncio
async def test_get_entity_triples_no_results(client, mock_ontology_store):
    """Test retrieval of entity triples with no results."""
    # Arrange
    entity_uri = "http://example.org/nonexistent"
    mock_ontology_store.get_triples_for_entity.return_value = []

    # Act
    response = client.get(f"/api/v1/ontology/entity/{entity_uri}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["uri"] == entity_uri
    assert len(data["triples"]) == 0
    mock_ontology_store.load_ontology.assert_called()
    mock_ontology_store.get_triples_for_entity.assert_called_with(entity_uri)


@pytest.mark.asyncio
async def test_get_entity_triples_error(client, mock_ontology_store):
    """Test error handling during entity triples retrieval."""
    # Arrange
    entity_uri = "http://example.org/error_entity"
    mock_ontology_store.get_triples_for_entity.side_effect = Exception("Triples error")

    # Act
    response = client.get(f"/api/v1/ontology/entity/{entity_uri}")

    # Assert
    assert response.status_code == 500
    assert "Triples error" in response.json()["detail"]
    mock_ontology_store.load_ontology.assert_called()
    mock_ontology_store.get_triples_for_entity.assert_called_with(entity_uri)


@pytest.mark.asyncio
async def test_get_entity_triplets_by_id_direct_match(client, mock_ontology_store):
    """Test successful retrieval of entity triples by ID with direct match."""
    # Arrange
    entity_id = "DWP1"
    expected_uri = f"https://w3id.org/waterframe/case/ghent/{entity_id}"
    mock_ontology_store.get_triples_for_entity.return_value = [
        {"s": expected_uri, "p": "prop1", "o": "val1"}
    ]

    # Act
    response = client.get(f"/api/v1/ontology/entities/{entity_id}/triplets")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["uri"] == expected_uri
    assert len(data["triples"]) == 1
    mock_ontology_store.load_ontology.assert_called()
    mock_ontology_store.get_triples_for_entity.assert_called_with(expected_uri)


@pytest.mark.asyncio
async def test_get_entity_triplets_by_id_sparql_search(client, mock_ontology_store):
    """Test successful retrieval of entity triples by ID via SPARQL search."""
    # Arrange
    entity_id = "wwtp1"
    expected_uri = "https://w3id.org/waterframe/case/ghent/WWTP1"
    mock_ontology_store.get_triples_for_entity.side_effect = [
        [],
        [{"s": expected_uri, "p": "propX", "o": "valX"}],
    ]  # First call returns empty, second returns actual triples
    mock_ontology_store.query_sparql.return_value = {
        "results": {"bindings": [{"entity": {"type": "uri", "value": expected_uri}}]}
    }

    # Act
    response = client.get(f"/api/v1/ontology/entities/{entity_id}/triplets")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["uri"] == expected_uri
    assert len(data["triples"]) == 1
    mock_ontology_store.load_ontology.assert_called()
    # Should call get_triples_for_entity twice: once for direct, once after SPARQL
    assert mock_ontology_store.get_triples_for_entity.call_count == 2
    mock_ontology_store.query_sparql.assert_called_once()


@pytest.mark.asyncio
async def test_get_entity_triplets_by_id_no_results(client, mock_ontology_store):
    """Test retrieval of entity triples by ID with no results."""
    # Arrange
    entity_id = "NonExistent"
    mock_ontology_store.get_triples_for_entity.return_value = []
    mock_ontology_store.query_sparql.return_value = {"results": {"bindings": []}}

    # Act
    response = client.get(f"/api/v1/ontology/entities/{entity_id}/triplets")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert (
        data["uri"] == f"https://w3id.org/waterframe/case/ghent/{entity_id}"
    )  # Default constructed URI
    assert len(data["triples"]) == 0
    mock_ontology_store.load_ontology.assert_called()
    mock_ontology_store.get_triples_for_entity.assert_called_once()
    mock_ontology_store.query_sparql.assert_called_once()


@pytest.mark.asyncio
async def test_get_entity_triplets_by_id_error(client, mock_ontology_store):
    """Test error handling during entity triples retrieval by ID."""
    # Arrange
    entity_id = "error_id"
    mock_ontology_store.load_ontology.side_effect = Exception("ID triples error")

    # Act
    response = client.get(f"/api/v1/ontology/entities/{entity_id}/triplets")

    # Assert
    assert response.status_code == 500
    assert "ID triples error" in response.json()["detail"]
    mock_ontology_store.load_ontology.assert_called_once()


@pytest.mark.asyncio
async def test_validate_graph_success(client):
    """Test successful graph validation (stub implementation)."""
    # Arrange
    validation_request = {
        "data_graph": "<http://example.org/s> <http://example.org/p> <http://example.org/o> .",
        "shape_graph": "<http://example.org/shape> <http://example.org/type> <http://example.org/Shape> .",
    }

    # Act
    response = client.post("/api/v1/ontology/validate", json=validation_request)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["conforms"] is True
    assert data["results"] == []


@pytest.mark.asyncio
async def test_validate_graph_invalid_request(client):
    """Test validation for an invalid request body."""
    # Arrange: Missing required 'data_graph' field
    invalid_request = {
        "shape_graph": "<http://example.org/shape> <http://example.org/type> <http://example.org/Shape> ."
    }

    # Act
    response = client.post("/api/v1/ontology/validate", json=invalid_request)

    # Assert
    assert (
        response.status_code == 422
    )  # Unprocessable Entity for Pydantic validation errors
    assert "field required" in response.json()["detail"][0]["msg"].lower()


@pytest.mark.asyncio
async def test_serialize_ontology_success(client, mock_ontology_store):
    """Test successful serialization of the ontology."""
    # Arrange
    mock_ontology_store.serialize.return_value = (
        "@prefix ex: <http://example.org/> . ex:entity a ex:Type ."
    )

    # Act
    response = client.get("/api/v1/ontology/serialize?format=turtle")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["format"] == "turtle"
    assert "@prefix ex:" in data["data"]
    mock_ontology_store.load_ontology.assert_called_once()
    mock_ontology_store.serialize.assert_called_once_with("turtle")


@pytest.mark.asyncio
async def test_serialize_ontology_error(client, mock_ontology_store):
    """Test error handling during ontology serialization."""
    # Arrange
    mock_ontology_store.serialize.side_effect = Exception("Serialization error")

    # Act
    response = client.get("/api/v1/ontology/serialize?format=turtle")

    # Assert
    assert response.status_code == 500
    assert "Serialization error" in response.json()["detail"]
    mock_ontology_store.load_ontology.assert_called_once()
    mock_ontology_store.serialize.assert_called_once_with("turtle")


@pytest.mark.asyncio
async def test_merge_model_description_success(client, mock_ontology_store):
    """Test successful merging of a model's RDF description."""
    # Arrange
    model_id = "model123"
    rdf_data = "<http://example.org/s> <http://example.org/p> <http://example.org/o> ."
    mock_ontology_store.merge_model_description.return_value = 3

    # Act
    response = client.post(
        f"/api/v1/ontology/merge?model_id={model_id}&rdf_data={rdf_data}",
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["model_id"] == model_id
    assert data["triples_added"] == 3
    mock_ontology_store.load_ontology.assert_called_once()
    mock_ontology_store.merge_model_description.assert_called_once_with(
        model_id, rdf_data
    )


@pytest.mark.asyncio
async def test_merge_model_description_error(client, mock_ontology_store):
    """Test error handling during merging of a model's RDF description."""
    # Arrange
    model_id = "model_error"
    rdf_data = "invalid rdf data"
    mock_ontology_store.merge_model_description.side_effect = Exception("Merge error")

    # Act
    response = client.post(
        f"/api/v1/ontology/merge?model_id={model_id}&rdf_data={rdf_data}",
    )

    # Assert
    assert response.status_code == 500
    assert "Merge error" in response.json()["detail"]
    mock_ontology_store.load_ontology.assert_called_once()
    mock_ontology_store.merge_model_description.assert_called_once_with(
        model_id, rdf_data
    )
