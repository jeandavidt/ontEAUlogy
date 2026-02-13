"""Infiltration-specific Pydantic schemas."""
from typing import List, Optional
from pydantic import BaseModel, Field
from .common import SimulationMode, DynamicConfig


class InfiltrationParameters(BaseModel):
    k_COD: float = Field(default=1.5, ge=0.01, le=10.0, description="First-order COD removal rate (1/d)")
    k_TSS: float = Field(default=3.0, ge=0.01, le=20.0, description="First-order TSS removal rate (1/d)")
    k_NH4: float = Field(default=0.8, ge=0.01, le=5.0, description="First-order NH4 removal rate (1/d)")
    K_sat: float = Field(default=0.5, ge=0.001, le=10.0, description="Saturated hydraulic conductivity (m/d)")
    theta_eff: float = Field(default=0.3, ge=0.1, le=0.6, description="Effective porosity (-)")
    n_vg: float = Field(default=2.0, ge=1.1, le=5.0, description="van Genuchten n parameter (-)")


class InfiltrationInput(BaseModel):
    influent_flow_m3d: float = Field(default=0.3, ge=0, description="Influent flow rate (m³/d)")
    influent_cod_mg_l: float = Field(default=200.0, ge=0, description="Influent COD (mg/L)")
    influent_tss_mg_l: float = Field(default=50.0, ge=0, description="Influent TSS (mg/L)")
    influent_nh4_mg_l: float = Field(default=40.0, ge=0, description="Influent NH4-N (mg/L)")
    area_m2: float = Field(default=10.0, ge=0, description="Infiltration area (m²)")
    soil_depth_m: float = Field(default=1.0, ge=0, description="Soil depth (m)")
    simulation_mode: SimulationMode = SimulationMode.steady_state
    dynamic_config: Optional[DynamicConfig] = None
    parameters: Optional[InfiltrationParameters] = None
    scenario_iri: Optional[str] = None


class InfiltrationSteadyOutput(BaseModel):
    infiltrated_flow_m3d: float
    removed_cod_fraction: float
    removed_tss_fraction: float
    removed_nh4_fraction: float
    effluent_cod_mg_l: float
    effluent_tss_mg_l: float
    effluent_nh4_mg_l: float
    hrt_days: float
    simulation_run_iri: Optional[str] = None


class InfiltrationDynamicOutput(BaseModel):
    time_days: List[float]
    soil_moisture: List[float]
    effluent_cod_mg_l: List[float]
    effluent_tss_mg_l: List[float]
    effluent_nh4_mg_l: List[float]
    simulation_run_iri: Optional[str] = None
