"""Residential District Stub Model.

Simulates domestic water use and wastewater generation for residential areas.
Uses per-capita water use rates (default: 150 L/person/day).
"""

import random
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ..base import BaseWaterModel


# Default per-capita water use
PER_CAPITA_WATER_USE = 150  # L/person/day


# Pydantic models for request/response validation
class ResidentialSimulationInput(BaseModel):
    """Input parameters for residential district simulation."""

    supply_water_flow: float = Field(..., description="Supply water flow rate (m³/d)")
    population: int = Field(..., description="Population served")


class ResidentialSimulationOutput(BaseModel):
    """Output parameters from residential district simulation."""

    wastewater_flow: float = Field(..., description="Wastewater flow rate (m³/d)")
    wastewater_BOD: float = Field(..., description="Wastewater BOD concentration (mg/L)")
    wastewater_COD: float = Field(..., description="Wastewater COD concentration (mg/L)")
    wastewater_TSS: float = Field(..., description="Wastewater TSS concentration (mg/L)")
    wastewater_TN: float = Field(..., description="Wastewater total nitrogen (mg/L)")
    wastewater_TP: float = Field(..., description="Wastewater total phosphorus (mg/L)")
    wastewater_coliforms: float = Field(..., description="Wastewater coliform count")
    per_capita_generation: float = Field(..., description="Per-capita wastewater generation (L/person/d)")


class ResidentialStub(BaseWaterModel):
    """Stub implementation for Residential District model.

    Simulates domestic water consumption and wastewater generation
    based on population and typical domestic wastewater characteristics.
    """

    def __init__(
        self,
        entity_id: str = "Dampoort",
        entity_name: str = "Dampoort Residential District",
        port: int = 8011,
        population: int = 15000,
        per_capita_use: float = PER_CAPITA_WATER_USE,
        **kwargs,
    ):
        """Initialize Residential stub.

        Args:
            entity_id: Entity identifier (Dampoort or Muide)
            entity_name: Human-readable name
            port: Service port
            population: Population served
            per_capita_use: Per-capita water use (L/person/day)
            **kwargs: Additional base class arguments
        """
        self.population = population
        self.per_capita_use = per_capita_use

        # Define capabilities
        capabilities = ["SteadyStateSimulation", "MassBalance"]

        # Define input parameters
        inputs = [
            {"name": "supply_water_flow", "unit": "m³/d", "datatype": "float"},
            {"name": "population", "unit": "persons", "datatype": "int"},
        ]

        # Define output parameters
        outputs = [
            {"name": "wastewater_flow", "unit": "m³/d", "datatype": "float"},
            {"name": "wastewater_BOD", "unit": "mg/L", "datatype": "float"},
            {"name": "wastewater_COD", "unit": "mg/L", "datatype": "float"},
            {"name": "wastewater_TSS", "unit": "mg/L", "datatype": "float"},
            {"name": "wastewater_TN", "unit": "mg/L", "datatype": "float"},
            {"name": "wastewater_TP", "unit": "mg/L", "datatype": "float"},
            {"name": "wastewater_coliforms", "unit": "CFU/100mL", "datatype": "float"},
            {"name": "per_capita_generation", "unit": "L/person/d", "datatype": "float"},
        ]

        metadata = {
            "population": population,
            "per_capita_water_use": per_capita_use,
            "discharges_to": "WWTP2" if entity_id == "Dampoort" else "WWTP1",
        }

        super().__init__(
            entity_id=entity_id,
            entity_name=entity_name,
            entity_type="ResidentialDistrict",
            port=port,
            capabilities=capabilities,
            inputs=inputs,
            outputs=outputs,
            metadata=metadata,
        )

        # Create FastAPI app for this model
        self.app = FastAPI(
            title=f"{entity_name} Model",
            description="Stub residential district model with waterFRAME ontology self-description",
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
        async def simulate(inputs: ResidentialSimulationInput):
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
                    "wf:population": self.population,
                    "wf:perCapitaWaterUse": self.per_capita_use,
                }
            ],
        }

    async def simulate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run residential water use simulation.

        Calculates wastewater generation and quality based on population.
        """
        # Extract input values
        supply_flow = self._get_parameter_value(inputs, "supply_water_flow", self.population * self.per_capita_use / 1000)
        population = self._get_parameter_value(inputs, "population", self.population)

        # Calculate per-capita generation (typically 80-90% of water use)
        per_capita_generation = self.per_capita_use * random.uniform(0.80, 0.90)

        # Wastewater flow
        wastewater_flow = population * per_capita_generation / 1000  # Convert to m³/d

        # Typical domestic wastewater characteristics (with variance)
        base_characteristics = {
            "BOD": 250,   # mg/L
            "COD": 450,   # mg/L
            "TSS": 200,   # mg/L
            "TN": 50,     # mg/L
            "TP": 6,      # mg/L
            "coliforms": 1000000,  # CFU/100mL
        }

        result = {
            "wastewater_flow": round(wastewater_flow, 2),
            "wastewater_BOD": round(base_characteristics["BOD"] * random.uniform(0.9, 1.1), 1),
            "wastewater_COD": round(base_characteristics["COD"] * random.uniform(0.9, 1.1), 1),
            "wastewater_TSS": round(base_characteristics["TSS"] * random.uniform(0.9, 1.1), 1),
            "wastewater_TN": round(base_characteristics["TN"] * random.uniform(0.9, 1.1), 1),
            "wastewater_TP": round(base_characteristics["TP"] * random.uniform(0.9, 1.1), 2),
            "wastewater_coliforms": round(base_characteristics["coliforms"] * random.uniform(0.5, 2.0), -1),
            "per_capita_generation": round(per_capita_generation, 1),
        }

        self._update_state(result)
        return result

    async def get_state(self) -> Dict[str, Any]:
        """Return current model state."""
        return self._state


def create_residential_model(
    entity_id: str = "Dampoort", port: int = 8011
) -> ResidentialStub:
    """Factory function to create a Residential model.

    Args:
        entity_id: Entity identifier (Dampoort or Muide)
        port: Service port

    Returns:
        Configured ResidentialStub instance
    """
    configs = {
        "Dampoort": {"population": 15000, "port": 8011},
        "Muide": {"population": 12000, "port": 8012},
    }

    config = configs.get(entity_id, {"population": 15000, "port": port})

    return ResidentialStub(
        entity_id=entity_id,
        entity_name=f"{entity_id} Residential District",
        port=config["port"],
        population=config["population"],
    )
