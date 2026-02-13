"""RO-specific Pydantic schemas."""
from typing import List, Optional
from pydantic import BaseModel, Field
from .common import SimulationMode, DynamicConfig


class ROParameters(BaseModel):
    A: float = Field(default=3.5e-7, ge=1e-9, le=1e-5, description="Water permeability (m/s/Pa)")
    B: float = Field(default=8e-8, ge=1e-10, le=1e-4, description="Salt permeability (m/s)")
    k_m: float = Field(default=1e-5, ge=1e-7, le=1e-3, description="Mass transfer coefficient (m/s)")


class ROInput(BaseModel):
    feed_flow_m3d: float = Field(default=0.8, ge=0, description="Feed flow rate (m³/d)")
    feed_tds_mg_l: float = Field(default=100.0, ge=0, description="Feed TDS (mg/L)")
    feed_turbidity_ntu: float = Field(default=1.0, ge=0, description="Feed turbidity (NTU)")
    feed_conductivity_us_cm: float = Field(default=200.0, ge=0, description="Feed conductivity (µS/cm)")
    applied_pressure_bar: float = Field(default=8.0, ge=0, description="Applied transmembrane pressure (bar)")
    membrane_area_m2: float = Field(default=2.0, ge=0, description="Membrane area (m²)")
    simulation_mode: SimulationMode = SimulationMode.steady_state
    dynamic_config: Optional[DynamicConfig] = None
    parameters: Optional[ROParameters] = None
    scenario_iri: Optional[str] = None


class ROSteadyOutput(BaseModel):
    permeate_flow_m3d: float
    concentrate_flow_m3d: float
    permeate_tds_mg_l: float
    permeate_conductivity_us_cm: float
    recovery_fraction: float
    energy_kwh_d: float
    water_flux_m_s: float
    osmotic_pressure_pa: float
    simulation_run_iri: Optional[str] = None


class RODynamicOutput(BaseModel):
    time_days: List[float]
    permeate_tds_mg_l: List[float]
    water_flux_m_s: List[float]
    simulation_run_iri: Optional[str] = None
