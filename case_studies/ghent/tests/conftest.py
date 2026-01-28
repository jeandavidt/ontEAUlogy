"""Shared pytest fixtures for ghent_water tests."""
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
import httpx

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture
def fresh_registry():
    """Fresh ModelRegistry for isolated testing."""
    from ghent_water.orchestrator.services.model_registry import ModelRegistry
    return ModelRegistry()


@pytest.fixture
def mock_httpx_client():
    """Mock httpx.AsyncClient for HTTP testing."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    return mock_client


@pytest.fixture
def mock_httpx_connect_error():
    """Mock client that raises ConnectError on any request."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.side_effect = httpx.ConnectError("Connection refused")
    mock_client.post.side_effect = httpx.ConnectError("Connection refused")
    return mock_client


@pytest.fixture
def mock_httpx_success():
    """Mock client that returns successful responses."""
    model_description = {
        "@graph": [
            {
                "@type": "wf:DrinkingWaterPlant",
                "rdfs:label": "DWP1",
                "rdfs:comment": "Drinking Water Plant 1"
            }
        ]
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = model_description

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = mock_response
    mock_client.post.return_value = mock_response
    return mock_client


@pytest.fixture
def sample_rdf_graph():
    """RDF graph with test data."""
    from rdflib import Graph, URIRef, Literal, Namespace
    from rdflib.namespace import RDF, RDFS

    wf = Namespace("https://w3id.org/waterframe/")
    ghent = Namespace("https://w3id.org/waterframe/case/ghent/")

    g = Graph()
    g.bind("wf", wf)
    g.bind("ghent", ghent)

    # Add test entities
    g.add((ghent.DWP1, RDF.type, wf.DrinkingWaterPlant))
    g.add((ghent.DWP1, RDFS.label, Literal("DWP1")))
    g.add((ghent.DWP1, wf.hasCapacity, Literal("2000")))

    g.add((ghent.WWTP1, RDF.type, wf.WastewaterTreatmentPlant))
    g.add((ghent.WWTP1, RDFS.label, Literal("WWTP1")))

    g.add((ghent.LieveRiver, RDF.type, wf.RiverSegment))
    g.add((ghent.LieveRiver, RDFS.label, Literal("Lieve River")))

    return g


@pytest.fixture
def fixed_random_seed():
    """Fixture that sets a fixed random seed for deterministic tests."""
    import random
    random.seed(42)
    yield
    # Reset seed after test (not strictly necessary but good practice)
    random.seed(None)


@pytest.fixture
def mock_registry_instance(fresh_registry):
    """Pre-populated registry with test models."""
    from ghent_water.orchestrator.schemas.models import ModelRegistrationRequest

    # Register some test models
    fresh_registry.register_model(ModelRegistrationRequest(
        id="dwp1",
        name="DWP1",
        description="Drinking Water Plant 1",
        endpoint="http://localhost:8001",
        capabilities=["SteadyStateSimulation", "MassBalance"],
        entities=["ghent:DWP1"],
    ))

    fresh_registry.register_model(ModelRegistrationRequest(
        id="lieve_river",
        name="Lieve River",
        description="River segment",
        endpoint="http://localhost:8010",
        capabilities=["SteadyStateSimulation"],
        entities=["ghent:LIEVE_RIVER"],
    ))

    return fresh_registry


@pytest.fixture
def app_client():
    """Test client for FastAPI application."""
    from ghent_water.orchestrator.main import app
    from httpx import ASGITransport, AsyncClient

    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")
