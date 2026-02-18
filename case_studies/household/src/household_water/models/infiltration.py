"""Infiltration model service — port 8103.

Receives blackwater from blackwater storage + purified greywater overflow.
Physics: plug-flow first-order removal (steady-state) and simplified
Richards + advective transport ODE (dynamic), via infiltration_equations.py.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel, Field
from scipy.optimize import least_squares

from .base import BaseHouseholdModel
from ..physics.infiltration_equations import (
    infiltration_simulate_steady,
    infiltration_simulate_dynamic,
    INFIL_DEFAULT_PARAMS,
)
from ..schemas.infiltration_schemas import (
    InfiltrationInput,
    InfiltrationSteadyOutput,
    InfiltrationDynamicOutput,
    InfiltrationParameters,
)
from ..schemas.common import (
    SimulationMode,
    CalibrationRequest,
    CalibrationResult,
    CompositionRequest,
)
from ..semantic.io_serializer import (
    serialize_outputs_to_turtle,
    params_to_turtle as _params_to_turtle_io,
)
from ..semantic.namespaces import INFILTRATION_VAR_IRIS
from ..composition.cascade import cascade_simulate
from ..composition.lumped import lumped_simulate
from ..composition.assembly import assemble_and_solve

logger = logging.getLogger(__name__)

# ── Model class ──────────────────────────────────────────────────────────────


class InfiltrationModel(BaseHouseholdModel):
    """Subsurface infiltration treatment model (physics-based).

    Steady-state uses plug-flow first-order removal.
    Dynamic uses a simplified Richards equation coupled with
    advective solute transport (via infiltration_equations.py).
    """

    _PARAM_BOUNDS: Dict[str, Tuple[float, float]] = {
        "k_COD": (0.01, 10.0),
        "k_TSS": (0.01, 20.0),
        "k_NH4": (0.01, 5.0),
        "K_sat": (0.01, 5.0),
        "theta_eff": (0.1, 0.5),
    }
    _default_params: Dict[str, float] = {
        "k_COD": 0.5,
        "k_TSS": 1.0,
        "k_NH4": 0.3,
        "K_sat": 0.5,
        "theta_eff": 0.3,
    }

    def __init__(self) -> None:
        super().__init__(
            entity_id="Infiltration",
            entity_name="Infiltration Unit",
            entity_type="SimulationModel",
            port=8103,
            capabilities=[
                "SteadyStateSimulation",
                "DynamicSimulation",
                "Calibration",
                "MassBalance",
            ],
            inputs=[
                {"name": "influent_flow_m3d", "unit": "m³/d"},
                {"name": "influent_cod_mg_l", "unit": "mg/L"},
                {"name": "influent_tss_mg_l", "unit": "mg/L"},
                {"name": "influent_nh4_mg_l", "unit": "mg/L"},
                {"name": "area_m2", "unit": "m²"},
                {"name": "soil_depth_m", "unit": "m"},
            ],
            outputs=[
                {"name": "infiltrated_flow_m3d", "unit": "m³/d"},
                {"name": "removed_cod_fraction", "unit": "-"},
                {"name": "removed_tss_fraction", "unit": "-"},
                {"name": "removed_nh4_fraction", "unit": "-"},
                {"name": "effluent_cod_mg_l", "unit": "mg/L"},
                {"name": "effluent_tss_mg_l", "unit": "mg/L"},
                {"name": "effluent_nh4_mg_l", "unit": "mg/L"},
                {"name": "hrt_days", "unit": "d"},
            ],
        )

    # ------------------------------------------------------------------
    # Abstract interface implementation
    # ------------------------------------------------------------------

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
                    "rdfs:comment": (
                        "Infiltration/soil treatment model for household "
                        "blackwater disposal (physics-based)"
                    ),
                    "wf:representsEntity": {"@id": self.entity_iri},
                    "wf:apiEndpoint": self.api_endpoint,
                    "wf:port": self.port,
                }
            ],
        }

    async def simulate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Route to steady-state or dynamic physics simulation."""
        mode = inputs.get("simulation_mode", SimulationMode.steady_state)
        if isinstance(mode, str):
            mode = SimulationMode(mode)

        # Merge any parameter overrides carried inside the inputs dict.
        params_override: Optional[Dict[str, float]] = inputs.get("parameters")
        params = dict(self._parameters)
        # Merge physics defaults (theta_sat, theta_res, n_vg) so the ODE works.
        full_params = {**INFIL_DEFAULT_PARAMS, **params}
        if params_override:
            if isinstance(params_override, dict):
                full_params.update(params_override)

        if mode == SimulationMode.dynamic:
            dyn = inputs.get("dynamic_config") or {}
            if hasattr(dyn, "model_dump"):
                dyn = dyn.model_dump()
            dyn_inputs = {**inputs, **dyn}
            result = infiltration_simulate_dynamic(dyn_inputs, full_params)
        else:
            result = infiltration_simulate_steady(inputs, full_params)

        self._update_state(result)
        return result

    def simulate_sync(
        self,
        inputs: Dict[str, Any],
        params_override: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Synchronous wrapper used by calibration."""
        import asyncio

        merged = dict(inputs)
        if params_override:
            merged["parameters"] = params_override
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                    fut = ex.submit(asyncio.run, self.simulate(merged))
                    return fut.result()
            return loop.run_until_complete(self.simulate(merged))
        except RuntimeError:
            return asyncio.run(self.simulate(merged))

    # ------------------------------------------------------------------
    # Calibration
    # ------------------------------------------------------------------

    def calibrate(self, request: CalibrationRequest) -> CalibrationResult:
        """Least-squares calibration against observed outputs.

        Args:
            request: Calibration request with observations and parameter names.

        Returns:
            CalibrationResult with calibrated parameter values.
        """
        names: List[str] = request.parameters_to_fit
        lows, highs = self.get_param_bounds(names)

        # Initial guess from current parameters.
        x0 = [self._parameters.get(n, self._default_params.get(n, 1.0)) for n in names]

        def residuals(x: np.ndarray) -> List[float]:
            override = dict(zip(names, x.tolist()))
            res: List[float] = []
            for obs in request.observations:
                out = self._simulate_steady_for_calibration(obs.inputs, override)
                for key, obs_val in obs.observed_outputs.items():
                    pred = out.get(key, 0.0)
                    res.append(float(pred) - float(obs_val))
            return res

        sol = least_squares(
            residuals,
            x0,
            bounds=(lows, highs),
            method="trf",
            ftol=1e-9,
            xtol=1e-9,
            gtol=1e-9,
            max_nfev=2000,
        )

        calibrated: Dict[str, float] = dict(zip(names, sol.x.tolist()))
        # Rough uncertainty estimate: diagonal of (J^T J)^-1 * residual variance.
        try:
            J = sol.jac
            cov = np.linalg.pinv(J.T @ J)
            rvar = (sol.fun @ sol.fun) / max(len(sol.fun) - len(names), 1)
            uncertainties = {
                n: float(np.sqrt(max(0.0, cov[i, i] * rvar)))
                for i, n in enumerate(names)
            }
        except Exception:
            uncertainties = {n: 0.0 for n in names}

        turtle_str = _params_to_turtle_io("Infiltration", calibrated)

        return CalibrationResult(
            calibrated_parameters=calibrated,
            parameter_uncertainties=uncertainties,
            residual_norm=float(np.linalg.norm(sol.fun)),
            converged=bool(sol.success),
            n_iterations=int(sol.nfev),
            semantic_turtle=turtle_str,
        )

    def _simulate_steady_for_calibration(
        self,
        inputs: Dict[str, float],
        override: Dict[str, float],
    ) -> Dict[str, Any]:
        """Run a pure steady-state simulation (no async) for calibration."""
        full_params = {**INFIL_DEFAULT_PARAMS, **self._parameters, **override}
        return infiltration_simulate_steady(inputs, full_params)


# ── FastAPI app ───────────────────────────────────────────────────────────────

_model = InfiltrationModel()
app = FastAPI(
    title="Household Infiltration Model",
    description="Physics-based subsurface infiltration treatment service",
    version="2.0.0",
)


def _wants_turtle(request: Request) -> bool:
    accept = request.headers.get("accept", "")
    return "text/turtle" in accept


@app.get("/health")
async def health() -> Dict[str, Any]:
    return await _model.health_check()


@app.get("/describe")
async def describe() -> Dict[str, Any]:
    return await _model.describe()


@app.get("/describe/turtle")
async def describe_turtle() -> PlainTextResponse:
    return PlainTextResponse(
        _model.generate_ttl_description(), media_type="text/turtle"
    )


@app.get("/describe/agent")
async def describe_agent() -> PlainTextResponse:
    return PlainTextResponse(_model.generate_agent_ttl(), media_type="text/turtle")


@app.get("/parameters")
async def get_parameters(request: Request):
    """Return current model parameters.

    Supports content negotiation: returns Turtle when ``Accept: text/turtle``
    is sent, otherwise returns JSON.
    """
    params = dict(_model._parameters)
    if _wants_turtle(request):
        ttl = _model.params_to_turtle(params)
        return PlainTextResponse(ttl, media_type="text/turtle")
    return JSONResponse({"parameters": params, "bounds": _model._PARAM_BOUNDS})


@app.post("/calibrate", response_model=CalibrationResult)
async def calibrate(body: CalibrationRequest) -> CalibrationResult:
    """Calibrate model parameters against observed data."""
    return _model.calibrate(body)


@app.post("/simulate")
async def simulate(body: InfiltrationInput, request: Request):
    """Run a simulation.

    Accepts ``simulation_mode`` (steady_state or dynamic), optional
    ``parameters`` override, ``scenario_iri``, ``area_m2``, and
    ``soil_depth_m``.  Supports content negotiation: returns Turtle when
    ``Accept: text/turtle`` is set.
    """
    payload = body.model_dump()
    result = await _model.simulate(payload)

    scenario_iri = body.scenario_iri
    mode_str = (
        body.simulation_mode.value
        if hasattr(body.simulation_mode, "value")
        else str(body.simulation_mode)
    )

    if _wants_turtle(request):
        ttl = serialize_outputs_to_turtle(
            outputs=result,
            model_id="Infiltration",
            var_iris={str(k): str(v) for k, v in INFILTRATION_VAR_IRIS.items()},
            simulation_mode=mode_str,
            scenario_iri=scenario_iri,
        )
        return PlainTextResponse(ttl, media_type="text/turtle")

    # Attach simulation_run_iri for JSON responses if mode is steady-state.
    if body.simulation_mode == SimulationMode.steady_state:
        return InfiltrationSteadyOutput(**result)
    return result


@app.get("/state")
async def state() -> Dict[str, Any]:
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
