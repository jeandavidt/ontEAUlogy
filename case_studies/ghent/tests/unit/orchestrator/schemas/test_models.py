# tests/unit/orchestrator/schemas/test_models.py

import pytest
from pydantic import ValidationError
from ghent_water.orchestrator.schemas.models import (
    SparqlQueryRequest,
    ModelRegistrationRequest,
    SimulationRequest,
)


def test_sparql_query_request_valid():
    """Test valid SPARQL query request."""
    request = SparqlQueryRequest(query="SELECT ?s WHERE { ?s ?p ?o }", format="json")
    assert request.query is not None
    assert request.format == "json"


def test_sparql_query_request_invalid_format():
    """Test invalid format rejection."""
    with pytest.raises(ValidationError):
        SparqlQueryRequest(
            query="SELECT ?s WHERE { ?s ?p ?o }", format="invalid_format"
        )


def test_model_registration_required_fields():
    """Test model registration requires all fields."""
    with pytest.raises(ValidationError):
        ModelRegistrationRequest(
            id="test",
            name="Test Model",
            # Missing required fields: endpoint, capabilities, entities
        )


def test_simulation_request_validation():
    """Test simulation request validation."""
    valid_request = SimulationRequest(
        entity_ids=["DWP1", "WWTP1"],
        scenario={"duration": 3600, "timestep": 60},
        parameters={"initial_flow": 100},
    )
    print(f"SimulationRequest fields: {SimulationRequest.model_fields.keys()}")
    assert len(valid_request.entity_ids) == 2
    assert valid_request.scenario["duration"] == 3600
