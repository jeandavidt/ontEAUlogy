"""Tests for the MBR model service."""

import pytest
from fastapi.testclient import TestClient

from household_water.models.mbr import app, MBRModel


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["model"] == "Membrane_bioreactor"


def test_describe_json_ld(client):
    resp = client.get("/describe")
    assert resp.status_code == 200
    data = resp.json()
    assert "@context" in data
    assert "@graph" in data
    graph = data["@graph"]
    assert len(graph) > 0
    assert "wf:SimulationModel" in graph[0].get("@type", "")


def test_describe_turtle_valid(client):
    resp = client.get("/describe/turtle")
    assert resp.status_code == 200
    assert "text/turtle" in resp.headers["content-type"]
    # Must contain SimulationModel triple
    assert "wf:SimulationModel" in resp.text
    assert "Membrane_bioreactor" in resp.text


def test_describe_agent_turtle(client):
    resp = client.get("/describe/agent")
    assert resp.status_code == 200
    ttl = resp.text
    assert "wf:SimulationAgent" in ttl
    assert "wf:Operation" in ttl
    assert "/simulate" in ttl


def test_simulate_defaults(client):
    resp = client.post("/simulate", json={})
    assert resp.status_code == 200
    data = resp.json()
    assert data["effluent_flow_m3d"] > 0
    assert data["effluent_cod_mg_l"] >= 0
    assert data["energy_kwh_d"] > 0
    assert data["sludge_kg_d"] >= 0
    assert 0.0 <= data["recovery_fraction"] <= 1.0


def test_simulate_custom_inputs(client):
    payload = {
        "influent_flow_m3d": 2.0,
        "influent_cod_mg_l": 400.0,
        "influent_bod_mg_l": 220.0,
        "influent_tss_mg_l": 180.0,
        "influent_nh4_mg_l": 60.0,
        "influent_tp_mg_l": 10.0,
    }
    resp = client.post("/simulate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    # Higher flow → higher energy
    assert data["energy_kwh_d"] > 0
    # COD removal: effluent must be < influent
    assert data["effluent_cod_mg_l"] < 400.0


def test_simulate_mass_balance(client):
    """Effluent COD must reflect removal fraction applied to influent."""
    payload = {"influent_flow_m3d": 1.5, "influent_cod_mg_l": 350.0}
    resp = client.post("/simulate", json=payload)
    data = resp.json()
    # 95% removal → effluent ≈ 350 * 0.05 = 17.5 mg/L
    assert abs(data["effluent_cod_mg_l"] - 17.5) < 1.0


def test_state_after_simulate(client):
    client.post("/simulate", json={})
    resp = client.get("/state")
    assert resp.status_code == 200
    data = resp.json()
    assert "outputs" in data
    assert data["model"] == "Membrane_bioreactor"
