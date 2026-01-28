"""Tests for model runner - MODEL_REGISTRY validation.

These tests ensure consistency between MODEL_REGISTRY in model_runner.py
and MODEL_PORTS in simulation.py.
"""
import pytest
from unittest.mock import patch, MagicMock


class TestModelRegistryConfiguration:
    """Test MODEL_REGISTRY configuration in model_runner.py."""

    def test_model_registry_contains_lieve_river(self):
        """Verify 'lieve_river' is in MODEL_REGISTRY."""
        from ghent_water.models.runners.model_runner import MODEL_REGISTRY

        assert "lieve_river" in MODEL_REGISTRY, "lieve_river should be in MODEL_REGISTRY"
        name, port, factory = MODEL_REGISTRY["lieve_river"]
        assert name == "Lieve River", "lieve_river should have name 'Lieve River'"
        assert port == 8010, "lieve_river should map to port 8010"

    def test_model_registry_contains_all_expected_models(self):
        """Verify all expected models are in MODEL_REGISTRY."""
        from ghent_water.models.runners.model_runner import MODEL_REGISTRY

        expected_models = [
            "dwp1", "dwp2",  # Drinking Water Plants
            "wwtp1", "wwtp2",  # Wastewater Treatment Plants
            "texfin", "foodpro", "chiptech", "pharmagen", "brewco",  # Industries
            "lieve_river",  # River
            "dampoort", "muide",  # Residential
        ]

        for model in expected_models:
            assert model in MODEL_REGISTRY, f"Model '{model}' should be in MODEL_REGISTRY"

    def test_model_registry_ports_are_unique(self):
        """Verify all ports in MODEL_REGISTRY are unique."""
        from ghent_water.models.runners.model_runner import MODEL_REGISTRY

        ports = [port for _, port, _ in MODEL_REGISTRY.values()]
        assert len(ports) == len(set(ports)), "All ports should be unique"

    def test_model_registry_port_range(self):
        """Verify all ports are in expected range."""
        from ghent_water.models.runners.model_runner import MODEL_REGISTRY

        for model_id, (_, port, _) in MODEL_REGISTRY.items():
            assert 8000 <= port <= 8100, f"Port {port} for {model_id} should be in range 8000-8100"

    def test_model_registry_has_factory_functions(self):
        """Verify all models have valid factory functions."""
        from ghent_water.models.runners.model_runner import MODEL_REGISTRY

        for model_id, (_, port, factory) in MODEL_REGISTRY.items():
            assert callable(factory), f"Model '{model_id}' should have a callable factory"
            assert factory is not None, f"Model '{model_id}' factory should not be None"


class TestCreateModel:
    """Test create_model function."""

    def test_create_lieve_river(self):
        """Test creating lieve_river model."""
        from ghent_water.models.runners.model_runner import create_model

        model = create_model("lieve_river")

        assert model is not None
        assert model.entity_id == "lieve_river"
        assert model.port == 8010

    def test_create_dwp1(self):
        """Test creating dwp1 model."""
        from ghent_water.models.runners.model_runner import create_model

        model = create_model("dwp1")

        assert model is not None
        assert model.entity_id == "dwp1"
        assert model.port == 8001

    def test_create_wwtp2(self):
        """Test creating wwtp2 model."""
        from ghent_water.models.runners.model_runner import create_model

        model = create_model("wwtp2")

        assert model is not None
        assert model.entity_id == "wwtp2"
        assert model.port == 8004

    def test_create_unknown_model_raises_error(self):
        """Test that creating an unknown model raises ValueError."""
        from ghent_water.models.runners.model_runner import create_model

        with pytest.raises(ValueError) as exc_info:
            create_model("unknown_model")

        assert "Unknown model" in str(exc_info.value)
        assert "unknown_model" in str(exc_info.value)

    def test_create_model_case_insensitive(self):
        """Test that model creation is case-insensitive."""
        from ghent_water.models.runners.model_runner import create_model

        model_lower = create_model("dwp1")
        model_upper = create_model("DWP1")

        assert model_lower.entity_id == model_upper.entity_id

    def test_create_model_port_override(self):
        """Test that port can be overridden."""
        from ghent_water.models.runners.model_runner import create_model

        model = create_model("dwp1", port=9000)

        assert model.port == 9000


class TestModelRegistryConsistency:
    """Test consistency between MODEL_REGISTRY and MODEL_PORTS."""

    def test_all_model_runner_models_in_simulation_ports(self):
        """All models in MODEL_REGISTRY should be in MODEL_PORTS."""
        from ghent_water.models.runners.model_runner import MODEL_REGISTRY
        from ghent_water.orchestrator.routers.simulation import MODEL_PORTS

        for model_id in MODEL_REGISTRY.keys():
            assert model_id in MODEL_PORTS, f"Model '{model_id}' from MODEL_REGISTRY not in MODEL_PORTS"

    def test_all_simulation_ports_in_model_runner(self):
        """All models in MODEL_PORTS should be in MODEL_REGISTRY."""
        from ghent_water.models.runners.model_runner import MODEL_REGISTRY
        from ghent_water.orchestrator.routers.simulation import MODEL_PORTS

        for model_id in MODEL_PORTS.keys():
            assert model_id in MODEL_REGISTRY, f"Model '{model_id}' from MODEL_PORTS not in MODEL_REGISTRY"

    def test_ports_match_between_files(self):
        """Verify ports match between MODEL_REGISTRY and MODEL_PORTS."""
        from ghent_water.models.runners.model_runner import MODEL_REGISTRY
        from ghent_water.orchestrator.routers.simulation import MODEL_PORTS

        for model_id in MODEL_REGISTRY.keys():
            _, registry_port, _ = MODEL_REGISTRY[model_id]
            simulation_port = MODEL_PORTS[model_id]
            assert registry_port == simulation_port, \
                f"Port mismatch for {model_id}: MODEL_REGISTRY={registry_port}, MODEL_PORTS={simulation_port}"
