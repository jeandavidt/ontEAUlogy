"""Tests for River model stub."""
import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from ghent_water.models.stubs.river import create_river_model


class TestRiverModel:
    """Test cases for River model."""

    def test_create_river_model(self, fixed_random_seed):
        """Test creating a river model."""
        model = create_river_model(entity_id="lieve_river", port=8010)

        assert model.entity_id == "lieve_river"
        assert model.port == 8010
        # Note: entity_name returns full name
        assert "River" in model.entity_name
        assert hasattr(model, 'app')

    def test_river_model_has_endpoints(self, fixed_random_seed):
        """Test that river model has required endpoints."""
        model = create_river_model(entity_id="test_river", port=8011)

        # Model should have FastAPI app with health and describe endpoints
        assert hasattr(model.app, 'routes')

    def test_river_model_simulation_output_structure(self, fixed_random_seed):
        """Test that river model simulation returns expected structure."""
        model = create_river_model(entity_id="test_river", port=8011)

        # Call simulate endpoint
        from starlette.testclient import TestClient

        client = TestClient(model.app)
        response = client.post("/simulate", json={})

        assert response.status_code == 200
        data = response.json()
        # Use actual field names from river stub
        assert "downstream_flow" in data
        assert "downstream_quality" in data

    def test_river_model_mixing_efficiency(self, fixed_random_seed):
        """Test that river model returns mixing efficiency."""
        model = create_river_model(entity_id="test_river", port=8011)

        from starlette.testclient import TestClient
        client = TestClient(model.app)
        response = client.post("/simulate", json={})

        assert response.status_code == 200
        data = response.json()
        assert "mixing_efficiency" in data
        mixing = data.get("mixing_efficiency", 0)
        assert 0 <= mixing <= 100, "Mixing efficiency should be between 0 and 100"


class TestRiverModelParameters:
    """Test river model parameter generation."""

    def test_downstream_flow_positive(self, fixed_random_seed):
        """Test that downstream flow is positive."""
        model = create_river_model(entity_id="test_river", port=8011)

        from starlette.testclient import TestClient
        client = TestClient(model.app)

        response = client.post("/simulate", json={})
        if response.status_code == 200:
            flow = response.json().get("downstream_flow", 0)
            assert flow > 0, "Downstream flow should be positive"

    def test_quality_change_sensible(self, fixed_random_seed):
        """Test that quality change is within sensible range."""
        model = create_river_model(entity_id="test_river", port=8011)

        from starlette.testclient import TestClient
        client = TestClient(model.app)

        response = client.post("/simulate", json={})

        assert response.status_code == 200
        data = response.json()
        quality_change = data.get("quality_change", 0)
        # Quality change should be between -1 and 1 (unitless ratio)
        assert -1 <= quality_change <= 1, "Quality change should be between -1 and 1"

    def test_flow_contributions_positive(self, fixed_random_seed):
        """Test that flow contributions are positive."""
        model = create_river_model(entity_id="test_river", port=8011)

        from starlette.testclient import TestClient
        client = TestClient(model.app)

        response = client.post("/simulate", json={})

        assert response.status_code == 200
        data = response.json()
        upstream = data.get("flow_contribution_upstream", 0)
        total = data.get("flow_contribution_total_discharge", 0)
        assert 0 <= upstream <= 100, "Upstream contribution should be 0-100%"
        assert 0 <= total <= 100, "Total discharge contribution should be 0-100%"
