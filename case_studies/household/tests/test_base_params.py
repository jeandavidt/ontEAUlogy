"""Tests for BaseHouseholdModel parameter management additions."""

from typing import Any, Dict

import pytest
from rdflib import Graph, Namespace

from household_water.models.base import BaseHouseholdModel


# ---------------------------------------------------------------------------
# Minimal concrete subclass used only in these tests
# ---------------------------------------------------------------------------

class _MinimalModel(BaseHouseholdModel):
    """Concrete subclass that satisfies the abstract interface."""

    _default_params: Dict[str, float] = {"mu_max": 6.0, "k_s": 0.1}
    _PARAM_BOUNDS: Dict[str, tuple] = {
        "mu_max": (1.0, 10.0),
        "k_s": (0.01, 1.0),
    }

    async def describe(self) -> Dict[str, Any]:
        return {"id": self.entity_id}

    async def simulate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return {}


@pytest.fixture()
def model() -> _MinimalModel:
    return _MinimalModel(
        entity_id="test_mbr",
        entity_name="Test MBR",
        entity_type="MBR",
        port=8001,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGetDefaultParamsDict:
    def test_returns_expected_dict(self, model: _MinimalModel) -> None:
        result = model.get_default_params_dict()
        assert result == {"mu_max": 6.0, "k_s": 0.1}

    def test_returns_copy_not_reference(self, model: _MinimalModel) -> None:
        result = model.get_default_params_dict()
        result["mu_max"] = 999.0
        # Class-level default must be unchanged.
        assert _MinimalModel._default_params["mu_max"] == 6.0


class TestUpdateParameters:
    def test_updates_instance_parameters(self, model: _MinimalModel) -> None:
        model.update_parameters({"mu_max": 8.0})
        assert model._parameters["mu_max"] == 8.0

    def test_does_not_touch_other_params(self, model: _MinimalModel) -> None:
        model.update_parameters({"mu_max": 8.0})
        assert model._parameters["k_s"] == pytest.approx(0.1)

    def test_adds_new_param(self, model: _MinimalModel) -> None:
        model.update_parameters({"new_param": 42.0})
        assert model._parameters["new_param"] == 42.0

    def test_does_not_mutate_class_defaults(self, model: _MinimalModel) -> None:
        model.update_parameters({"mu_max": 99.0})
        assert _MinimalModel._default_params["mu_max"] == 6.0


class TestGetParamBounds:
    def test_returns_correct_lows_and_highs(self, model: _MinimalModel) -> None:
        lows, highs = model.get_param_bounds(["mu_max", "k_s"])
        assert lows == [1.0, 0.01]
        assert highs == [10.0, 1.0]

    def test_single_param(self, model: _MinimalModel) -> None:
        lows, highs = model.get_param_bounds(["mu_max"])
        assert lows == [1.0]
        assert highs == [10.0]

    def test_missing_param_raises_key_error(self, model: _MinimalModel) -> None:
        with pytest.raises(KeyError):
            model.get_param_bounds(["nonexistent"])

    def test_order_matches_names(self, model: _MinimalModel) -> None:
        lows1, highs1 = model.get_param_bounds(["mu_max", "k_s"])
        lows2, highs2 = model.get_param_bounds(["k_s", "mu_max"])
        assert lows1 == [1.0, 0.01]
        assert lows2 == [0.01, 1.0]
        assert highs1 == [10.0, 1.0]
        assert highs2 == [1.0, 10.0]


class TestParamsToTurtle:
    _WF = Namespace("https://ugentbiomath.github.io/waterframe#")

    def _parse(self, ttl: str) -> Graph:
        g = Graph()
        g.parse(data=ttl, format="turtle")
        return g

    def test_produces_valid_turtle(self, model: _MinimalModel) -> None:
        ttl = model.params_to_turtle({"mu_max": 6.0})
        g = self._parse(ttl)
        assert len(g) > 0

    def test_contains_wf_parameter_type(self, model: _MinimalModel) -> None:
        ttl = model.params_to_turtle({"mu_max": 6.0})
        g = self._parse(ttl)
        from rdflib import RDF
        param_nodes = list(g.subjects(RDF.type, self._WF.Parameter))
        assert len(param_nodes) == 1

    def test_one_node_per_param(self, model: _MinimalModel) -> None:
        ttl = model.params_to_turtle({"mu_max": 6.0, "k_s": 0.1})
        g = self._parse(ttl)
        from rdflib import RDF
        param_nodes = list(g.subjects(RDF.type, self._WF.Parameter))
        assert len(param_nodes) == 2

    def test_parameter_name_literal_present(self, model: _MinimalModel) -> None:
        from rdflib import Literal, RDF
        ttl = model.params_to_turtle({"mu_max": 6.0})
        g = self._parse(ttl)
        names = {
            str(o)
            for s in g.subjects(RDF.type, self._WF.Parameter)
            for o in g.objects(s, self._WF.parameterName)
        }
        assert "mu_max" in names

    def test_empty_params_produces_parseable_turtle(self, model: _MinimalModel) -> None:
        ttl = model.params_to_turtle({})
        g = self._parse(ttl)
        # An empty graph is still valid Turtle.
        assert isinstance(g, Graph)
