"""Model configuration for all 12 water system entities in Ghent case study.

Contains configuration for:
- Drinking Water Plants (DWP-1, DWP-2)
- Wastewater Treatment Plants (WWTP-1, WWTP-2)
- Industries (Texfin, FoodPro, ChipTech, PharmaGen, BrewCo)
- Residential Districts (Dampoort, Muide)
- River (Lieve River)
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum


class EntityType(str, Enum):
    """Types of water system entities."""
    DRINKING_WATER_PLANT = "DrinkingWaterPlant"
    WASTEWATER_TREATMENT_PLANT = "WastewaterTreatmentPlant"
    INDUSTRY = "Industry"
    RESIDENTIAL = "ResidentialDistrict"
    RIVER = "RiverSegment"


@dataclass
class ParameterConfig:
    """Configuration for a model parameter."""
    name: str
    unit: str
    datatype: str = "float"
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    default: Optional[Any] = None
    is_decision_variable: bool = False
    description: Optional[str] = None


@dataclass
class TreatmentConfig:
    """Configuration for treatment/removal process."""
    parameter: str
    removal_rate: float  # Percentage (0-100)
    efficiency_variance: float = 5.0  # Variance in efficiency


@dataclass
class EntityConfig:
    """Complete configuration for a water system entity."""
    entity_id: str
    entity_name: str
    entity_type: EntityType
    port: int
    parameters: List[ParameterConfig]
    inputs: List[ParameterConfig]
    outputs: List[ParameterConfig]
    capabilities: List[str]
    treatment_config: Optional[List[TreatmentConfig]] = None
    metadata: Optional[Dict[str, Any]] = None


# Drinking Water Plant Configurations
DWP_CONFIGS: List[EntityConfig] = [
    EntityConfig(
        entity_id="DWP1",
        entity_name="Drinking Water Plant 1",
        entity_type=EntityType.DRINKING_WATER_PLANT,
        port=8001,
        parameters=[
            ParameterConfig("design_capacity", "m³/d", default=50000),
            ParameterConfig("treatment_efficiency", "%", default=95.0),
        ],
        inputs=[
            ParameterConfig("raw_water_flow", "m³/d", min_value=0, max_value=60000, default=40000),
            ParameterConfig("raw_water_turbidity", "NTU", min_value=0, max_value=100, default=10),
            ParameterConfig("raw_water_toc", "mg/L", min_value=0, max_value=50, default=5),
            ParameterConfig("raw_water_ph", "-", min_value=6, max_value=9, default=7.5),
            ParameterConfig("raw_water_coliforms", "CFU/100mL", min_value=0, max_value=10000, default=100),
        ],
        outputs=[
            ParameterConfig("treated_water_flow", "m³/d", min_value=0, max_value=60000, default=40000),
            ParameterConfig("treated_water_turbidity", "NTU", min_value=0, max_value=5, default=0.5),
            ParameterConfig("treated_water_toc", "mg/L", min_value=0, max_value=10, default=1),
            ParameterConfig("treated_water_ph", "-", min_value=6.5, max_value=8.5, default=7.2),
            ParameterConfig("treated_water_coliforms", "CFU/100mL", min_value=0, max_value=10, default=0),
            ParameterConfig("energy_consumption", "kWh/d", min_value=0, max_value=5000, default=1500),
            ParameterConfig("chemical_consumption", "kg/d", min_value=0, max_value=500, default=50),
        ],
        capabilities=["SteadyStateSimulation", "MassBalance", "WaterQualityPrediction"],
        treatment_config=[
            TreatmentConfig("turbidity", 95, 3),
            TreatmentConfig("toc", 80, 5),
            TreatmentConfig("coliforms", 99.9, 0.1),
        ],
        metadata={"location": "upstream", "supplies": ["DWP2"]},
    ),
    EntityConfig(
        entity_id="DWP2",
        entity_name="Drinking Water Plant 2",
        entity_type=EntityType.DRINKING_WATER_PLANT,
        port=8002,
        parameters=[
            ParameterConfig("design_capacity", "m³/d", default=75000),
            ParameterConfig("treatment_efficiency", "%", default=97.0),
        ],
        inputs=[
            ParameterConfig("raw_water_flow", "m³/d", min_value=0, max_value=80000, default=60000),
            ParameterConfig("raw_water_turbidity", "NTU", min_value=0, max_value=100, default=8),
            ParameterConfig("raw_water_toc", "mg/L", min_value=0, max_value=50, default=4),
            ParameterConfig("raw_water_ph", "-", min_value=6, max_value=9, default=7.6),
            ParameterConfig("raw_water_coliforms", "CFU/100mL", min_value=0, max_value=10000, default=80),
        ],
        outputs=[
            ParameterConfig("treated_water_flow", "m³/d", min_value=0, max_value=80000, default=60000),
            ParameterConfig("treated_water_turbidity", "NTU", min_value=0, max_value=5, default=0.3),
            ParameterConfig("treated_water_toc", "mg/L", min_value=0, max_value=10, default=0.8),
            ParameterConfig("treated_water_ph", "-", min_value=6.5, max_value=8.5, default=7.3),
            ParameterConfig("treated_water_coliforms", "CFU/100mL", min_value=0, max_value=10, default=0),
            ParameterConfig("energy_consumption", "kWh/d", min_value=0, max_value=8000, default=2200),
            ParameterConfig("chemical_consumption", "kg/d", min_value=0, max_value=800, default=75),
        ],
        capabilities=["SteadyStateSimulation", "MassBalance", "WaterQualityPrediction"],
        treatment_config=[
            TreatmentConfig("turbidity", 96, 2),
            TreatmentConfig("toc", 85, 4),
            TreatmentConfig("coliforms", 99.99, 0.01),
        ],
        metadata={"location": "downstream", "supplies": ["Dampoort", "Muide"]},
    ),
]

# Wastewater Treatment Plant Configurations
WWTP_CONFIGS: List[EntityConfig] = [
    EntityConfig(
        entity_id="WWTP1",
        entity_name="Wastewater Treatment Plant 1",
        entity_type=EntityType.WASTEWATER_TREATMENT_PLANT,
        port=8003,
        parameters=[
            ParameterConfig("design_capacity", "m³/d", default=100000),
            ParameterConfig("treatment_level", "%", default=95.0),
        ],
        inputs=[
            ParameterConfig("influent_flow", "m³/d", min_value=0, max_value=120000, default=80000),
            ParameterConfig("influent_BOD", "mg/L", min_value=0, max_value=500, default=200),
            ParameterConfig("influent_COD", "mg/L", min_value=0, max_value=1000, default=400),
            ParameterConfig("influent_TSS", "mg/L", min_value=0, max_value=500, default=250),
            ParameterConfig("influent_TN", "mg/L", min_value=0, max_value=100, default=40),
            ParameterConfig("influent_TP", "mg/L", min_value=0, max_value=20, default=8),
            ParameterConfig("influent_coliforms", "CFU/100mL", min_value=0, max_value=10000000, default=1000000),
        ],
        outputs=[
            ParameterConfig("effluent_flow", "m³/d", min_value=0, max_value=120000, default=80000),
            ParameterConfig("effluent_BOD", "mg/L", min_value=0, max_value=50, default=10),
            ParameterConfig("effluent_COD", "mg/L", min_value=0, max_value=100, default=30),
            ParameterConfig("effluent_TSS", "mg/L", min_value=0, max_value=50, default=10),
            ParameterConfig("effluent_TN", "mg/L", min_value=0, max_value=30, default=15),
            ParameterConfig("effluent_TP", "mg/L", min_value=0, max_value=5, default=1),
            ParameterConfig("effluent_coliforms", "CFU/100mL", min_value=0, max_value=100000, default=1000),
            ParameterConfig("sludge_production", "kg/d", min_value=0, max_value=5000, default=800),
            ParameterConfig("energy_consumption", "kWh/d", min_value=0, max_value=15000, default=5000),
        ],
        capabilities=["SteadyStateSimulation", "MassBalance", "WaterQualityPrediction"],
        treatment_config=[
            TreatmentConfig("BOD", 95, 2),
            TreatmentConfig("COD", 92.5, 3),
            TreatmentConfig("TSS", 96, 2),
            TreatmentConfig("TN", 62.5, 8),
            TreatmentConfig("TP", 87.5, 5),
            TreatmentConfig("coliforms", 99.9, 0.1),
        ],
        metadata={"location": "upstream", "receives_from": ["Muide"]},
    ),
    EntityConfig(
        entity_id="WWTP2",
        entity_name="Wastewater Treatment Plant 2",
        entity_type=EntityType.WASTEWATER_TREATMENT_PLANT,
        port=8004,
        parameters=[
            ParameterConfig("design_capacity", "m³/d", default=120000),
            ParameterConfig("treatment_level", "%", default=97.0),
        ],
        inputs=[
            ParameterConfig("influent_flow", "m³/d", min_value=0, max_value=150000, default=100000),
            ParameterConfig("influent_BOD", "mg/L", min_value=0, max_value=500, default=180),
            ParameterConfig("influent_COD", "mg/L", min_value=0, max_value=1000, default=350),
            ParameterConfig("influent_TSS", "mg/L", min_value=0, max_value=500, default=200),
            ParameterConfig("influent_TN", "mg/L", min_value=0, max_value=100, default=35),
            ParameterConfig("influent_TP", "mg/L", min_value=0, max_value=20, default=6),
            ParameterConfig("influent_coliforms", "CFU/100mL", min_value=0, max_value=10000000, default=800000),
        ],
        outputs=[
            ParameterConfig("effluent_flow", "m³/d", min_value=0, max_value=150000, default=100000),
            ParameterConfig("effluent_BOD", "mg/L", min_value=0, max_value=30, default=6),
            ParameterConfig("effluent_COD", "mg/L", min_value=0, max_value=75, default=20),
            ParameterConfig("effluent_TSS", "mg/L", min_value=0, max_value=30, default=5),
            ParameterConfig("effluent_TN", "mg/L", min_value=0, max_value=20, default=10),
            ParameterConfig("effluent_TP", "mg/L", min_value=0, max_value=3, default=0.5),
            ParameterConfig("effluent_coliforms", "CFU/100mL", min_value=0, max_value=50000, default=500),
            ParameterConfig("sludge_production", "kg/d", min_value=0, max_value=6000, default=1000),
            ParameterConfig("energy_consumption", "kWh/d", min_value=0, max_value=20000, default=6500),
        ],
        capabilities=["SteadyStateSimulation", "MassBalance", "WaterQualityPrediction"],
        treatment_config=[
            TreatmentConfig("BOD", 96.7, 1.5),
            TreatmentConfig("COD", 94.3, 2),
            TreatmentConfig("TSS", 97.5, 1.5),
            TreatmentConfig("TN", 71.4, 6),
            TreatmentConfig("TP", 91.7, 4),
            TreatmentConfig("coliforms", 99.94, 0.05),
        ],
        metadata={"location": "downstream", "receives_from": ["Dampoort", "Texfin", "FoodPro"]},
    ),
]

# Industry Configurations
INDUSTRY_CONFIGS: List[EntityConfig] = [
    EntityConfig(
        entity_id="Texfin",
        entity_name="Texfin Textile Industry",
        entity_type=EntityType.INDUSTRY,
        port=8005,
        parameters=[
            ParameterConfig("water_demand", "m³/d", default=2000),
            ParameterConfig("production_rate", "kg/d", default=500),
        ],
        inputs=[
            ParameterConfig("supply_water_flow", "m³/d", min_value=0, max_value=3000, default=2000),
            ParameterConfig("supply_water_quality", "-", default=1.0),
        ],
        outputs=[
            ParameterConfig("wastewater_flow", "m³/d", min_value=0, max_value=2500, default=1800),
            ParameterConfig("wastewater_COD", "mg/L", min_value=100, max_value=2000, default=800),
            ParameterConfig("wastewater_TSS", "mg/L", min_value=50, max_value=500, default=150),
            ParameterConfig("wastewater_color", "Pt-Co", min_value=50, max_value=500, default=200),
            ParameterConfig("wastewater_pH", "-", min_value=5, max_value=10, default=8),
            ParameterConfig("energy_consumption", "kWh/d", min_value=0, max_value=2000, default=500),
        ],
        capabilities=["SteadyStateSimulation", "MassBalance"],
        metadata={
            "industry_type": "textile",
            "discharges_to": "WWTP2",
            "water_reuse_rate": 0.1,
        },
    ),
    EntityConfig(
        entity_id="FoodPro",
        entity_name="FoodPro Food Processing",
        entity_type=EntityType.INDUSTRY,
        port=8006,
        parameters=[
            ParameterConfig("water_demand", "m³/d", default=1500),
            ParameterConfig("production_rate", "kg/d", default=1000),
        ],
        inputs=[
            ParameterConfig("supply_water_flow", "m³/d", min_value=0, max_value=2000, default=1500),
            ParameterConfig("supply_water_quality", "-", default=1.0),
        ],
        outputs=[
            ParameterConfig("wastewater_flow", "m³/d", min_value=0, max_value=1700, default=1300),
            ParameterConfig("wastewater_COD", "mg/L", min_value=500, max_value=3000, default=1500),
            ParameterConfig("wastewater_BOD", "mg/L", min_value=300, max_value=2000, default=800),
            ParameterConfig("wastewater_TSS", "mg/L", min_value=100, max_value=800, default=300),
            ParameterConfig("wastewater_fat", "mg/L", min_value=20, max_value=200, default=80),
            ParameterConfig("energy_consumption", "kWh/d", min_value=0, max_value=1500, default=400),
        ],
        capabilities=["SteadyStateSimulation", "MassBalance"],
        metadata={
            "industry_type": "food_processing",
            "discharges_to": "WWTP2",
            "water_reuse_rate": 0.15,
        },
    ),
    EntityConfig(
        entity_id="ChipTech",
        entity_name="ChipTech Electronics",
        entity_type=EntityType.INDUSTRY,
        port=8007,
        parameters=[
            ParameterConfig("water_demand", "m³/d", default=800),
            ParameterConfig("production_rate", "units/d", default=100),
        ],
        inputs=[
            ParameterConfig("supply_water_flow", "m³/d", min_value=0, max_value=1000, default=800),
            ParameterConfig("supply_water_quality", "-", default=1.0),
        ],
        outputs=[
            ParameterConfig("wastewater_flow", "m³/d", min_value=0, max_value=900, default=720),
            ParameterConfig("wastewater_COD", "mg/L", min_value=10, max_value=200, default=50),
            ParameterConfig("wastewater_TSS", "mg/L", min_value=5, max_value=100, default=20),
            ParameterConfig("wastewater_metals", "mg/L", min_value=0.1, max_value=10, default=1),
            ParameterConfig("wastewater_pH", "-", min_value=2, max_value=12, default=6),
            ParameterConfig("energy_consumption", "kWh/d", min_value=0, max_value=3000, default=1200),
        ],
        capabilities=["SteadyStateSimulation", "MassBalance"],
        metadata={
            "industry_type": "electronics",
            "discharges_to": "WWTP1",
            "water_reuse_rate": 0.1,
        },
    ),
    EntityConfig(
        entity_id="PharmaGen",
        entity_name="PharmaGen Pharmaceutical",
        entity_type=EntityType.INDUSTRY,
        port=8008,
        parameters=[
            ParameterConfig("water_demand", "m³/d", default=600),
            ParameterConfig("production_rate", "kg/d", default=50),
        ],
        inputs=[
            ParameterConfig("supply_water_flow", "m³/d", min_value=0, max_value=800, default=600),
            ParameterConfig("supply_water_quality", "-", default=1.0),
        ],
        outputs=[
            ParameterConfig("wastewater_flow", "m³/d", min_value=0, max_value=700, default=540),
            ParameterConfig("wastewater_COD", "mg/L", min_value=100, max_value=1500, default=400),
            ParameterConfig("wastewater_BOD", "mg/L", min_value=50, max_value=800, default=200),
            ParameterConfig("wastewater_TSS", "mg/L", min_value=10, max_value=200, default=50),
            ParameterConfig("wastewater_pH", "-", min_value=4, max_value=10, default=7),
            ParameterConfig("wastewater_residuals", "mg/L", min_value=1, max_value=100, default=10),
            ParameterConfig("energy_consumption", "kWh/d", min_value=0, max_value=2000, default=800),
        ],
        capabilities=["SteadyStateSimulation", "MassBalance"],
        metadata={
            "industry_type": "pharmaceutical",
            "discharges_to": "WWTP1",
            "water_reuse_rate": 0.1,
        },
    ),
    EntityConfig(
        entity_id="BrewCo",
        entity_name="BrewCo Brewery",
        entity_type=EntityType.INDUSTRY,
        port=8009,
        parameters=[
            ParameterConfig("water_demand", "m³/d", default=1000),
            ParameterConfig("production_rate", "hl/d", default=200),
        ],
        inputs=[
            ParameterConfig("supply_water_flow", "m³/d", min_value=0, max_value=1500, default=1000),
            ParameterConfig("supply_water_quality", "-", default=1.0),
        ],
        outputs=[
            ParameterConfig("wastewater_flow", "m³/d", min_value=0, max_value=1200, default=900),
            ParameterConfig("wastewater_COD", "mg/L", min_value=500, max_value=2500, default=1200),
            ParameterConfig("wastewater_BOD", "mg/L", min_value=300, max_value=1500, default=600),
            ParameterConfig("wastewater_TSS", "mg/L", min_value=50, max_value=400, default=150),
            ParameterConfig("wastewater_pH", "-", min_value=4, max_value=9, default=6),
            ParameterConfig("energy_consumption", "kWh/d", min_value=0, max_value=1500, default=500),
        ],
        capabilities=["SteadyStateSimulation", "MassBalance"],
        metadata={
            "industry_type": "brewery",
            "discharges_to": "WWTP1",
            "water_reuse_rate": 0.2,
        },
    ),
]

# Residential District Configurations
RESIDENTIAL_CONFIGS: List[EntityConfig] = [
    EntityConfig(
        entity_id="Dampoort",
        entity_name="Dampoort Residential District",
        entity_type=EntityType.RESIDENTIAL,
        port=8011,
        parameters=[
            ParameterConfig("population", "persons", default=15000),
            ParameterConfig("per_capita_water_use", "L/person/d", default=150),
        ],
        inputs=[
            ParameterConfig("supply_water_flow", "m³/d", min_value=0, max_value=3000, default=2250),
            ParameterConfig("population", "persons", min_value=0, max_value=30000, default=15000),
        ],
        outputs=[
            ParameterConfig("wastewater_flow", "m³/d", min_value=0, max_value=2700, default=2025),
            ParameterConfig("wastewater_BOD", "mg/L", min_value=150, max_value=400, default=250),
            ParameterConfig("wastewater_COD", "mg/L", min_value=300, max_value=700, default=450),
            ParameterConfig("wastewater_TSS", "mg/L", min_value=100, max_value=400, default=200),
            ParameterConfig("wastewater_TN", "mg/L", min_value=30, max_value=80, default=50),
            ParameterConfig("wastewater_TP", "mg/L", min_value=3, max_value=12, default=6),
            ParameterConfig("wastewater_coliforms", "CFU/100mL", min_value=100000, max_value=10000000, default=1000000),
        ],
        capabilities=["SteadyStateSimulation", "MassBalance"],
        metadata={"discharges_to": "WWTP2"},
    ),
    EntityConfig(
        entity_id="Muide",
        entity_name="Muide Residential District",
        entity_type=EntityType.RESIDENTIAL,
        port=8012,
        parameters=[
            ParameterConfig("population", "persons", default=12000),
            ParameterConfig("per_capita_water_use", "L/person/d", default=150),
        ],
        inputs=[
            ParameterConfig("supply_water_flow", "m³/d", min_value=0, max_value=2500, default=1800),
            ParameterConfig("population", "persons", min_value=0, max_value=25000, default=12000),
        ],
        outputs=[
            ParameterConfig("wastewater_flow", "m³/d", min_value=0, max_value=2250, default=1620),
            ParameterConfig("wastewater_BOD", "mg/L", min_value=150, max_value=400, default=250),
            ParameterConfig("wastewater_COD", "mg/L", min_value=300, max_value=700, default=450),
            ParameterConfig("wastewater_TSS", "mg/L", min_value=100, max_value=400, default=200),
            ParameterConfig("wastewater_TN", "mg/L", min_value=30, max_value=80, default=50),
            ParameterConfig("wastewater_TP", "mg/L", min_value=3, max_value=12, default=6),
            ParameterConfig("wastewater_coliforms", "CFU/100mL", min_value=100000, max_value=10000000, default=1000000),
        ],
        capabilities=["SteadyStateSimulation", "MassBalance"],
        metadata={"discharges_to": "WWTP1"},
    ),
]

# River Configuration
RIVER_CONFIGS: List[EntityConfig] = [
    EntityConfig(
        entity_id="River",
        entity_name="Lieve River",
        entity_type=EntityType.RIVER,
        port=8010,
        parameters=[
            ParameterConfig("river_length", "km", default=10),
            ParameterConfig("flow_rate", "m³/s", default=5.0),
            ParameterConfig("dilution_factor", "-", default=1.0),
        ],
        inputs=[
            ParameterConfig("upstream_flow", "m³/d", min_value=0, max_value=500000, default=200000),
            ParameterConfig("upstream_quality", "-", min_value=0, max_value=1, default=0.8),
            ParameterConfig("discharge_flows", "m³/d", min_value=0, max_value=200000, default=[50000, 30000]),
            ParameterConfig("discharge_qualities", "-", min_value=0, max_value=1, default=[0.6, 0.7]),
        ],
        outputs=[
            ParameterConfig("downstream_flow", "m³/d", min_value=0, max_value=600000, default=280000),
            ParameterConfig("downstream_quality", "-", min_value=0, max_value=1, default=0.75),
            ParameterConfig("flow_contribution_upstream", "%", default=71.4),
            ParameterConfig("flow_contribution_total_discharge", "%", default=28.6),
        ],
        capabilities=["SteadyStateSimulation", "MassBalance"],
        metadata={
            "receives_from": ["WWTP1", "WWTP2"],
            "discharges_to": "River_mouth",
        },
    ),
]

# All configurations combined
ALL_CONFIGS: Dict[str, EntityConfig] = {
    **{cfg.entity_id: cfg for cfg in DWP_CONFIGS},
    **{cfg.entity_id: cfg for cfg in WWTP_CONFIGS},
    **{cfg.entity_id: cfg for cfg in INDUSTRY_CONFIGS},
    **{cfg.entity_id: cfg for cfg in RESIDENTIAL_CONFIGS},
    **{cfg.entity_id: cfg for cfg in RIVER_CONFIGS},
}


def get_config(entity_id: str) -> EntityConfig:
    """Get configuration for a specific entity.

    Args:
        entity_id: The entity identifier (e.g., "DWP1", "WWTP1").

    Returns:
        EntityConfig for the requested entity.

    Raises:
        KeyError: If entity_id is not found.
    """
    if entity_id not in ALL_CONFIGS:
        raise KeyError(f"Unknown entity_id: {entity_id}. Available: {list(ALL_CONFIGS.keys())}")
    return ALL_CONFIGS[entity_id]


def list_all_entity_ids() -> List[str]:
    """List all entity IDs.

    Returns:
        List of all entity identifiers.
    """
    return list(ALL_CONFIGS.keys())
