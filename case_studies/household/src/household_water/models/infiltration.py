"""Infiltration model service — port 8103.

Receives blackwater from blackwater storage + purified greywater overflow.
QSDsan has no native Infiltration SanUnit; uses a first-order soil treatment
model (documented in MISSING_CONCEPTS.md under Gap INF-01).
"""

import logging
from typing import Any, Dict

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .base import BaseHouseholdModel

logger = logging.getLogger(__name__)


class InfiltrationInput(BaseModel):
    influent_flow_m3d: float = Field(default=0.3, ge=0, description="Influent flow rate (m³/d)")
    influent_cod_mg_l: float = Field(default=200.0, ge=0, description="Influent COD (mg/L)")
    influent_tss_mg_l: float = Field(default=50.0, ge=0, description="Influent TSS (mg/L)")
    influent_nh4_mg_l: float = Field(default=40.0, ge=0, description="Influent NH4-N (mg/L)")


class InfiltrationOutput(BaseModel):
    infiltrated_flow_m3d: float
    removed_cod_fraction: float
    removed_tss_fraction: float
    removed_nh4_fraction: float


# Infiltration/soil treatment removal fractions
# Based on literature values for subsurface soil infiltration systems
# (Crites & Tchobanoglous, Small and Decentralized Wastewater Management Systems)
_COD_REMOVAL = 0.70   # 70% COD removal in soil
_TSS_REMOVAL = 0.90   # 90% TSS removal (physical filtration)
_NH4_REMOVAL = 0.55   # 55% NH4 removal (nitrification in soil varies widely)


class InfiltrationModel(BaseHouseholdModel):
    """Subsurface infiltration treatment model (first-order soil removal)."""

    def __init__(self):
        super().__init__(
            entity_id="Infiltration",
            entity_name="Infiltration Unit",
            entity_type="SimulationModel",
            port=8103,
            capabilities=["SteadyStateSimulation", "MassBalance"],
            inputs=[
                {"name": "influent_flow_m3d", "unit": "m³/d"},
                {"name": "influent_cod_mg_l", "unit": "mg/L"},
                {"name": "influent_tss_mg_l", "unit": "mg/L"},
                {"name": "influent_nh4_mg_l", "unit": "mg/L"},
            ],
            outputs=[
                {"name": "infiltrated_flow_m3d", "unit": "m³/d"},
                {"name": "removed_cod_fraction", "unit": "-"},
                {"name": "removed_tss_fraction", "unit": "-"},
                {"name": "removed_nh4_fraction", "unit": "-"},
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
                    "rdfs:comment": "Infiltration/soil treatment model for household blackwater disposal",
                    "wf:representsEntity": {"@id": self.entity_iri},
                    "wf:apiEndpoint": self.api_endpoint,
                    "wf:port": self.port,
                }
            ],
        }

    async def simulate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        q = float(inputs.get("influent_flow_m3d", 0.3))
        # All flow infiltrates into the soil (no surface discharge)
        result = {
            "infiltrated_flow_m3d": round(q, 4),
            "removed_cod_fraction": _COD_REMOVAL,
            "removed_tss_fraction": _TSS_REMOVAL,
            "removed_nh4_fraction": _NH4_REMOVAL,
        }
        self._update_state(result)
        return result


# ── FastAPI app ──────────────────────────────────────────────────────────────

_model = InfiltrationModel()
app = FastAPI(
    title="Household Infiltration Model",
    description="Subsurface infiltration treatment service",
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


@app.post("/simulate", response_model=InfiltrationOutput)
async def simulate(body: InfiltrationInput):
    return await _model.simulate(body.model_dump())


@app.get("/state")
async def state():
    return await _model.get_state()
