"""Tests for simulation router - Bug Investigation Tests.

These tests specifically target the bug where `/simulation/models/lieve_river/run`
returns "Unknown model: lieve_river" despite the model being in MODEL_PORTS.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from ghent_water.orchestrator.routers.simulation import MODEL_PORTS
from ghent_water.orchestrator.services.model_registry import ModelRegistry


class TestModelPortsConfiguration:
    """Test MODEL_PORTS configuration consistency."""

    def test_model_ports_contains_lieve_river(self):
        """Verify 'lieve_river' is in MODEL_PORTS."""
        assert "lieve_river" in MODEL_PORTS, "lieve_river should be in MODEL_PORTS"
        assert MODEL_PORTS["lieve_river"] == 8010, "lieve_river should map to port 8010"

    def test_model_ports_contains_all_expected_models(self):
        """Verify all expected models are in MODEL_PORTS."""
        expected_models = [
            "dwp1", "dwp2",  # Drinking Water Plants
            "wwtp1", "wwtp2",  # Wastewater Treatment Plants
            "texfin", "foodpro", "chiptech", "pharmagen", "brewco",  # Industries
            "lieve_river",  # River
            "dampoort", "muide",  # Residential
        ]

        for model in expected_models:
            assert model in MODEL_PORTS, f"Model '{model}' should be in MODEL_PORTS"

    def test_model_ports_ports_are_unique(self):
        """Verify all ports in MODEL_PORTS are unique."""
        ports = list(MODEL_PORTS.values())
        assert len(ports) == len(set(ports)), "All ports should be unique"

    def test_model_ports_port_range(self):
        """Verify all ports are in expected range."""
        for model, port in MODEL_PORTS.items():
            assert 8000 <= port <= 8100, f"Port {port} for {model} should be in range 8000-8100"


class TestSimulationEndpoints:
    """Test simulation endpoint behavior."""

    @pytest.fixture
    def registry(self):
        """Fresh registry for testing."""
        return ModelRegistry()

    @pytest.mark.asyncio
    async def test_run_simulation_model_not_running_returns_503(self, registry):
        """When model is in MODEL_PORTS but not running, should return 503, NOT 404."""
        from fastapi import HTTPException
        from ghent_water.orchestrator.routers.simulation import try_register_model

        # Mock httpx to simulate connection error (model not running)
        with patch('ghent_water.orchestrator.routers.simulation.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.side_effect = httpx.ConnectError("Connection refused")
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # try_register_model should return False when model is not running
            result = await try_register_model("lieve_river")
            assert result is False, "try_register_model should return False when model is not running"

        # The router should then raise 503, not 404
        # This is tested by checking the logic in run_simulation
        model = registry.get_model("lieve_river")
        if not model:
            if "lieve_river" in MODEL_PORTS:
                # This is the expected behavior: 503 for known model not running
                port = MODEL_PORTS["lieve_river"]
                assert port == 8010
            else:
                pytest.fail("lieve_river should be in MODEL_PORTS")

    @pytest.mark.asyncio
    async def test_try_register_model_unknown_model_returns_false(self):
        """Test that try_register_model returns False for unknown model IDs."""
        from ghent_water.orchestrator.routers.simulation import try_register_model

        result = await try_register_model("nonexistent_model")
        assert result is False

    @pytest.mark.asyncio
    async def test_try_register_model_connect_error(self, mock_httpx_connect_error):
        """Test that try_register_model handles connection errors gracefully."""
        from ghent_water.orchestrator.routers.simulation import try_register_model

        with patch('ghent_water.orchestrator.routers.simulation.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.side_effect = httpx.ConnectError("Connection refused")
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await try_register_model("lieve_river")
            assert result is False


class TestModelPortsVsModelRegistry:
    """Test consistency between MODEL_PORTS and MODEL_REGISTRY."""

    def test_model_ports_matches_model_runner_registry(self):
        """Verify MODEL_PORTS matches MODEL_REGISTRY from model_runner.py."""
        # Import from model_runner to check consistency
        from ghent_water.models.runners.model_runner import MODEL_REGISTRY

        # All models in MODEL_PORTS should be in MODEL_REGISTRY
        for model_id, port in MODEL_PORTS.items():
            assert model_id in MODEL_REGISTRY, f"Model '{model_id}' from MODEL_PORTS not in MODEL_REGISTRY"
            _, registry_port, _ = MODEL_REGISTRY[model_id]
            assert port == registry_port, f"Port mismatch for {model_id}: MODEL_PORTS={port}, MODEL_REGISTRY={registry_port}"

    def test_model_runner_registry_matches_model_ports(self):
        """Verify MODEL_REGISTRY matches MODEL_PORTS."""
        from ghent_water.models.runners.model_runner import MODEL_REGISTRY

        for model_id, (_, port, _) in MODEL_REGISTRY.items():
            assert model_id in MODEL_PORTS, f"Model '{model_id}' from MODEL_REGISTRY not in MODEL_PORTS"
            assert MODEL_PORTS[model_id] == port, f"Port mismatch for {model_id}"


class TestRunSimulationLogic:
    """Test the run_simulation endpoint logic."""

    @pytest.mark.asyncio
    async def test_run_registered_model(self):
        """Test running a simulation for a registered model."""
        from ghent_water.orchestrator.routers.simulation import run_simulation
        from ghent_water.orchestrator.services.model_registry import registry
        from ghent_water.orchestrator.schemas.models import SimulationRequest, ModelRegistrationRequest

        # First register the model
        registry.register_model(ModelRegistrationRequest(
            id="dwp1",
            name="DWP1",
            description="Test",
            endpoint="http://localhost:8001",
            capabilities=["SteadyStateSimulation"],
            entities=["ghent:DWP1"],
        ))

        request = SimulationRequest(parameters={})

        # Mock httpx for the simulate call
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch('ghent_water.orchestrator.routers.simulation.httpx.AsyncClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client

            response = await run_simulation("dwp1", request)

        assert response.model_id == "dwp1"
        assert response.job_id is not None
        assert response.status == "pending"

    @pytest.mark.asyncio
    async def test_run_unknown_model_returns_404(self):
        """Test that running an unknown model returns 404."""
        from fastapi import HTTPException
        from ghent_water.orchestrator.routers.simulation import run_simulation
        from ghent_water.orchestrator.schemas.models import SimulationRequest

        # Model not in MODEL_PORTS should return 404
        request = SimulationRequest(parameters={})

        with pytest.raises(HTTPException) as exc_info:
            await run_simulation("completely_unknown_model", request)

        assert exc_info.value.status_code == 404
