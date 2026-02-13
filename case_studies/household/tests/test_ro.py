"""Tests for the RO model service."""

import pytest
from fastapi.testclient import TestClient

from household_water.models.ro import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"
    assert resp.json()["model"] == "Reverse_osmosis"


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
    assert "Reverse_osmosis" in resp.text


def test_describe_agent_turtle(client):
    resp = client.get("/describe/agent")
    ttl = resp.text
    assert "wf:SimulationAgent" in ttl
    assert "wf:Operation" in ttl


def test_simulate_defaults(client):
    resp = client.post("/simulate", json={})
    assert resp.status_code == 200
    data = resp.json()
    assert data["permeate_flow_m3d"] > 0
    assert data["concentrate_flow_m3d"] > 0
    assert 0.0 <= data["recovery_fraction"] <= 1.0
    assert data["energy_kwh_d"] > 0


def test_simulate_mass_balance(client):
    """Permeate + concentrate must sum to feed flow."""
    payload = {"feed_flow_m3d": 1.0, "feed_tds_mg_l": 100.0, "feed_conductivity_us_cm": 200.0}
    resp = client.post("/simulate", json=payload)
    data = resp.json()
    total = data["permeate_flow_m3d"] + data["concentrate_flow_m3d"]
    assert abs(total - 1.0) < 0.001


def test_simulate_recovery_fraction(client):
    """Default recovery must be 0.75."""
    resp = client.post("/simulate", json={"feed_flow_m3d": 1.0})
    data = resp.json()
    assert data["recovery_fraction"] == pytest.approx(0.75)
    assert data["permeate_flow_m3d"] == pytest.approx(0.75, rel=0.01)
    assert data["concentrate_flow_m3d"] == pytest.approx(0.25, rel=0.01)


def test_simulate_tds_rejection(client):
    """Permeate TDS must reflect 99% rejection."""
    payload = {"feed_flow_m3d": 1.0, "feed_tds_mg_l": 200.0}
    resp = client.post("/simulate", json=payload)
    data = resp.json()
    # 1% passes through: 200 * 0.01 = 2 mg/L
    assert abs(data["permeate_tds_mg_l"] - 2.0) < 0.1


def test_state_after_simulate(client):
    client.post("/simulate", json={})
    resp = client.get("/state")
    assert resp.status_code == 200
    assert "outputs" in resp.json()
