"""Tests for semantic I/O serialization and parsing."""
import sys
sys.path.insert(0, "/Users/jeandavidt/Developer/jeandavidt/ontEAUlogy/case_studies/household/src")

import pytest
from rdflib import Graph

from household_water.semantic.namespaces import WF, CASE, MBR_VAR_IRIS
from household_water.semantic.io_serializer import serialize_outputs_to_turtle, params_to_turtle
from household_water.semantic.io_parser import parse_turtle_to_dict


def test_serialize_outputs_basic():
    outputs = {"effluent_cod_mg_l": 17.5, "energy_kwh_d": 0.6}
    ttl = serialize_outputs_to_turtle(outputs, "Membrane_bioreactor", MBR_VAR_IRIS, "steady_state")
    g = Graph()
    g.parse(data=ttl, format="turtle")
    assert any(str(o) == str(WF.SimulationRun) for s, p, o in g)


def test_serialize_includes_scenario():
    outputs = {"effluent_cod_mg_l": 17.5}
    scenario = "https://example.org/Baseline"
    ttl = serialize_outputs_to_turtle(outputs, "Membrane_bioreactor", MBR_VAR_IRIS, scenario_iri=scenario)
    assert scenario in ttl


def test_serialize_default_scenario():
    outputs = {"effluent_cod_mg_l": 17.5}
    ttl = serialize_outputs_to_turtle(outputs, "Membrane_bioreactor", MBR_VAR_IRIS)
    assert "Baseline_Scenario" in ttl


def test_params_to_turtle():
    params = {"mu_max": 6.0, "K_s": 20.0}
    ttl = params_to_turtle("Membrane_bioreactor", params)
    g = Graph()
    g.parse(data=ttl, format="turtle")
    assert len(list(g)) > 0


def test_parse_turtle_roundtrip():
    outputs = {"effluent_cod_mg_l": 17.5, "energy_kwh_d": 0.6}
    ttl = serialize_outputs_to_turtle(outputs, "Membrane_bioreactor", MBR_VAR_IRIS)
    g = Graph()
    g.parse(data=ttl, format="turtle")
    assert len(list(g)) > 0
