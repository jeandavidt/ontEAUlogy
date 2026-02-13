"""Reverse Osmosis (RO) model service — port 8102.

Treats rainwater feed from rainwater storage tank.
Uses default recovery=0.75, rejection=0.99 per plan spec.
"""

import logging
from typing import Any, Dict

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .base import BaseHouseholdModel

logger = logging.getLogger(__name__)


class ROInput(BaseModel):
    feed_flow_m3d: float = Field(default=0.8, ge=0, description="Feed flow rate (m³/d)")
    feed_tds_mg_l: float = Field(default=100.0, ge=0, description="Feed TDS (mg/L)")
    feed_turbidity_ntu: float = Field(default=1.0, ge=0, description="Feed turbidity (NTU)")
    feed_conductivity_us_cm: float = Field(default=200.0, ge=0, description="Feed conductivity (µS/cm)")


class ROOutput(BaseModel):
    permeate_flow_m3d: float
    concentrate_flow_m3d: float
    permeate_tds_mg_l: float
    permeate_conductivity_us_cm: float
    recovery_fraction: float
    energy_kwh_d: float


_RECOVERY = 0.75       # 75% water recovery
_TDS_REJECTION = 0.99  # 99% TDS rejection
_CONDUCTIVITY_REJECTION = 0.98
# Energy: ~0.3 kWh/m³ permeate for low-pressure RO (rainwater)
_ENERGY_KWH_PER_M3_PERMEATE = 0.3


class ROModel(BaseHouseholdModel):
    """Reverse Osmosis rainwater treatment model."""

    def __init__(self):
        super().__init__(
            entity_id="Reverse_osmosis",
            entity_name="Reverse Osmosis Unit",
            entity_type="SimulationModel",
            port=8102,
            capabilities=["SteadyStateSimulation", "MassBalance", "WaterQualityPrediction"],
            inputs=[
                {"name": "feed_flow_m3d", "unit": "m³/d"},
                {"name": "feed_tds_mg_l", "unit": "mg/L"},
                {"name": "feed_turbidity_ntu", "unit": "NTU"},
                {"name": "feed_conductivity_us_cm", "unit": "µS/cm"},
            ],
            outputs=[
                {"name": "permeate_flow_m3d", "unit": "m³/d"},
                {"name": "concentrate_flow_m3d", "unit": "m³/d"},
                {"name": "permeate_tds_mg_l", "unit": "mg/L"},
                {"name": "permeate_conductivity_us_cm", "unit": "µS/cm"},
                {"name": "recovery_fraction", "unit": "-"},
                {"name": "energy_kwh_d", "unit": "kWh/d"},
            ],
        )

    async def describe(self) -> Dict[str, Any]:
        return {
            "@context": {
                "wf": "https://ugentbiomath.github.io/waterframe#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            },
            "@graph": [
                {
                    "@id": self.model_iri,
                    "@type": "wf:SimulationModel",
                    "rdfs:label": self.entity_name,
                    "rdfs:comment": "RO model for household rainwater purification",
                    "wf:representsEntity": {"@id": self.entity_iri},
                    "wf:apiEndpoint": self.api_endpoint,
                    "wf:port": self.port,
                }
            ],
        }

    async def simulate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        q_feed = float(inputs.get("feed_flow_m3d", 0.8))
        tds_feed = float(inputs.get("feed_tds_mg_l", 100.0))
        cond_feed = float(inputs.get("feed_conductivity_us_cm", 200.0))

        q_permeate = q_feed * _RECOVERY
        q_concentrate = q_feed - q_permeate

        # Mass balance for TDS: permeate concentration = feed × (1 - rejection)
        tds_permeate = tds_feed * (1 - _TDS_REJECTION)
        cond_permeate = cond_feed * (1 - _CONDUCTIVITY_REJECTION)

        energy = q_permeate * _ENERGY_KWH_PER_M3_PERMEATE

        result = {
            "permeate_flow_m3d": round(q_permeate, 4),
            "concentrate_flow_m3d": round(q_concentrate, 4),
            "permeate_tds_mg_l": round(tds_permeate, 3),
            "permeate_conductivity_us_cm": round(cond_permeate, 2),
            "recovery_fraction": _RECOVERY,
            "energy_kwh_d": round(energy, 3),
        }
        self._update_state(result)
        return result


# ── FastAPI app ──────────────────────────────────────────────────────────────

_model = ROModel()
app = FastAPI(
    title="Household RO Model",
    description="Reverse Osmosis rainwater treatment service",
    version="1.0.0",
)


@app.get("/health")
async def health():
    return await _model.health_check()


@app.get("/describe")
async def describe():
    return await _model.describe()


@app.get("/describe/turtle")
async def describe_turtle():
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(_model.generate_ttl_description(), media_type="text/turtle")


@app.get("/describe/agent")
async def describe_agent():
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(_model.generate_agent_ttl(), media_type="text/turtle")


@app.post("/simulate", response_model=ROOutput)
async def simulate(body: ROInput):
    return await _model.simulate(body.model_dump())


@app.get("/state")
async def state():
    return await _model.get_state()
