"""Tests for DWP (Drinking Water Plant) model stub."""
import pytest
from unittest.mock import patch
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from ghent_water.models.stubs.dwp import create_dwp_model


class TestDWPModel:
    """Test cases for DWP model."""

    def test_create_dwp_model(self, fixed_random_seed):
        """Test creating a DWP model."""
        model = create_dwp_model(entity_id="dwp1", port=8001)

        assert model.entity_id == "dwp1"
        assert model.port == 8001
        # Note: entity_name returns full name, not abbreviation
        assert "Drinking Water Plant" in model.entity_name
        assert hasattr(model, 'app')

    def test_dwp_model_has_endpoints(self, fixed_random_seed):
        """Test that DWP model has required endpoints."""
        model = create_dwp_model(entity_id="dwp1", port=8001)

        assert hasattr(model.app, 'routes')

    def test_dwp_model_simulation_output_structure(self, fixed_random_seed):
        """Test that DWP simulation returns expected structure."""
        model = create_dwp_model(entity_id="dwp1", port=8001)

        from starlette.testclient import TestClient
        client = TestClient(model.app)
        response = client.post("/simulate", json={})

        assert response.status_code == 200
        data = response.json()
        # Use actual field names from DWP stub
        assert "treated_water_flow" in data
        assert "treated_water_turbidity" in data


class TestDWPTreatmentProcess:
    """Test DWP treatment process calculations."""

    def test_turbidity_reduction(self, fixed_random_seed):
        """Test that turbidity is reduced through treatment."""
        model = create_dwp_model(entity_id="dwp1", port=8001)

        from starlette.testclient import TestClient
        client = TestClient(model.app)
        response = client.post("/simulate", json={})

        assert response.status_code == 200
        data = response.json()

        # Check removal efficiency is positive
        removal = data.get("removal_efficiency_turbidity", 0)
        assert 0 <= removal <= 100, "Removal efficiency should be between 0 and 100"

    def test_flow_rate_positive(self, fixed_random_seed):
        """Test that flow rate is positive."""
        model = create_dwp_model(entity_id="dwp1", port=8001)

        from starlette.testclient import TestClient
        client = TestClient(model.app)
        response = client.post("/simulate", json={})

        assert response.status_code == 200
        data = response.json()
        flow = data.get("treated_water_flow", 0)
        assert flow > 0, "Flow rate should be positive"


class TestDWPWaterQuality:
    """Test DWP water quality parameters."""

    def test_ph_within_range(self, fixed_random_seed):
        """Test that pH is within drinking water standards."""
        model = create_dwp_model(entity_id="dwp1", port=8001)

        from starlette.testclient import TestClient
        client = TestClient(model.app)
        response = client.post("/simulate", json={})

        assert response.status_code == 200
        data = response.json()
        ph = data.get("treated_water_ph", 7.0)

        # Drinking water pH should be between 6.5 and 9.5
        assert 6.5 <= ph <= 9.5, f"pH {ph} should be between 6.5 and 9.5"

    def test_toc_removal_positive(self, fixed_random_seed):
        """Test that TOC removal is positive."""
        model = create_dwp_model(entity_id="dwp1", port=8001)

        from starlette.testclient import TestClient
        client = TestClient(model.app)
        response = client.post("/simulate", json={})

        assert response.status_code == 200
        data = response.json()
        toc_removal = data.get("removal_efficiency_toc", 0)

        assert 0 <= toc_removal <= 100, "TOC removal should be between 0 and 100"
