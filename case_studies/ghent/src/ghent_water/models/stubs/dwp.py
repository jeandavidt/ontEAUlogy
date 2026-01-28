"""Drinking Water Plant Stub Model.

Simulates drinking water treatment processes using configurable
removal efficiencies for various water quality parameters.
"""

import random
from typing import Any, Dict, List, Optional
import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ..base import BaseWaterModel, CASE_GHENT, CAP, ModelStatus


# Pydantic models for request/response validation
class DWPSimulationInput(BaseModel):
    """Input parameters for DWP simulation."""

    raw_water_flow: float = Field(
        default=40000.0, description="Raw water intake flow rate (m³/d)"
    )
    raw_water_turbidity: float = Field(
        default=10.0, description="Raw water turbidity (NTU)"
    )
    raw_water_toc: float = Field(
        default=5.0, description="Raw water total organic carbon (mg/L)"
    )
    raw_water_ph: float = Field(default=7.5, description="Raw water pH")
    raw_water_coliforms: float = Field(
        default=100.0, description="Raw water coliform count (CFU/100mL)"
    )


class DWPSimulationOutput(BaseModel):
    """Output parameters from DWP simulation."""

    treated_water_flow: float = Field(..., description="Treated water output flow rate (m³/d)")
    treated_water_turbidity: float = Field(..., description="Treated water turbidity (NTU)")
    treated_water_toc: float = Field(..., description="Treated water TOC (mg/L)")
    treated_water_ph: float = Field(..., description="Treated water pH")
    treated_water_coliforms: float = Field(..., description="Treated water coliform count")
    energy_consumption: float = Field(..., description="Energy consumption (kWh/d)")
    chemical_consumption: float = Field(..., description="Chemical consumption (kg/d)")
    removal_efficiency_turbidity: float = Field(..., description="Turbidity removal efficiency (%)")
    removal_efficiency_toc: float = Field(..., description="TOC removal efficiency (%)")
    removal_efficiency_coliforms: float = Field(..., description="Coliform removal efficiency (%)")


class DrinkingWaterPlantStub(BaseWaterModel):
    """Stub implementation for Drinking Water Plant model.

    Simulates water treatment processes with configurable removal rates
    for turbidity, TOC, and microbial contaminants.
    """

    def __init__(
        self,
        entity_id: str = "DWP1",
        entity_name: str = "Drinking Water Plant 1",
        port: int = 8001,
        removal_rates: Optional[Dict[str, float]] = None,
        **kwargs,
    ):
        """Initialize DWP stub.

        Args:
            entity_id: Entity identifier (DWP1 or DWP2)
            entity_name: Human-readable name
            port: Service port
            removal_rates: Custom removal rates for parameters
            **kwargs: Additional base class arguments
        """
        # Default removal rates
        self.removal_rates = removal_rates or {
            "turbidity": 95.0,
            "toc": 80.0,
            "coliforms": 99.9,
        }

        # Define capabilities
        capabilities = ["SteadyStateSimulation", "MassBalance", "WaterQualityPrediction"]

        # Define input parameters
        inputs = [
            {"name": "raw_water_flow", "unit": "m³/d", "datatype": "float"},
            {"name": "raw_water_turbidity", "unit": "NTU", "datatype": "float"},
            {"name": "raw_water_toc", "unit": "mg/L", "datatype": "float"},
            {"name": "raw_water_ph", "unit": "-", "datatype": "float"},
            {"name": "raw_water_coliforms", "unit": "CFU/100mL", "datatype": "float"},
        ]

        # Define output parameters
        outputs = [
            {"name": "treated_water_flow", "unit": "m³/d", "datatype": "float"},
            {"name": "treated_water_turbidity", "unit": "NTU", "datatype": "float"},
            {"name": "treated_water_toc", "unit": "mg/L", "datatype": "float"},
            {"name": "treated_water_ph", "unit": "-", "datatype": "float"},
            {"name": "treated_water_coliforms", "unit": "CFU/100mL", "datatype": "float"},
            {"name": "energy_consumption", "unit": "kWh/d", "datatype": "float"},
            {"name": "chemical_consumption", "unit": "kg/d", "datatype": "float"},
        ]

        metadata = {
            "treatment_type": "conventional",
            "location": "upstream" if entity_id == "DWP1" else "downstream",
            "supplies": ["DWP2"] if entity_id == "DWP1" else ["Dampoort", "Muide"],
        }

        super().__init__(
            entity_id=entity_id,
            entity_name=entity_name,
            entity_type="DrinkingWaterPlant",
            port=port,
            capabilities=capabilities,
            inputs=inputs,
            outputs=outputs,
            metadata=metadata,
        )

        # Create FastAPI app for this model
        self.app = FastAPI(
            title=f"{entity_name} Model",
            description="Stub drinking water plant model with waterFRAME ontology self-description",
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
        async def simulate(inputs: DWPSimulationInput):
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
        """Run drinking water treatment simulation.

        Applies removal rates to input water quality parameters.
        """
        # Extract input values with defaults
        raw_flow = self._get_parameter_value(inputs, "raw_water_flow", 40000.0)
        raw_turbidity = self._get_parameter_value(inputs, "raw_water_turbidity", 10.0)
        raw_toc = self._get_parameter_value(inputs, "raw_water_toc", 5.0)
        raw_ph = self._get_parameter_value(inputs, "raw_water_ph", 7.5)
        raw_coliforms = self._get_parameter_value(inputs, "raw_water_coliforms", 100.0)

        # Calculate flow loss (typically 5-10% for backwash, sludge)
        flow_loss_factor = 0.05 + random.uniform(-0.02, 0.02)
        treated_flow = raw_flow * (1 - flow_loss_factor)

        # Apply removal rates with variance
        turbidity_removal = self.removal_rates.get("turbidity", 95.0) + random.uniform(-3, 3)
        turbidity_removal = max(0, min(100, turbidity_removal))
        treated_turbidity = raw_turbidity * (1 - turbidity_removal / 100)

        toc_removal = self.removal_rates.get("toc", 80.0) + random.uniform(-5, 5)
        toc_removal = max(0, min(100, toc_removal))
        treated_toc = raw_toc * (1 - toc_removal / 100)

        coliform_removal = self.removal_rates.get("coliforms", 99.9) + random.uniform(-0.1, 0.1)
        coliform_removal = max(0, min(100, coliform_removal))
        treated_coliforms = raw_coliforms * (1 - coliform_removal / 100)

        # pH adjustment (typically slight acidification then neutralization)
        ph_adjustment = random.uniform(-0.3, 0.3)
        treated_ph = raw_ph + ph_adjustment
        treated_ph = max(6.5, min(8.5, treated_ph))

        # Energy consumption correlates with flow and treatment intensity
        base_energy = treated_flow * 0.025  # kWh per m³
        energy_consumption = base_energy * (1 + turbidity_removal / 200)

        # Chemical consumption for coagulation, disinfection
        base_chemical = treated_flow * 0.001  # kg per m³
        chemical_consumption = base_chemical * (1 + raw_turbidity / 20)

        result = {
            "treated_water_flow": round(treated_flow, 2),
            "treated_water_turbidity": round(treated_turbidity, 3),
            "treated_water_toc": round(treated_toc, 2),
            "treated_water_ph": round(treated_ph, 2),
            "treated_water_coliforms": round(treated_coliforms, 1),
            "energy_consumption": round(energy_consumption, 1),
            "chemical_consumption": round(chemical_consumption, 2),
            "removal_efficiency_turbidity": round(turbidity_removal, 2),
            "removal_efficiency_toc": round(toc_removal, 2),
            "removal_efficiency_coliforms": round(coliform_removal, 2),
        }

        self._update_state(result, ModelStatus.RUNNING)
        return result


def create_dwp_model(entity_id: str = "DWP1", port: int = 8001) -> DrinkingWaterPlantStub:
    """Factory function to create a DWP model.

    Args:
        entity_id: Entity identifier (DWP1 or DWP2)
        port: Service port

    Returns:
        Configured DrinkingWaterPlantStub instance
    """
    entity_names = {
        "DWP1": "Drinking Water Plant 1",
        "DWP2": "Drinking Water Plant 2",
    }
    removal_configs = {
        "DWP1": {"turbidity": 95.0, "toc": 80.0, "coliforms": 99.9},
        "DWP2": {"turbidity": 96.0, "toc": 85.0, "coliforms": 99.99},
    }

    return DrinkingWaterPlantStub(
        entity_id=entity_id,
        entity_name=entity_names.get(entity_id, f"Drinking Water Plant {entity_id[-1]}"),
        port=port,
        removal_rates=removal_configs.get(entity_id),
    )
