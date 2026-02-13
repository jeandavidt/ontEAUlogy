"""Shared schemas for simulation modes, calibration, and composition."""
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel


class SimulationMode(str, Enum):
    steady_state = "steady_state"
    dynamic = "dynamic"


class CompositionStrategy(str, Enum):
    cascade  = "cascade"
    assembly = "assembly"
    lumped   = "lumped"


class DynamicConfig(BaseModel):
    t_start: float = 0.0
    t_end: float = 10.0
    n_points: int = 100


class CalibrationObservation(BaseModel):
    inputs: Dict[str, float]
    observed_outputs: Dict[str, float]


class CalibrationRequest(BaseModel):
    observations: List[CalibrationObservation]
    parameters_to_fit: List[str]
    method: str = "least_squares"


class CalibrationResult(BaseModel):
    calibrated_parameters: Dict[str, float]
    parameter_uncertainties: Dict[str, float]
    residual_norm: float
    converged: bool
    n_iterations: int
    semantic_turtle: Optional[str] = None


class CompositionRequest(BaseModel):
    unit_iri: str
    sub_unit_iris: List[str]
    sub_unit_endpoints: List[str]
    inputs: Dict[str, float]
    simulation_mode: SimulationMode = SimulationMode.steady_state
    dynamic_config: Optional[DynamicConfig] = None
    composition_strategy: CompositionStrategy = CompositionStrategy.cascade
    scenario_iri: Optional[str] = None
