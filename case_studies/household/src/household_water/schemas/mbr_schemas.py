"""MBR-specific Pydantic schemas."""
from typing import List, Optional
from pydantic import BaseModel, Field
from .common import SimulationMode, DynamicConfig


class MBRParameters(BaseModel):
    mu_max: float = Field(default=6.0, ge=0.1, le=20.0, description="Max specific growth rate (1/d)")
    K_s: float = Field(default=20.0, ge=1.0, le=200.0, description="Half-saturation constant (mg COD/L)")
    Y: float = Field(default=0.67, ge=0.3, le=0.8, description="Yield coefficient (g VSS/g COD)")
    b: float = Field(default=0.15, ge=0.01, le=1.0, description="Decay rate (1/d)")
    K_La: float = Field(default=240.0, ge=1.0, le=1000.0, description="Oxygen transfer rate (1/d)")


class MBRInput(BaseModel):
    influent_flow_m3d: float = Field(default=1.5, ge=0, description="Influent flow rate (m³/d)")
    influent_cod_mg_l: float = Field(default=350.0, ge=0, description="Influent COD (mg/L)")
    influent_bod_mg_l: float = Field(default=200.0, ge=0, description="Influent BOD (mg/L)")
    influent_tss_mg_l: float = Field(default=150.0, ge=0, description="Influent TSS (mg/L)")
    influent_nh4_mg_l: float = Field(default=50.0, ge=0, description="Influent NH4-N (mg/L)")
    influent_tp_mg_l: float = Field(default=8.0, ge=0, description="Influent total phosphorus (mg/L)")
    simulation_mode: SimulationMode = SimulationMode.steady_state
    dynamic_config: Optional[DynamicConfig] = None
    parameters: Optional[MBRParameters] = None
    scenario_iri: Optional[str] = None


class MBRSteadyOutput(BaseModel):
    effluent_flow_m3d: float
    effluent_cod_mg_l: float
    effluent_tss_mg_l: float
    effluent_nh4_mg_l: float
    effluent_tp_mg_l: float
    energy_kwh_d: float
    sludge_kg_d: float
    recovery_fraction: float
    biomass_x_mg_l: float
    dissolved_o2_mg_l: float
    simulation_run_iri: Optional[str] = None


class MBRDynamicOutput(BaseModel):
    time_days: List[float]
    substrate_s_mg_l: List[float]
    biomass_x_mg_l: List[float]
    dissolved_o2_mg_l: List[float]
    simulation_run_iri: Optional[str] = None
