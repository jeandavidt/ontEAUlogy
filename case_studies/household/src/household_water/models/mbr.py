"""Membrane Bioreactor (MBR) model service — port 8101.

Treats household greywater (bath, sink, washer, dishwasher, kitchen, cleaning).
Provides both a legacy analytical path (backward-compatible) and a physics-based
Monod-CSTR ODE path selectable via ``simulation_mode`` / ``use_physics``.

Physics implementation delegates to:
- ``household_water.physics.mbr_odes.mbr_simulate_steady`` (analytical steady-state)
- ``household_water.physics.mbr_odes.mbr_simulate_dynamic`` (ODE solver)

Calibration uses ``scipy.optimize.least_squares`` against the physics model.
Content negotiation: ``Accept: text/turtle`` returns RDF Turtle output.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Union

import numpy as np
from fastapi import FastAPI, Header
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from scipy.optimize import least_squares

from .base import BaseHouseholdModel
from ..physics.mbr_odes import (
    MBR_DEFAULT_PARAMS,
    mbr_simulate_steady,
    mbr_simulate_dynamic,
)
from ..schemas.common import (
    CalibrationObservation,
    CalibrationRequest,
    CalibrationResult,
    CompositionRequest,
    DynamicConfig,
    SimulationMode,
)
from ..schemas.mbr_schemas import (
    MBRDynamicOutput,
    MBRInput,
    MBRSteadyOutput,
)
from ..semantic.io_serializer import serialize_outputs_to_turtle
from ..semantic.namespaces import MBR_VAR_IRIS
from ..composition.cascade import cascade_simulate
from ..composition.lumped import lumped_simulate
from ..composition.assembly import assemble_and_solve

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Legacy schemas kept for backward compatibility with test_mbr.py
# ---------------------------------------------------------------------------


class _LegacyMBRInput(BaseModel):
    """Original schema without physics fields — used by the legacy /simulate endpoint."""

    influent_flow_m3d: float = Field(
        default=1.5, ge=0, description="Influent flow rate (m³/d)"
    )
    influent_cod_mg_l: float = Field(
        default=350.0, ge=0, description="Influent COD (mg/L)"
    )
    influent_bod_mg_l: float = Field(
        default=200.0, ge=0, description="Influent BOD (mg/L)"
    )
    influent_tss_mg_l: float = Field(
        default=150.0, ge=0, description="Influent TSS (mg/L)"
    )
    influent_nh4_mg_l: float = Field(
        default=50.0, ge=0, description="Influent NH4-N (mg/L)"
    )
    influent_tp_mg_l: float = Field(
        default=8.0, ge=0, description="Influent total phosphorus (mg/L)"
    )


class _LegacyMBROutput(BaseModel):
    """Original output schema — returned by the legacy /simulate endpoint."""

    effluent_flow_m3d: float
    effluent_cod_mg_l: float
    effluent_tss_mg_l: float
    effluent_nh4_mg_l: float
    effluent_tp_mg_l: float
    energy_kwh_d: float
    sludge_kg_d: float
    recovery_fraction: float


# Legacy analytical removal constants
_COD_REMOVAL = 0.95
_BOD_REMOVAL = 0.97
_TSS_REMOVAL = 0.99
_NH4_REMOVAL = 0.85
_TP_REMOVAL = 0.60
_ENERGY_KWH_PER_M3 = 0.4
_SLUDGE_YIELD = 0.6


# ---------------------------------------------------------------------------
# Physics-route input schema (superset of legacy schema)
# ---------------------------------------------------------------------------


class PhysicsMBRInput(BaseModel):
    """Extended input schema with physics routing, mode selection, and calibration."""

    influent_flow_m3d: float = Field(
        default=1.5, ge=0, description="Influent flow rate (m³/d)"
    )
    influent_cod_mg_l: float = Field(
        default=350.0, ge=0, description="Influent COD (mg/L)"
    )
    influent_bod_mg_l: float = Field(
        default=200.0, ge=0, description="Influent BOD (mg/L)"
    )
    influent_tss_mg_l: float = Field(
        default=150.0, ge=0, description="Influent TSS (mg/L)"
    )
    influent_nh4_mg_l: float = Field(
        default=50.0, ge=0, description="Influent NH4-N (mg/L)"
    )
    influent_tp_mg_l: float = Field(
        default=8.0, ge=0, description="Influent total phosphorus (mg/L)"
    )
    simulation_mode: SimulationMode = SimulationMode.steady_state
    dynamic_config: Optional[DynamicConfig] = None
    parameters: Optional[Dict[str, float]] = None
    scenario_iri: Optional[str] = None


# ---------------------------------------------------------------------------
# MBRModel — physics-capable subclass of BaseHouseholdModel
# ---------------------------------------------------------------------------


class MBRModel(BaseHouseholdModel):
    """Membrane Bioreactor greywater treatment model.

    Implements both the legacy analytical path (for backward compatibility)
    and a physics-based Monod-CSTR ODE path via ``simulate_sync``.
    """

    _PARAM_BOUNDS: Dict[str, tuple] = {
        "mu_max": (0.1, 20.0),
        "K_s": (1.0, 200.0),
        "Y": (0.3, 0.8),
        "b": (0.01, 1.0),
        "K_La": (0.1, 100.0),
    }
    _default_params: Dict[str, float] = {
        "mu_max": 6.0,
        "K_s": 20.0,
        "Y": 0.67,
        "b": 0.15,
        "K_La": 24.0,
    }

    def __init__(self) -> None:
        super().__init__(
            entity_id="Membrane_bioreactor",
            entity_name="Membrane Bioreactor",
            entity_type="SimulationModel",
            port=8101,
            capabilities=[
                "SteadyStateSimulation",
                "DynamicSimulation",
                "Calibration",
                "MassBalance",
                "WaterQualityPrediction",
            ],
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
                {"name": "biomass_x_mg_l", "unit": "mg/L"},
                {"name": "dissolved_o2_mg_l", "unit": "mg/L"},
            ],
        )

    # ------------------------------------------------------------------
    # Legacy analytical simulate (kept for backward compatibility)
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
                    "rdfs:comment": "MBR model for household greywater treatment",
                    "wf:representsEntity": {"@id": self.entity_iri},
                    "wf:apiEndpoint": self.api_endpoint,
                    "wf:port": self.port,
                }
            ],
        }

    async def simulate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy analytical simulation (backward-compatible, first-order removal).

        Args:
            inputs: Dictionary of influent concentrations and flows.

        Returns:
            Output dictionary with effluent quality and energy metrics.
        """
        q = float(inputs.get("influent_flow_m3d", 1.5))
        cod_in = float(inputs.get("influent_cod_mg_l", 350.0))
        tss_in = float(inputs.get("influent_tss_mg_l", 150.0))
        nh4_in = float(inputs.get("influent_nh4_mg_l", 50.0))
        tp_in = float(inputs.get("influent_tp_mg_l", 8.0))

        cod_eff = cod_in * (1 - _COD_REMOVAL)
        tss_eff = tss_in * (1 - _TSS_REMOVAL)
        nh4_eff = nh4_in * (1 - _NH4_REMOVAL)
        tp_eff = tp_in * (1 - _TP_REMOVAL)

        energy = q * _ENERGY_KWH_PER_M3
        tss_removed_kg_d = (tss_in - tss_eff) * q * 1e-3
        sludge = tss_removed_kg_d * _SLUDGE_YIELD

        recovery = 0.95
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

    # ------------------------------------------------------------------
    # Physics-based simulate_sync (Monod-CSTR ODE)
    # ------------------------------------------------------------------

    def simulate_sync(
        self,
        inputs: Dict[str, Any],
        params_override: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Physics-based synchronous simulation using the Monod-CSTR ODE system.

        Merges ``self._parameters`` with ``params_override`` and dispatches
        to the appropriate physics function based on ``simulation_mode``.

        Args:
            inputs: Influent conditions and simulation configuration.
                Recognised keys include all ``PhysicsMBRInput`` fields, plus
                ``t_start``, ``t_end``, ``n_points`` for dynamic runs.
            params_override: Optional parameter overrides (applied only for
                this call; instance parameters are not mutated).

        Returns:
            For ``steady_state``: dict matching ``MBRSteadyOutput`` fields.
            For ``dynamic``: dict matching ``MBRDynamicOutput`` fields.
        """
        # Build effective parameter set: physics defaults → instance params → override
        effective_params = dict(MBR_DEFAULT_PARAMS)
        effective_params.update(self._parameters)
        if params_override:
            effective_params.update(params_override)

        # Extract simulation mode
        mode = inputs.get("simulation_mode", SimulationMode.steady_state)
        if isinstance(mode, str):
            mode = SimulationMode(mode)

        # Propagate dynamic config fields into inputs dict if present
        dynamic_cfg = inputs.get("dynamic_config")
        if dynamic_cfg is not None:
            if isinstance(dynamic_cfg, DynamicConfig):
                inputs = dict(inputs)
                inputs["t_start"] = dynamic_cfg.t_start
                inputs["t_end"] = dynamic_cfg.t_end
                inputs["n_points"] = dynamic_cfg.n_points
            elif isinstance(dynamic_cfg, dict):
                inputs = dict(inputs)
                inputs.setdefault("t_start", dynamic_cfg.get("t_start", 0.0))
                inputs.setdefault("t_end", dynamic_cfg.get("t_end", 10.0))
                inputs.setdefault("n_points", dynamic_cfg.get("n_points", 100))

        if mode == SimulationMode.dynamic:
            result = mbr_simulate_dynamic(inputs, effective_params)
        else:
            result = mbr_simulate_steady(inputs, effective_params)

        return result

    # ------------------------------------------------------------------
    # Current parameters as a dict
    # ------------------------------------------------------------------

    def get_current_params(self) -> Dict[str, float]:
        """Return the current effective physics parameters.

        Returns:
            Merged dict of class defaults overridden by instance parameters.
        """
        merged = dict(MBR_DEFAULT_PARAMS)
        merged.update(self._parameters)
        return merged


# ---------------------------------------------------------------------------
# Calibration helper (module-level, injectable for testability)
# ---------------------------------------------------------------------------


def _calibration_residuals(
    x: np.ndarray,
    param_names: List[str],
    observations: List[CalibrationObservation],
    simulate_fn: Any,
) -> List[float]:
    """Compute residuals between predicted and observed outputs.

    Args:
        x: Current parameter vector aligned with ``param_names``.
        param_names: Names of parameters being optimised.
        observations: List of (inputs, observed_outputs) pairs.
        simulate_fn: Callable accepting ``(inputs_dict, params_override)``
            and returning an output dict.

    Returns:
        Flat list of signed residuals ``(predicted - observed)``.
    """
    params = dict(zip(param_names, x.tolist()))
    residuals: List[float] = []
    for obs in observations:
        pred = simulate_fn(obs.inputs, params)
        for k, v_obs in obs.observed_outputs.items():
            residuals.append(pred.get(k, 0.0) - v_obs)
    return residuals


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

_model = MBRModel()

app = FastAPI(
    title="Household MBR Model",
    description="Membrane Bioreactor greywater treatment service with physics-based ODE engine",
    version="2.0.0",
)


@app.get("/health")
async def health():
    """Health-check endpoint."""
    return await _model.health_check()


@app.get("/describe")
async def describe():
    """Return JSON-LD model description."""
    return await _model.describe()


@app.get("/describe/turtle")
async def describe_turtle():
    """Return Turtle RDF model description."""
    return PlainTextResponse(
        _model.generate_ttl_description(), media_type="text/turtle"
    )


@app.get("/describe/agent")
async def describe_agent():
    """Return Turtle RDF agent description."""
    return PlainTextResponse(_model.generate_agent_ttl(), media_type="text/turtle")


@app.get("/state")
async def state():
    """Return current model state."""
    return await _model.get_state()


# ------------------------------------------------------------------
# Legacy /simulate endpoint — backward-compatible analytical model
# ------------------------------------------------------------------


@app.post("/simulate", response_model=_LegacyMBROutput)
async def simulate(body: _LegacyMBRInput):
    """Analytical (first-order removal) simulation.  Preserved for backward compatibility."""
    return await _model.simulate(body.model_dump())


# ------------------------------------------------------------------
# Physics /simulate/physics endpoint — Monod-CSTR ODE
# ------------------------------------------------------------------


@app.post("/simulate/physics")
async def simulate_physics(
    body: PhysicsMBRInput,
    accept: Optional[str] = Header(default=None),
):
    """Physics-based MBR simulation using the Monod-CSTR ODE system.

    Supports content negotiation:
    - ``Accept: application/json`` (default) — returns JSON.
    - ``Accept: text/turtle`` — returns RDF Turtle with ``wf:SimulationRun``.

    Request body fields:
    - ``simulation_mode``: ``"steady_state"`` (default) or ``"dynamic"``.
    - ``parameters``: optional dict of parameter overrides.
    - ``dynamic_config``: optional ``{t_start, t_end, n_points}`` for dynamic runs.
    - ``scenario_iri``: optional IRI to tag the simulation run.
    """
    inputs_dict = body.model_dump()
    result = _model.simulate_sync(inputs_dict, body.parameters)
    _model._update_state(result)

    want_turtle = accept and "text/turtle" in accept
    if want_turtle:
        mode_str = body.simulation_mode.value
        turtle_str = serialize_outputs_to_turtle(
            outputs=result,
            model_id=_model.entity_id,
            var_iris={k: str(v) for k, v in MBR_VAR_IRIS.items()},
            simulation_mode=mode_str,
            scenario_iri=body.scenario_iri,
        )
        return PlainTextResponse(turtle_str, media_type="text/turtle")

    return result


# ------------------------------------------------------------------
# GET /parameters — return current physics parameters
# ------------------------------------------------------------------


@app.get("/parameters")
async def get_parameters(accept: Optional[str] = Header(default=None)):
    """Return current physics parameters.

    Supports content negotiation:
    - ``Accept: application/json`` (default) — returns JSON dict.
    - ``Accept: text/turtle`` — returns RDF Turtle parameter descriptions.
    """
    params = _model.get_current_params()

    want_turtle = accept and "text/turtle" in accept
    if want_turtle:
        turtle_str = _model.params_to_turtle(params)
        return PlainTextResponse(turtle_str, media_type="text/turtle")

    return params


# ------------------------------------------------------------------
# POST /calibrate — least-squares parameter calibration
# ------------------------------------------------------------------


@app.post("/calibrate", response_model=CalibrationResult)
async def calibrate(body: CalibrationRequest):
    """Calibrate physics parameters using ``scipy.optimize.least_squares``.

    Fits the parameters listed in ``parameters_to_fit`` against the provided
    ``observations`` (each with ``inputs`` and ``observed_outputs``).
    Updates the model's internal parameter store with calibrated values.
    Returns parameter uncertainties derived from the Jacobian covariance.

    Args:
        body: ``CalibrationRequest`` with observations and parameter names.

    Returns:
        ``CalibrationResult`` with calibrated values, uncertainties, and
        a Turtle serialisation of the calibrated parameters.
    """
    param_names = body.parameters_to_fit
    if not param_names:
        return CalibrationResult(
            calibrated_parameters={},
            parameter_uncertainties={},
            residual_norm=0.0,
            converged=True,
            n_iterations=0,
            semantic_turtle=None,
        )

    # Initial guess from current instance parameters (merged with physics defaults)
    current = _model.get_current_params()
    x0 = np.array([current.get(n, MBR_DEFAULT_PARAMS.get(n, 1.0)) for n in param_names])

    # Bounds from _PARAM_BOUNDS (fall back to unconstrained if missing)
    lows = [
        _model._PARAM_BOUNDS[n][0] if n in _model._PARAM_BOUNDS else -np.inf
        for n in param_names
    ]
    highs = [
        _model._PARAM_BOUNDS[n][1] if n in _model._PARAM_BOUNDS else np.inf
        for n in param_names
    ]

    opt = least_squares(
        _calibration_residuals,
        x0,
        bounds=(lows, highs),
        args=(param_names, body.observations, _model.simulate_sync),
        method="trf",
    )

    calibrated = dict(zip(param_names, opt.x.tolist()))

    # Parameter uncertainties from Jacobian covariance
    n_obs = sum(len(obs.observed_outputs) for obs in body.observations)
    n_par = len(param_names)
    uncertainties: Dict[str, float] = {}
    try:
        J = opt.jac  # shape (n_residuals, n_params)
        JtJ = J.T @ J
        cost = float(opt.cost)
        dof = max(1, n_obs - n_par)
        cov = np.linalg.inv(JtJ) * (2.0 * cost / dof)
        diag = np.maximum(np.diag(cov), 0.0)
        uncertainties = dict(zip(param_names, np.sqrt(diag).tolist()))
    except np.linalg.LinAlgError:
        uncertainties = {n: float("nan") for n in param_names}

    # Persist calibrated parameters in model
    _model.update_parameters(calibrated)

    turtle_str = _model.params_to_turtle(calibrated)

    return CalibrationResult(
        calibrated_parameters=calibrated,
        parameter_uncertainties=uncertainties,
        residual_norm=float(np.sqrt(2.0 * opt.cost)),
        converged=bool(opt.success),
        n_iterations=int(opt.njev),
        semantic_turtle=turtle_str,
    )


# ------------------------------------------------------------------
# POST /compose — multi-step treatment unit composition
# ------------------------------------------------------------------


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
