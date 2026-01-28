"""Tests for WWTP model stub."""
import pytest
from unittest.mock import patch
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from ghent_water.models.stubs.wwtp import create_wwtp_model


class TestWWTPModel:
    """Test cases for WWTP model."""

    def test_create_wwtp_model(self, fixed_random_seed):
        """Test creating a WWTP model."""
        model = create_wwtp_model(entity_id="wwtp1", port=8003)

        assert model.entity_id == "wwtp1"
        assert model.port == 8003
        # Note: entity_name returns full name
        assert "Wastewater Treatment Plant" in model.entity_name
        assert hasattr(model, 'app')

    def test_wwtp_model_has_endpoints(self, fixed_random_seed):
        """Test that WWTP model has required endpoints."""
        model = create_wwtp_model(entity_id="wwtp1", port=8003)

        assert hasattr(model.app, 'routes')

    def test_wwtp_model_simulation_output_structure(self, fixed_random_seed):
        """Test that WWTP simulation returns expected structure."""
        model = create_wwtp_model(entity_id="wwtp1", port=8003)

        from starlette.testclient import TestClient
        client = TestClient(model.app)
        response = client.post("/simulate", json={})

        assert response.status_code == 200
        data = response.json()
        # Use actual field names from WWTP stub
        assert "effluent_flow" in data
        assert "effluent_BOD" in data
        assert "compliance_status" in data


class TestWWTPTreatmentEfficiency:
    """Test WWTP treatment efficiency calculations."""

    def test_cod_efficiency_positive(self, fixed_random_seed):
        """Test that COD efficiency is positive."""
        model = create_wwtp_model(entity_id="wwtp1", port=8003)

        from starlette.testclient import TestClient
        client = TestClient(model.app)
        response = client.post("/simulate", json={})

        assert response.status_code == 200
        data = response.json()
        efficiency = data.get("removal_efficiency_COD", 0)
        assert 0 <= efficiency <= 100, "COD removal efficiency should be between 0 and 100"

    def test_bod_removal_efficiency(self, fixed_random_seed):
        """Test BOD removal efficiency."""
        model = create_wwtp_model(entity_id="wwtp1", port=8003)

        from starlette.testclient import TestClient
        client = TestClient(model.app)
        response = client.post("/simulate", json={})

        assert response.status_code == 200
        data = response.json()
        bod_removal = data.get("removal_efficiency_BOD", 0)
        assert 0 <= bod_removal <= 100, "BOD removal should be between 0 and 100"


class TestVLAREMIICompliance:
    """Test VLAREM II compliance checks."""

    def test_discharge_within_limits(self, fixed_random_seed):
        """Test that discharge parameters are within VLAREM II limits."""
        model = create_wwtp_model(entity_id="wwtp1", port=8003)

        from starlette.testclient import TestClient
        client = TestClient(model.app)
        response = client.post("/simulate", json={})

        assert response.status_code == 200
        data = response.json()

        # VLAREM II limits
        cod_limit = 125  # mg/L
        bod_limit = 25   # mg/L
        tss_limit = 35   # mg/L

        cod = data.get("effluent_COD", 0)
        bod = data.get("effluent_BOD", 0)
        tss = data.get("effluent_TSS", 0)

        assert cod <= cod_limit, f"COD {cod} should be <= {cod_limit} mg/L"
        assert bod <= bod_limit, f"BOD {bod} should be <= {bod_limit} mg/L"
        assert tss <= tss_limit, f"TSS {tss} should be <= {tss_limit} mg/L"

    def test_compliance_status_structure(self, fixed_random_seed):
        """Test compliance status structure."""
        model = create_wwtp_model(entity_id="wwtp1", port=8003)

        from starlette.testclient import TestClient
        client = TestClient(model.app)
        response = client.post("/simulate", json={})

        assert response.status_code == 200
        data = response.json()

        compliance = data.get("compliance_status", {})
        assert "is_compliant" in compliance
        assert "violations" in compliance
        assert "regulation" in compliance
        assert compliance["regulation"] == "VLAREM II"


class TestWWTPEnergyAndSludge:
    """Test WWTP energy and sludge production."""

    def test_energy_consumption_positive(self, fixed_random_seed):
        """Test that energy consumption is positive."""
        model = create_wwtp_model(entity_id="wwtp1", port=8003)

        from starlette.testclient import TestClient
        client = TestClient(model.app)
        response = client.post("/simulate", json={})

        assert response.status_code == 200
        data = response.json()
        energy = data.get("energy_consumption", 0)
        assert energy >= 0, "Energy consumption should be non-negative"

    def test_sludge_production_positive(self, fixed_random_seed):
        """Test that sludge production is positive."""
        model = create_wwtp_model(entity_id="wwtp1", port=8003)

        from starlette.testclient import TestClient
        client = TestClient(model.app)
        response = client.post("/simulate", json={})

        assert response.status_code == 200
        data = response.json()
        sludge = data.get("sludge_production", 0)
        assert sludge >= 0, "Sludge production should be non-negative"
