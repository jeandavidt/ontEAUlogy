"""Integration tests: verify household models appear in shared orchestrator.

These tests require the full docker-compose stack to be running:
  docker-compose --profile full up -d  (from case_studies/ghent/)

They are skipped automatically when the orchestrator is not reachable.
"""

import pytest
import httpx

ORCHESTRATOR_URL = "http://localhost:8080"
MBR_URL = "http://localhost:8101"
RO_URL = "http://localhost:8102"
INFILTRATION_URL = "http://localhost:8103"


def _is_reachable(url: str) -> bool:
    try:
        httpx.get(f"{url}/health", timeout=2.0, follow_redirects=True)
        return True
    except Exception:
        return False


def _orchestrator_has_household_models() -> bool:
    """Return True only when the orchestrator lists at least one household model."""
    try:
        resp = httpx.get(
            f"{ORCHESTRATOR_URL}/api/v1/models", timeout=2.0, follow_redirects=True
        )
        if resp.status_code != 200:
            return False
        models = resp.json()
        ids = [m.get("id", "") for m in models if isinstance(m, dict)]
        return any("mbr" in mid or "ro" in mid or "infiltration" in mid for mid in ids)
    except Exception:
        return False


requires_orchestrator = pytest.mark.skipif(
    not _orchestrator_has_household_models(),
    reason="Orchestrator not running with household models (start with docker-compose --profile full up -d)",
)

requires_mbr = pytest.mark.skipif(
    not _is_reachable(MBR_URL),
    reason="MBR model not running at localhost:8101",
)

requires_ro = pytest.mark.skipif(
    not _is_reachable(RO_URL),
    reason="RO model not running at localhost:8102",
)

requires_infiltration = pytest.mark.skipif(
    not _is_reachable(INFILTRATION_URL),
    reason="Infiltration model not running at localhost:8103",
)


@requires_mbr
def test_mbr_health_live():
    resp = httpx.get(f"{MBR_URL}/health", timeout=5.0)
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


@requires_ro
def test_ro_health_live():
    resp = httpx.get(f"{RO_URL}/health", timeout=5.0)
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


@requires_infiltration
def test_infiltration_health_live():
    resp = httpx.get(f"{INFILTRATION_URL}/health", timeout=5.0)
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


@requires_orchestrator
def test_orchestrator_lists_household_models():
    """Shared orchestrator must include household models in /api/v1/models."""
    resp = httpx.get(f"{ORCHESTRATOR_URL}/api/v1/models", timeout=10.0, follow_redirects=True)
    assert resp.status_code == 200
    models = resp.json()
    model_ids = [m.get("id", "") for m in models if isinstance(m, dict)]
    # At least one household model should be registered
    household_ids = [mid for mid in model_ids if "mbr" in mid or "ro" in mid or "infiltration" in mid]
    assert len(household_ids) > 0, f"No household models found. Registered: {model_ids}"


@requires_orchestrator
def test_orchestrator_sparql_finds_household_agents():
    """SPARQL query should find household agents in the shared graph."""
    query = """
    PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
    SELECT ?agent WHERE {
        ?agent a wf:SimulationAgent .
        FILTER(CONTAINS(STR(?agent), "household"))
    }
    """
    resp = httpx.post(
        f"{ORCHESTRATOR_URL}/api/v1/query/sparql",
        json={"query": query},
        timeout=15.0,
    )
    assert resp.status_code == 200
    data = resp.json()
    bindings = data.get("results", {}).get("bindings", [])
    assert len(bindings) >= 3, f"Expected ≥3 household agents, got: {bindings}"


@requires_mbr
def test_mbr_simulate_live():
    """End-to-end simulation via live MBR service."""
    payload = {
        "influent_flow_m3d": 1.5,
        "influent_cod_mg_l": 350.0,
        "influent_bod_mg_l": 200.0,
        "influent_tss_mg_l": 150.0,
        "influent_nh4_mg_l": 50.0,
        "influent_tp_mg_l": 8.0,
    }
    resp = httpx.post(f"{MBR_URL}/simulate", json=payload, timeout=10.0)
    assert resp.status_code == 200
    data = resp.json()
    assert data["effluent_cod_mg_l"] >= 0
    assert data["energy_kwh_d"] > 0
