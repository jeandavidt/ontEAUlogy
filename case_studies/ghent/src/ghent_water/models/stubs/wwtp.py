"""Wastewater Treatment Plant Stub Model.

Simulates wastewater treatment processes with configurable
treatment efficiencies for BOD, COD, TSS, nutrients, and pathogens.
Includes scenario support and VLAREM II compliance checking.
"""

import random
from typing import Any, Dict, List, Optional
import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ..base import BaseWaterModel, ModelStatus


# VLAREM II compliance limits (Belgian water regulations)
VLAREM_II_LIMITS = {
    "BOD": 25,  # mg/L
    "COD": 125,  # mg/L
    "TSS": 35,  # mg/L
    "Total_N": 15,  # mg/L as N
    "Total_P": 2,  # mg/L as P
}

# Supported scenarios
SCENARIOS = ["baseline", "high_load", "low_efficiency", "high_efficiency", "storm_event"]


def check_vlarem_compliance(effluent: Dict) -> Dict[str, Any]:
    """Check effluent against VLAREM II limits.
    
    Args:
        effluent: Dictionary containing effluent parameters.
        
    Returns:
        Dictionary with compliance status and violations.
    """
    violations = {}
    is_compliant = True
    
    # Map effluent keys to VLAREM parameter names
    param_mapping = {
        "effluent_BOD": ("BOD", VLAREM_II_LIMITS["BOD"]),
        "effluent_COD": ("COD", VLAREM_II_LIMITS["COD"]),
        "effluent_TSS": ("TSS", VLAREM_II_LIMITS["TSS"]),
        "effluent_TN": ("Total_N", VLAREM_II_LIMITS["Total_N"]),
        "effluent_TP": ("Total_P", VLAREM_II_LIMITS["Total_P"]),
    }
    
    for key, (name, limit) in param_mapping.items():
        if key in effluent:
            value = effluent[key]
            is_violation = value > limit
            violations[name] = {
                "value": value,
                "limit": limit,
                "unit": "mg/L",
                "is_violation": is_violation,
                "excess_pct": ((value - limit) / limit * 100) if is_violation else 0,
            }
            if is_violation:
                is_compliant = False
    
    return {
        "is_compliant": is_compliant,
        "violations": violations,
        "regulation": "VLAREM II",
    }


# Pydantic models for request/response validation
class WWTPSimulationInput(BaseModel):
    """Input parameters for WWTP simulation."""

    influent_flow: float = Field(default=25000.0, description="Influent flow rate (m³/d)")
    influent_BOD: float = Field(default=250.0, description="Influent BOD concentration (mg/L)")
    influent_COD: float = Field(default=500.0, description="Influent COD concentration (mg/L)")
    influent_TSS: float = Field(
        default=300.0, description="Influent total suspended solids (mg/L)"
    )
    influent_TN: float = Field(default=45.0, description="Influent total nitrogen (mg/L)")
    influent_TP: float = Field(default=8.0, description="Influent total phosphorus (mg/L)")
    influent_coliforms: float = Field(
        default=1e7, description="Influent coliform count (CFU/100mL)"
    )
    scenario: str = Field(default="baseline", description="Simulation scenario")


class WWTPSimulationOutput(BaseModel):
    """Output parameters from WWTP simulation."""

    effluent_flow: float = Field(..., description="Effluent flow rate (m³/d)")
    effluent_BOD: float = Field(..., description="Effluent BOD concentration (mg/L)")
    effluent_COD: float = Field(..., description="Effluent COD concentration (mg/L)")
    effluent_TSS: float = Field(..., description="Effluent total suspended solids (mg/L)")
    effluent_TN: float = Field(..., description="Effluent total nitrogen (mg/L)")
    effluent_TP: float = Field(..., description="Effluent total phosphorus (mg/L)")
    effluent_coliforms: float = Field(..., description="Effluent coliform count")
    sludge_production: float = Field(..., description="Sludge production (kg/d)")
    energy_consumption: float = Field(..., description="Energy consumption (kWh/d)")
    removal_efficiency_BOD: float = Field(..., description="BOD removal efficiency (%)")
    removal_efficiency_COD: float = Field(..., description="COD removal efficiency (%)")
    removal_efficiency_TSS: float = Field(..., description="TSS removal efficiency (%)")
    removal_efficiency_TN: float = Field(..., description="TN removal efficiency (%)")
    removal_efficiency_TP: float = Field(..., description="TP removal efficiency (%)")
    removal_efficiency_coliforms: float = Field(..., description="Coliform removal efficiency (%)")
    compliance_status: Dict[str, Any] = Field(..., description="VLAREM II compliance status")
    scenario: str = Field(..., description="Applied scenario")


class WastewaterTreatmentPlantStub(BaseWaterModel):
    """Stub implementation for Wastewater Treatment Plant model.

    Simulates secondary and tertiary treatment with configurable
    efficiencies for organic matter, solids, nutrients, and pathogens.
    """

    def __init__(
        self,
        entity_id: str = "WWTP1",
        entity_name: str = "Wastewater Treatment Plant 1",
        port: int = 8003,
        treatment_efficiencies: Optional[Dict[str, float]] = None,
        **kwargs,
    ):
        """Initialize WWTP stub.

        Args:
            entity_id: Entity identifier (WWTP1 or WWTP2)
            entity_name: Human-readable name
            port: Service port
            treatment_efficiencies: Custom treatment efficiencies
            **kwargs: Additional base class arguments
        """
        # Default treatment efficiencies
        self.treatment_efficiencies = treatment_efficiencies or {
            "BOD": 95.0,
            "COD": 92.5,
            "TSS": 96.0,
            "TN": 62.5,
            "TP": 87.5,
            "coliforms": 99.9,
        }

        # Define capabilities
        capabilities = ["SteadyStateSimulation", "MassBalance", "WaterQualityPrediction"]

        # Define input parameters
        inputs = [
            {"name": "influent_flow", "unit": "m³/d", "datatype": "float"},
            {"name": "influent_BOD", "unit": "mg/L", "datatype": "float"},
            {"name": "influent_COD", "unit": "mg/L", "datatype": "float"},
            {"name": "influent_TSS", "unit": "mg/L", "datatype": "float"},
            {"name": "influent_TN", "unit": "mg/L", "datatype": "float"},
            {"name": "influent_TP", "unit": "mg/L", "datatype": "float"},
            {"name": "influent_coliforms", "unit": "CFU/100mL", "datatype": "float"},
        ]

        # Define output parameters
        outputs = [
            {"name": "effluent_flow", "unit": "m³/d", "datatype": "float"},
            {"name": "effluent_BOD", "unit": "mg/L", "datatype": "float"},
            {"name": "effluent_COD", "unit": "mg/L", "datatype": "float"},
            {"name": "effluent_TSS", "unit": "mg/L", "datatype": "float"},
            {"name": "effluent_TN", "unit": "mg/L", "datatype": "float"},
            {"name": "effluent_TP", "unit": "mg/L", "datatype": "float"},
            {"name": "effluent_coliforms", "unit": "CFU/100mL", "datatype": "float"},
            {"name": "sludge_production", "unit": "kg/d", "datatype": "float"},
            {"name": "energy_consumption", "unit": "kWh/d", "datatype": "float"},
        ]

        metadata = {
            "treatment_type": "conventional_activated_sludge",
            "location": "upstream" if entity_id == "WWTP1" else "downstream",
            "receives_from": ["Muide"] if entity_id == "WWTP1" else ["Dampoort", "Texfin", "FoodPro"],
        }

        super().__init__(
            entity_id=entity_id,
            entity_name=entity_name,
            entity_type="WastewaterTreatmentPlant",
            port=port,
            capabilities=capabilities,
            inputs=inputs,
            outputs=outputs,
            metadata=metadata,
        )

        # Create FastAPI app for this model
        self.app = FastAPI(
            title=f"{entity_name} Model",
            description="Stub wastewater treatment plant model with waterFRAME ontology self-description",
            version="0.1.0",
        )
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Set up FastAPI routes."""

        @self.app.get("/describe")
        async def describe():
            """Return JSON-LD self-description."""
            return await self.describe()

        @self.app.get("/describe/turtle")
        async def describe_turtle():
            """Return TTL self-description."""
            return {"ttl": self.generate_ttl_description()}

        @self.app.get("/describe/agent")
        async def describe_agent():
            """Return agent-aware TTL self-description."""
            return {"ttl": self.generate_agent_ttl()}

        @self.app.post("/simulate")
        async def simulate(inputs: WWTPSimulationInput):
            """Run simulation with given inputs."""
            result = await self.simulate(inputs.model_dump())
            return result

        @self.app.get("/state")
        async def state():
            """Return current model state."""
            return await self.get_state()

        @self.app.get("/health")
        async def health():
            """Health check endpoint."""
            return await self.health_check()

    async def describe(self) -> Dict[str, Any]:
        """Generate JSON-LD self-description."""
        inputs_list = []
        for inp in self.inputs:
            inputs_list.append({
                "@type": "wf:Parameter",
                "wf:parameterName": inp["name"],
                "wf:hasUnit": inp["unit"],
                "wf:hasDataType": inp["datatype"],
            })

        outputs_list = []
        for out in self.outputs:
            outputs_list.append({
                "@type": "wf:Parameter",
                "wf:parameterName": out["name"],
                "wf:hasUnit": out["unit"],
                "wf:hasDataType": out["datatype"],
            })

        capabilities_list = []
        for cap in self.capabilities:
            capabilities_list.append({
                "@type": f"cap:{cap}",
            })

        return {
            "@context": {
                "wf": "https://w3id.org/waterframe/",
                "cap": "https://w3id.org/waterframe/capability/",
                "ghent": "https://w3id.org/waterframe/case/ghent/",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            },
            "@graph": [
                {
                    "@id": f"ghent:{self.entity_id}_Model",
                    "@type": "wf:ProcessModel",
                    "rdfs:label": self.entity_name,
                    "wf:representsEntity": f"ghent:{self.entity_id}",
                    "wf:hasIdentifier": self.entity_id,
                    "wf:hasCapability": capabilities_list,
                    "wf:hasInput": inputs_list,
                    "wf:hasOutput": outputs_list,
                    "wf:implementedBy": "stub",
                    "wf:apiEndpoint": self.api_endpoint,
                    "wf:port": self.port,
                }
            ],
        }

    async def simulate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run wastewater treatment simulation.

        Applies treatment efficiencies to influent parameters.
        Supports multiple scenarios for different operating conditions.
        Returns compliance status against VLAREM II limits.
        """
        # Get scenario from inputs (default to baseline)
        scenario = inputs.get("scenario", "baseline")
        
        # Apply scenario effects to influent conditions
        scenario_modifiers = self._get_scenario_modifiers(scenario)
        
        # Extract input values with scenario-adjusted defaults
        base_influent_flow = self._get_parameter_value(inputs, "influent_flow", 80000.0)
        base_influent_BOD = self._get_parameter_value(inputs, "influent_BOD", 200.0)
        base_influent_COD = self._get_parameter_value(inputs, "influent_COD", 400.0)
        base_influent_TSS = self._get_parameter_value(inputs, "influent_TSS", 250.0)
        base_influent_TN = self._get_parameter_value(inputs, "influent_TN", 40.0)
        base_influent_TP = self._get_parameter_value(inputs, "influent_TP", 8.0)
        base_influent_coliforms = self._get_parameter_value(inputs, "influent_coliforms", 1000000.0)
        
        # Apply scenario modifiers
        influent_flow = base_influent_flow * scenario_modifiers.get("flow_factor", 1.0)
        influent_BOD = base_influent_BOD * scenario_modifiers.get("bod_factor", 1.0)
        influent_COD = base_influent_COD * scenario_modifiers.get("cod_factor", 1.0)
        influent_TSS = base_influent_TSS * scenario_modifiers.get("tss_factor", 1.0)
        influent_TN = base_influent_TN * scenario_modifiers.get("tn_factor", 1.0)
        influent_TP = base_influent_TP * scenario_modifiers.get("tp_factor", 1.0)
        influent_coliforms = base_influent_coliforms * scenario_modifiers.get("coliform_factor", 1.0)
        
        # Calculate flow (typically small losses to sludge)
        effluent_flow = influent_flow * (1 - random.uniform(0.01, 0.03))
        
        # Get scenario-adjusted treatment efficiencies
        efficiencies = self._get_scenario_efficiencies(scenario)
        
        # Apply treatment efficiencies with variance
        def apply_efficiency(value: float, param: str) -> tuple[float, float]:
            eff = efficiencies.get(param, 90.0) + random.uniform(-2, 2)
            eff = max(0, min(100, eff))
            return value * (1 - eff / 100), eff

        effluent_BOD, removal_BOD = apply_efficiency(influent_BOD, "BOD")
        effluent_COD, removal_COD = apply_efficiency(influent_COD, "COD")
        effluent_TSS, removal_TSS = apply_efficiency(influent_TSS, "TSS")
        effluent_TN, removal_TN = apply_efficiency(influent_TN, "TN")
        effluent_TP, removal_TP = apply_efficiency(influent_TP, "TP")
        effluent_coliforms, removal_coliforms = apply_efficiency(influent_coliforms, "coliforms")

        # Sludge production correlates with TSS and BOD removal
        sludge_from_TSS = influent_TSS * effluent_flow * (removal_TSS / 100) / 1000  # kg/d
        sludge_from_BOD = influent_BOD * effluent_flow * (removal_BOD / 100) * 0.3 / 1000  # biodegradation
        sludge_production = sludge_from_TSS + sludge_from_BOD

        # Energy consumption
        base_energy = effluent_flow * 0.05  # kWh per m³
        energy_consumption = base_energy * (1 + influent_BOD / 400)

        # Build effluent dictionary for compliance checking
        effluent_dict = {
            "effluent_BOD": effluent_BOD,
            "effluent_COD": effluent_COD,
            "effluent_TSS": effluent_TSS,
            "effluent_TN": effluent_TN,
            "effluent_TP": effluent_TP,
        }
        
        # Check compliance with VLAREM II
        compliance_status = check_vlarem_compliance(effluent_dict)

        result = {
            "effluent_flow": round(effluent_flow, 2),
            "effluent_BOD": round(effluent_BOD, 2),
            "effluent_COD": round(effluent_COD, 2),
            "effluent_TSS": round(effluent_TSS, 2),
            "effluent_TN": round(effluent_TN, 2),
            "effluent_TP": round(effluent_TP, 3),
            "effluent_coliforms": round(effluent_coliforms, 0),
            "sludge_production": round(sludge_production, 1),
            "energy_consumption": round(energy_consumption, 1),
            "removal_efficiency_BOD": round(removal_BOD, 2),
            "removal_efficiency_COD": round(removal_COD, 2),
            "removal_efficiency_TSS": round(removal_TSS, 2),
            "removal_efficiency_TN": round(removal_TN, 2),
            "removal_efficiency_TP": round(removal_TP, 2),
            "removal_efficiency_coliforms": round(removal_coliforms, 2),
            "compliance_status": compliance_status,
            "scenario": scenario,
        }

        self._update_state(result, ModelStatus.RUNNING)
        return result
    
    def _get_scenario_modifiers(self, scenario: str) -> Dict[str, float]:
        """Get influent modifiers for a scenario.
        
        Args:
            scenario: Scenario name.
            
        Returns:
            Dictionary of modifiers to apply to influent values.
        """
        scenarios = {
            "baseline": {
                "flow_factor": 1.0, "bod_factor": 1.0, "cod_factor": 1.0,
                "tss_factor": 1.0, "tn_factor": 1.0, "tp_factor": 1.0,
                "coliform_factor": 1.0,
            },
            "high_load": {
                "flow_factor": 1.0, "bod_factor": 1.5, "cod_factor": 1.4,
                "tss_factor": 1.3, "tn_factor": 1.2, "tp_factor": 1.2,
                "coliform_factor": 1.5,
            },
            "low_efficiency": {
                "flow_factor": 1.0, "bod_factor": 1.0, "cod_factor": 1.0,
                "tss_factor": 1.0, "tn_factor": 1.0, "tp_factor": 1.0,
                "coliform_factor": 1.0,
            },
            "high_efficiency": {
                "flow_factor": 1.0, "bod_factor": 1.0, "cod_factor": 1.0,
                "tss_factor": 1.0, "tn_factor": 1.0, "tp_factor": 1.0,
                "coliform_factor": 1.0,
            },
            "storm_event": {
                "flow_factor": 2.0, "bod_factor": 0.7, "cod_factor": 0.8,
                "tss_factor": 2.0, "tn_factor": 0.9, "tp_factor": 1.1,
                "coliform_factor": 1.2,
            },
        }
        return scenarios.get(scenario, scenarios["baseline"])
    
    def _get_scenario_efficiencies(self, scenario: str) -> Dict[str, float]:
        """Get treatment efficiencies for a scenario.
        
        Args:
            scenario: Scenario name.
            
        Returns:
            Dictionary of treatment efficiencies.
        """
        # Base efficiencies from instance config
        base_eff = self.treatment_efficiencies.copy()
        
        scenario_efficiencies = {
            "baseline": base_eff,
            "high_load": {k: v * 0.85 for k, v in base_eff.items()},  # 15% less efficient
            "low_efficiency": {k: v * 0.7 for k, v in base_eff.items()},  # 30% less efficient
            "high_efficiency": {k: min(99.9, v * 1.05) for k, v in base_eff.items()},  # 5% more efficient
            "storm_event": {k: v * 0.6 for k, v in base_eff.items()},  # 40% less efficient (dilution)
        }
        
        return scenario_efficiencies.get(scenario, base_eff)


def create_wwtp_model(entity_id: str = "WWTP1", port: int = 8003) -> WastewaterTreatmentPlantStub:
    """Factory function to create a WWTP model.

    Args:
        entity_id: Entity identifier (WWTP1 or WWTP2)
        port: Service port

    Returns:
        Configured WastewaterTreatmentPlantStub instance
    """
    entity_names = {
        "WWTP1": "Wastewater Treatment Plant 1",
        "WWTP2": "Wastewater Treatment Plant 2",
    }
    efficiency_configs = {
        "WWTP1": {"BOD": 95.0, "COD": 92.5, "TSS": 96.0, "TN": 62.5, "TP": 87.5, "coliforms": 99.9},
        "WWTP2": {"BOD": 96.7, "COD": 94.3, "TSS": 97.5, "TN": 71.4, "TP": 91.7, "coliforms": 99.94},
    }

    return WastewaterTreatmentPlantStub(
        entity_id=entity_id,
        entity_name=entity_names.get(entity_id, f"Wastewater Treatment Plant {entity_id[-1]}"),
        port=port,
        treatment_efficiencies=efficiency_configs.get(entity_id),
    )
