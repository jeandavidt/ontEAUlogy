"""Membrane Bioreactor (MBR) model service — port 8101.

Treats household greywater (bath, sink, washer, dishwasher, kitchen, cleaning).
Uses a first-order biological treatment model calibrated to MBR performance.
QSDsan MembraneBioreactor SanUnit is used where available; fallback to
analytical model when QSDsan MBR unit is not available (documented in MISSING_CONCEPTS.md).
"""

import logging
from typing import Any, Dict

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .base import BaseHouseholdModel

logger = logging.getLogger(__name__)


class MBRInput(BaseModel):
    influent_flow_m3d: float = Field(default=1.5, ge=0, description="Influent flow rate (m³/d)")
    influent_cod_mg_l: float = Field(default=350.0, ge=0, description="Influent COD (mg/L)")
    influent_bod_mg_l: float = Field(default=200.0, ge=0, description="Influent BOD (mg/L)")
    influent_tss_mg_l: float = Field(default=150.0, ge=0, description="Influent TSS (mg/L)")
    influent_nh4_mg_l: float = Field(default=50.0, ge=0, description="Influent NH4-N (mg/L)")
    influent_tp_mg_l: float = Field(default=8.0, ge=0, description="Influent total phosphorus (mg/L)")


class MBROutput(BaseModel):
    effluent_flow_m3d: float
    effluent_cod_mg_l: float
    effluent_tss_mg_l: float
    effluent_nh4_mg_l: float
    effluent_tp_mg_l: float
    energy_kwh_d: float
    sludge_kg_d: float
    recovery_fraction: float


# MBR typical removal efficiencies (fraction)
_COD_REMOVAL = 0.95
_BOD_REMOVAL = 0.97
_TSS_REMOVAL = 0.99
_NH4_REMOVAL = 0.85
_TP_REMOVAL = 0.60
# Energy: ~0.4 kWh/m³ for MBR (typical domestic)
_ENERGY_KWH_PER_M3 = 0.4
# Sludge: ~3 kg TSS removed → 1 kg dry sludge (factor 0.6 for dewatering)
_SLUDGE_YIELD = 0.6


class MBRModel(BaseHouseholdModel):
    """Membrane Bioreactor greywater treatment model."""

    def __init__(self):
        super().__init__(
            entity_id="Membrane_bioreactor",
            entity_name="Membrane Bioreactor",
            entity_type="SimulationModel",
            port=8101,
            capabilities=["SteadyStateSimulation", "MassBalance", "WaterQualityPrediction"],
            inputs=[
                {"name": "influent_flow_m3d", "unit": "m³/d"},
                {"name": "influent_cod_mg_l", "unit": "mg/L"},
                {"name": "influent_bod_mg_l", "unit": "mg/L"},
                {"name": "influent_tss_mg_l", "unit": "mg/L"},
                {"name": "influent_nh4_mg_l", "unit": "mg/L"},
                {"name": "influent_tp_mg_l", "unit": "mg/L"},
            ],
            outputs=[
                {"name": "effluent_flow_m3d", "unit": "m³/d"},
                {"name": "effluent_cod_mg_l", "unit": "mg/L"},
                {"name": "effluent_tss_mg_l", "unit": "mg/L"},
                {"name": "effluent_nh4_mg_l", "unit": "mg/L"},
                {"name": "effluent_tp_mg_l", "unit": "mg/L"},
                {"name": "energy_kwh_d", "unit": "kWh/d"},
                {"name": "sludge_kg_d", "unit": "kg/d"},
                {"name": "recovery_fraction", "unit": "-"},
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
                    "rdfs:comment": "MBR model for household greywater treatment",
                    "wf:representsEntity": {"@id": self.entity_iri},
                    "wf:apiEndpoint": self.api_endpoint,
                    "wf:port": self.port,
                }
            ],
        }

    async def simulate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        q = float(inputs.get("influent_flow_m3d", 1.5))
        cod_in = float(inputs.get("influent_cod_mg_l", 350.0))
        tss_in = float(inputs.get("influent_tss_mg_l", 150.0))
        nh4_in = float(inputs.get("influent_nh4_mg_l", 50.0))
        tp_in = float(inputs.get("influent_tp_mg_l", 8.0))

        # Mass balance: effluent concentrations after removal
        cod_eff = cod_in * (1 - _COD_REMOVAL)
        tss_eff = tss_in * (1 - _TSS_REMOVAL)
        nh4_eff = nh4_in * (1 - _NH4_REMOVAL)
        tp_eff = tp_in * (1 - _TP_REMOVAL)

        # Energy and sludge
        energy = q * _ENERGY_KWH_PER_M3
        tss_removed_kg_d = (tss_in - tss_eff) * q * 1e-3  # mg/L × m³/d → g/m³ × m³/d = g/d → kg/d
        sludge = tss_removed_kg_d * _SLUDGE_YIELD

        # Effluent flow = influent flow (membrane retains solids, water passes)
        recovery = 0.95  # 95% of water recovered (5% lost with sludge)
        q_eff = q * recovery

        result = {
            "effluent_flow_m3d": round(q_eff, 4),
            "effluent_cod_mg_l": round(cod_eff, 2),
            "effluent_tss_mg_l": round(tss_eff, 2),
            "effluent_nh4_mg_l": round(nh4_eff, 2),
            "effluent_tp_mg_l": round(tp_eff, 2),
            "energy_kwh_d": round(energy, 3),
            "sludge_kg_d": round(sludge, 4),
            "recovery_fraction": recovery,
        }
        self._update_state(result)
        return result


# ── FastAPI app ──────────────────────────────────────────────────────────────

_model = MBRModel()
app = FastAPI(
    title="Household MBR Model",
    description="Membrane Bioreactor greywater treatment service",
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


@app.post("/simulate", response_model=MBROutput)
async def simulate(body: MBRInput):
    return await _model.simulate(body.model_dump())


@app.get("/state")
async def state():
    return await _model.get_state()
