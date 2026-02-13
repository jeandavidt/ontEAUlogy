"""Tests for the Infiltration model service."""

import pytest
from fastapi.testclient import TestClient

from household_water.models.infiltration import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"
    assert resp.json()["model"] == "Infiltration"


def test_describe_json_ld(client):
    resp = client.get("/describe")
    assert resp.status_code == 200
    data = resp.json()
    assert "@graph" in data
    assert "wf:SimulationModel" in data["@graph"][0].get("@type", "")


def test_describe_turtle_valid(client):
    resp = client.get("/describe/turtle")
    assert resp.status_code == 200
    assert "wf:SimulationModel" in resp.text
    assert "Infiltration" in resp.text


def test_describe_agent_turtle(client):
    resp = client.get("/describe/agent")
    ttl = resp.text
    assert "wf:SimulationAgent" in ttl
    assert "wf:Operation" in ttl


def test_simulate_defaults(client):
    resp = client.post("/simulate", json={})
    assert resp.status_code == 200
    data = resp.json()
    assert data["infiltrated_flow_m3d"] > 0


def test_simulate_removal_fractions_in_range(client):
    """All removal fractions must be in [0, 1]."""
    resp = client.post("/simulate", json={
        "influent_flow_m3d": 0.5,
        "influent_cod_mg_l": 300.0,
        "influent_tss_mg_l": 80.0,
        "influent_nh4_mg_l": 50.0,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert 0.0 <= data["removed_cod_fraction"] <= 1.0
    assert 0.0 <= data["removed_tss_fraction"] <= 1.0
    assert 0.0 <= data["removed_nh4_fraction"] <= 1.0


def test_simulate_flow_conservation(client):
    """Infiltrated flow must equal influent (all water absorbed into soil)."""
    payload = {"influent_flow_m3d": 0.4}
    resp = client.post("/simulate", json=payload)
    data = resp.json()
    assert abs(data["infiltrated_flow_m3d"] - 0.4) < 0.001


def test_state_after_simulate(client):
    client.post("/simulate", json={})
    resp = client.get("/state")
    assert resp.status_code == 200
    assert "outputs" in resp.json()
