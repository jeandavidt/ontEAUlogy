"""Wastewater Treatment Plant Stub Model.

Simulates wastewater treatment processes with configurable
treatment efficiencies for BOD, COD, TSS, nutrients, and pathogens.
"""

import random
from typing import Any, Dict, List, Optional
import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ..base import BaseWaterModel


# Pydantic models for request/response validation
class WWTPSimulationInput(BaseModel):
    """Input parameters for WWTP simulation."""

    influent_flow: float = Field(..., description="Influent flow rate (m³/d)")
    influent_BOD: float = Field(..., description="Influent BOD concentration (mg/L)")
    influent_COD: float = Field(..., description="Influent COD concentration (mg/L)")
    influent_TSS: float = Field(..., description="Influent total suspended solids (mg/L)")
    influent_TN: float = Field(..., description="Influent total nitrogen (mg/L)")
    influent_TP: float = Field(..., description="Influent total phosphorus (mg/L)")
    influent_coliforms: float = Field(..., description="Influent coliform count (CFU/100mL)")


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
        """
        # Extract input values
        influent_flow = self._get_parameter_value(inputs, "influent_flow", 80000.0)
        influent_BOD = self._get_parameter_value(inputs, "influent_BOD", 200.0)
        influent_COD = self._get_parameter_value(inputs, "influent_COD", 400.0)
        influent_TSS = self._get_parameter_value(inputs, "influent_TSS", 250.0)
        influent_TN = self._get_parameter_value(inputs, "influent_TN", 40.0)
        influent_TP = self._get_parameter_value(inputs, "influent_TP", 8.0)
        influent_coliforms = self._get_parameter_value(inputs, "influent_coliforms", 1000000.0)

        # Calculate flow (typically small losses to sludge)
        effluent_flow = influent_flow * (1 - random.uniform(0.01, 0.03))

        # Apply treatment efficiencies with variance
        def apply_efficiency(value: float, param: str) -> tuple[float, float]:
            eff = self.treatment_efficiencies.get(param, 90.0) + random.uniform(-2, 2)
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
        }

        self._update_state(result)
        return result

    async def get_state(self) -> Dict[str, Any]:
        """Return current model state."""
        return self._state


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
