"""Reverse Osmosis (RO) model service — port 8102.

Treats rainwater feed from rainwater storage tank.
Physics-based implementation using solution-diffusion model with concentration
polarisation (ro_equations.py). Content negotiation for Turtle/JSON-LD output.
Calibration via scipy least_squares with Jacobian-based uncertainty estimation.

Backward compatibility: the legacy /simulate endpoint preserves the fixed
recovery=0.75, rejection=0.99 behaviour tested in test_ro.py.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

import numpy as np
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel, Field
from scipy.optimize import least_squares

from .base import BaseHouseholdModel
from ..physics.ro_equations import (
    ro_simulate_steady,
    ro_simulate_dynamic,
    RO_DEFAULT_PARAMS,
)
from ..schemas.common import (
    CalibrationObservation,
    CalibrationRequest,
    CalibrationResult,
    SimulationMode,
    DynamicConfig,
    CompositionRequest,
)
from ..schemas.ro_schemas import (
    ROInput,
    ROParameters,
    ROSteadyOutput,
    RODynamicOutput,
)
from ..semantic.io_serializer import (
    serialize_outputs_to_turtle,
    params_to_turtle as _params_to_turtle_helper,
)
from ..semantic.namespaces import RO_VAR_IRIS
from ..composition.cascade import cascade_simulate
from ..composition.lumped import lumped_simulate
from ..composition.assembly import assemble_and_solve

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Legacy schemas (kept for backward compatibility with test_ro.py)
# ---------------------------------------------------------------------------


class _LegacyROInput(BaseModel):
    """Minimal input schema matching the original stub endpoint."""

    feed_flow_m3d: float = Field(default=0.8, ge=0, description="Feed flow rate (m³/d)")
    feed_tds_mg_l: float = Field(default=100.0, ge=0, description="Feed TDS (mg/L)")
    feed_turbidity_ntu: float = Field(
        default=1.0, ge=0, description="Feed turbidity (NTU)"
    )
    feed_conductivity_us_cm: float = Field(
        default=200.0, ge=0, description="Feed conductivity (µS/cm)"
    )


class _LegacyROOutput(BaseModel):
    permeate_flow_m3d: float
    concentrate_flow_m3d: float
    permeate_tds_mg_l: float
    permeate_conductivity_us_cm: float
    recovery_fraction: float
    energy_kwh_d: float


# Legacy fixed-ratio constants (preserve test_ro.py expectations)
_RECOVERY = 0.75
_TDS_REJECTION = 0.99
_CONDUCTIVITY_REJECTION = 0.98
_ENERGY_KWH_PER_M3_PERMEATE = 0.3


# ---------------------------------------------------------------------------
# ROModel
# ---------------------------------------------------------------------------


class ROModel(BaseHouseholdModel):
    """Reverse Osmosis rainwater treatment model with physics engine.

    The solution-diffusion model with iterative concentration polarisation
    is implemented in ``ro_equations.py``. This class wires it to the
    FastAPI service, adds parameter management, calibration, and semantic
    output serialisation.
    """

    _PARAM_BOUNDS: Dict[str, Tuple[float, float]] = {
        "A": (1e-9, 1e-5),  # water permeability m/(s·Pa)
        "B": (1e-10, 1e-4),  # salt permeability m/s
        "k_m": (1e-6, 1e-3),  # mass transfer coefficient m/s
    }
    _default_params: Dict[str, float] = {
        "A": 5e-7,
        "B": 1e-7,
        "k_m": 5e-5,
    }

    def __init__(self) -> None:
        super().__init__(
            entity_id="Reverse_osmosis",
            entity_name="Reverse Osmosis Unit",
            entity_type="SimulationModel",
            port=8102,
            capabilities=[
                "SteadyStateSimulation",
                "DynamicSimulation",
                "MassBalance",
                "WaterQualityPrediction",
                "Calibration",
            ],
            inputs=[
                {"name": "feed_flow_m3d", "unit": "m³/d"},
                {"name": "feed_tds_mg_l", "unit": "mg/L"},
                {"name": "feed_turbidity_ntu", "unit": "NTU"},
                {"name": "feed_conductivity_us_cm", "unit": "µS/cm"},
                {"name": "applied_pressure_bar", "unit": "bar"},
                {"name": "membrane_area_m2", "unit": "m²"},
            ],
            outputs=[
                {"name": "permeate_flow_m3d", "unit": "m³/d"},
                {"name": "concentrate_flow_m3d", "unit": "m³/d"},
                {"name": "permeate_tds_mg_l", "unit": "mg/L"},
                {"name": "permeate_conductivity_us_cm", "unit": "µS/cm"},
                {"name": "recovery_fraction", "unit": "-"},
                {"name": "energy_kwh_d", "unit": "kWh/d"},
                {"name": "water_flux_m_s", "unit": "m/s"},
                {"name": "osmotic_pressure_pa", "unit": "Pa"},
            ],
        )

    # ------------------------------------------------------------------
    # Physics simulation (synchronous)
    # ------------------------------------------------------------------

    def simulate_sync(
        self,
        inputs: Dict[str, Any],
        params_override: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Run the physics-based RO simulation synchronously.

        Args:
            inputs: Model inputs; keys match ``ROInput`` field names.
            params_override: Optional parameter overrides for this call only.

        Returns:
            Output dictionary matching ``ROSteadyOutput`` or
            ``RODynamicOutput`` fields depending on ``simulation_mode``.
        """
        # Build effective params: defaults → instance → override
        effective_params: Dict[str, float] = {
            **RO_DEFAULT_PARAMS,
            **self._parameters,
            **(params_override or {}),
        }

        mode = inputs.get("simulation_mode", SimulationMode.steady_state)
        if isinstance(mode, str):
            mode = SimulationMode(mode)

        if mode == SimulationMode.dynamic:
            dyn_cfg = inputs.get("dynamic_config") or {}
            if hasattr(dyn_cfg, "model_dump"):
                dyn_cfg = dyn_cfg.model_dump()
            dyn_inputs = {**inputs, **dyn_cfg}
            return ro_simulate_dynamic(dyn_inputs, effective_params)

        return ro_simulate_steady(inputs, effective_params)

    # ------------------------------------------------------------------
    # Calibration
    # ------------------------------------------------------------------

    def calibrate(self, request: CalibrationRequest) -> CalibrationResult:
        """Calibrate model parameters using scipy least_squares.

        Args:
            request: Calibration specification with observations and
                parameter names to fit.

        Returns:
            ``CalibrationResult`` with fitted parameters, uncertainties,
            residual norm, convergence flag, and semantic Turtle.
        """
        params_to_fit: List[str] = request.parameters_to_fit
        if not params_to_fit:
            raise ValueError("parameters_to_fit must not be empty")

        lows, highs = self.get_param_bounds(params_to_fit)
        x0 = [self._parameters.get(n, self._default_params[n]) for n in params_to_fit]

        def _residuals(x: np.ndarray) -> np.ndarray:
            override = dict(zip(params_to_fit, x))
            res_list: List[float] = []
            for obs in request.observations:
                out = self.simulate_sync(dict(obs.inputs), params_override=override)
                for key, obs_val in obs.observed_outputs.items():
                    pred = out.get(key, 0.0)
                    # Normalise by observed value to scale residuals
                    scale = abs(obs_val) if abs(obs_val) > 1e-12 else 1.0
                    res_list.append((pred - obs_val) / scale)
            return np.array(res_list)

        result = least_squares(
            _residuals,
            x0,
            bounds=(lows, highs),
            method="trf",
            ftol=1e-9,
            xtol=1e-9,
            max_nfev=2000,
        )

        calibrated = dict(zip(params_to_fit, result.x.tolist()))

        # Uncertainty from Jacobian covariance estimate
        uncertainties: Dict[str, float] = {}
        try:
            jac = result.jac
            cov = np.linalg.pinv(jac.T @ jac)
            std = np.sqrt(np.maximum(np.diag(cov), 0.0))
            uncertainties = dict(zip(params_to_fit, std.tolist()))
        except Exception:  # noqa: BLE001
            uncertainties = {n: float("nan") for n in params_to_fit}

        # Update model parameters with calibrated values
        self.update_parameters(calibrated)

        turtle = _params_to_turtle_helper(self.entity_id, calibrated)

        return CalibrationResult(
            calibrated_parameters=calibrated,
            parameter_uncertainties=uncertainties,
            residual_norm=float(np.linalg.norm(result.fun)),
            converged=bool(result.success),
            n_iterations=int(result.nfev),
            semantic_turtle=turtle,
        )

    # ------------------------------------------------------------------
    # Legacy async interface (backward compatibility with test_ro.py)
    # ------------------------------------------------------------------

    async def describe(self) -> Dict[str, Any]:
        """Return JSON-LD description of this model."""
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
        """Legacy fixed-ratio simulation (preserves test_ro.py expectations).

        Args:
            inputs: Input dict (feed_flow_m3d, feed_tds_mg_l, …).

        Returns:
            Output dict with permeate/concentrate flows, TDS, conductivity,
            recovery fraction, and energy.
        """
        q_feed = float(inputs.get("feed_flow_m3d", 0.8))
        tds_feed = float(inputs.get("feed_tds_mg_l", 100.0))
        cond_feed = float(inputs.get("feed_conductivity_us_cm", 200.0))

        q_permeate = q_feed * _RECOVERY
        q_concentrate = q_feed - q_permeate
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


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

_model = ROModel()

app = FastAPI(
    title="Household RO Model",
    description="Reverse Osmosis rainwater treatment service (physics-based)",
    version="2.0.0",
)


# -- Health / describe -------------------------------------------------------


@app.get("/health")
async def health() -> Dict[str, Any]:
    """Health check endpoint."""
    return await _model.health_check()


@app.get("/describe")
async def describe() -> Dict[str, Any]:
    """JSON-LD model description."""
    return await _model.describe()


@app.get("/describe/turtle")
async def describe_turtle() -> PlainTextResponse:
    """Turtle model description."""
    return PlainTextResponse(
        _model.generate_ttl_description(), media_type="text/turtle"
    )


@app.get("/describe/agent")
async def describe_agent() -> PlainTextResponse:
    """Turtle agent description."""
    return PlainTextResponse(_model.generate_agent_ttl(), media_type="text/turtle")


# -- Parameters --------------------------------------------------------------


@app.get("/parameters")
async def get_parameters(request: Request) -> Any:
    """Return current model parameters as JSON or Turtle.

    Content negotiation: send ``Accept: text/turtle`` for Turtle output.
    """
    params = {**_model._default_params, **_model._parameters}
    accept = request.headers.get("accept", "application/json")
    if "text/turtle" in accept:
        return PlainTextResponse(
            _model.params_to_turtle(params), media_type="text/turtle"
        )
    return JSONResponse({"parameters": params, "bounds": _model._PARAM_BOUNDS})


# -- Simulate (legacy + physics) --------------------------------------------


@app.post("/simulate")
async def simulate(body: _LegacyROInput, request: Request) -> Any:
    """Run simulation.

    Legacy JSON output uses fixed-ratio physics.  The physics engine is
    exposed via ``/simulate/physics``.

    Content negotiation: ``Accept: text/turtle`` returns a Turtle
    ``wf:SimulationRun``.
    """
    result = await _model.simulate(body.model_dump())
    accept = request.headers.get("accept", "application/json")
    if "text/turtle" in accept:
        turtle = serialize_outputs_to_turtle(
            result,
            model_id=_model.entity_id,
            var_iris={k: str(v) for k, v in RO_VAR_IRIS.items()},
            simulation_mode="steady_state",
        )
        return PlainTextResponse(turtle, media_type="text/turtle")
    return result


@app.post("/simulate/physics")
async def simulate_physics(body: ROInput, request: Request) -> Any:
    """Physics-based RO simulation endpoint.

    Supports ``simulation_mode`` (steady_state / dynamic), parameter
    overrides, and content negotiation for Turtle output.
    """
    inputs_dict = body.model_dump()

    # Extract optional parameter override
    params_override: Optional[Dict[str, float]] = None
    if body.parameters is not None:
        params_override = body.parameters.model_dump()

    result = _model.simulate_sync(inputs_dict, params_override=params_override)

    mode_str = str(body.simulation_mode.value)
    run_id = uuid4().hex[:8]

    accept = request.headers.get("accept", "application/json")
    if "text/turtle" in accept:
        turtle = serialize_outputs_to_turtle(
            result,
            model_id=_model.entity_id,
            var_iris={k: str(v) for k, v in RO_VAR_IRIS.items()},
            simulation_mode=mode_str,
            scenario_iri=body.scenario_iri,
            run_id=run_id,
        )
        return PlainTextResponse(turtle, media_type="text/turtle")

    # Attach run IRI to response
    result["simulation_run_iri"] = (
        f"https://w3id.org/waterframe/case/household/{_model.entity_id}_Run_{run_id}"
    )
    return result


# -- Calibrate ---------------------------------------------------------------


@app.post("/calibrate", response_model=CalibrationResult)
async def calibrate(body: CalibrationRequest) -> CalibrationResult:
    """Calibrate model parameters to observations.

    Args:
        body: ``CalibrationRequest`` with ``observations`` and
            ``parameters_to_fit``.

    Returns:
        ``CalibrationResult`` with fitted parameters and Turtle serialisation.
    """
    try:
        return _model.calibrate(body)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


# -- State -------------------------------------------------------------------


@app.get("/state")
async def state() -> Dict[str, Any]:
    """Return current model state."""
    return await _model.get_state()


# -- Compose (multi-step treatment unit) --------------------------------------


@app.post("/compose")
async def compose(body: CompositionRequest):
    """Compose multiple sub-unit simulations into a single result.

    Supports three composition strategies:
    - cascade: Sequential HTTP calls to sub-model services (default)
    - assembly: Coupled ODE system (not yet implemented)
    - lumped: Algebraic removal using default efficiencies (fast fallback)

    Args:
        body: CompositionRequest with sub_unit_iris, sub_unit_endpoints,
            inputs, simulation_mode, and composition_strategy.

    Returns:
        JSON with final_outputs, intermediate_outputs (if applicable),
        and metadata about the composition.
    """
    if body.composition_strategy.value == "cascade":
        result = await cascade_simulate(body)
    elif body.composition_strategy.value == "assembly":
        result = assemble_and_solve(body)
    else:
        result = lumped_simulate(body)

    return result
