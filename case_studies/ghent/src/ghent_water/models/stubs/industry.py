"""Industry Stub Model.

Generic configurable stub for industrial water users and wastewater producers.
Supports various industry types: textile, food processing, electronics, pharmaceutical, brewery.
"""

import random
from typing import Any, Dict, List, Optional
import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ..base import BaseWaterModel


# Industry-specific configurations
INDUSTRY_CONFIGS = {
    "Texfin": {
        "industry_type": "textile",
        "water_demand": 2000,
        "wastewater_characteristics": {
            "COD": (800, 200),  # mean, std
            "TSS": (150, 50),
            "color": (200, 100),
            "pH": (8, 1),
        },
        "water_reuse_rate": 0.1,
        "discharges_to": "WWTP2",
    },
    "FoodPro": {
        "industry_type": "food_processing",
        "water_demand": 1500,
        "wastewater_characteristics": {
            "COD": (1500, 300),
            "BOD": (800, 200),
            "TSS": (300, 100),
            "fat": (80, 30),
        },
        "water_reuse_rate": 0.15,
        "discharges_to": "WWTP2",
    },
    "ChipTech": {
        "industry_type": "electronics",
        "water_demand": 800,
        "wastewater_characteristics": {
            "COD": (50, 20),
            "TSS": (20, 10),
            "metals": (1, 0.5),
            "pH": (6, 1),
        },
        "water_reuse_rate": 0.1,
        "discharges_to": "WWTP1",
    },
    "PharmaGen": {
        "industry_type": "pharmaceutical",
        "water_demand": 600,
        "wastewater_characteristics": {
            "COD": (400, 100),
            "BOD": (200, 50),
            "TSS": (50, 20),
            "pH": (7, 1),
            "residuals": (10, 5),
        },
        "water_reuse_rate": 0.1,
        "discharges_to": "WWTP1",
    },
    "BrewCo": {
        "industry_type": "brewery",
        "water_demand": 1000,
        "wastewater_characteristics": {
            "COD": (1200, 300),
            "BOD": (600, 150),
            "TSS": (150, 50),
            "pH": (6, 1),
        },
        "water_reuse_rate": 0.2,
        "discharges_to": "WWTP1",
    },
}


# Pydantic models for request/response validation
class IndustrySimulationInput(BaseModel):
    """Input parameters for industry simulation."""

    supply_water_flow: float = Field(..., description="Supply water flow rate (m³/d)")
    supply_water_quality: float = Field(..., description="Supply water quality index (0-1)")
    production_rate: Optional[float] = Field(None, description="Production rate (industry specific)")


class IndustrySimulationOutput(BaseModel):
    """Output parameters from industry simulation."""

    wastewater_flow: float = Field(..., description="Wastewater flow rate (m³/d)")
    wastewater_COD: float = Field(..., description="Wastewater COD concentration (mg/L)")
    wastewater_BOD: float = Field(..., description="Wastewater BOD concentration (mg/L)")
    wastewater_TSS: float = Field(..., description="Wastewater TSS concentration (mg/L)")
    wastewater_pH: float = Field(..., description="Wastewater pH")
    wastewater_metals: float = Field(..., description="Wastewater metals concentration (mg/L)")
    wastewater_color: float = Field(..., description="Wastewater color (Pt-Co)")
    wastewater_fat: float = Field(..., description="Wastewater fat concentration (mg/L)")
    wastewater_residuals: float = Field(..., description="Wastewater residuals (mg/L)")
    energy_consumption: float = Field(..., description="Energy consumption (kWh/d)")
    water_reuse_rate: float = Field(..., description="Water reuse rate (%)")


class IndustryStub(BaseWaterModel):
    """Stub implementation for Industry model.

    Generic configurable model for various industrial water users.
    """

    def __init__(
        self,
        entity_id: str = "Texfin",
        entity_name: str = "Texfin Textile Industry",
        port: int = 8005,
        industry_config: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """Initialize Industry stub.

        Args:
            entity_id: Entity identifier (Texfin, FoodPro, ChipTech, PharmaGen, BrewCo)
            entity_name: Human-readable name
            port: Service port
            industry_config: Custom industry configuration
            **kwargs: Additional base class arguments
        """
        # Use provided config or load from defaults
        self.industry_config = industry_config or INDUSTRY_CONFIGS.get(entity_id, {
            "industry_type": "generic",
            "water_demand": 1000,
            "wastewater_characteristics": {"COD": (200, 50)},
            "water_reuse_rate": 0.1,
            "discharges_to": "WWTP1",
        })

        # Define capabilities
        capabilities = ["SteadyStateSimulation", "MassBalance"]

        # Define input parameters
        inputs = [
            {"name": "supply_water_flow", "unit": "m³/d", "datatype": "float"},
            {"name": "supply_water_quality", "unit": "-", "datatype": "float"},
            {"name": "production_rate", "unit": "varies", "datatype": "float"},
        ]

        # Define output parameters based on industry type
        industry_type = self.industry_config.get("industry_type", "generic")
        outputs = [
            {"name": "wastewater_flow", "unit": "m³/d", "datatype": "float"},
            {"name": "wastewater_COD", "unit": "mg/L", "datatype": "float"},
            {"name": "energy_consumption", "unit": "kWh/d", "datatype": "float"},
            {"name": "water_reuse_rate", "unit": "%", "datatype": "float"},
        ]

        # Add industry-specific outputs
        if industry_type in ["textile"]:
            outputs.extend([
                {"name": "wastewater_TSS", "unit": "mg/L", "datatype": "float"},
                {"name": "wastewater_color", "unit": "Pt-Co", "datatype": "float"},
                {"name": "wastewater_pH", "unit": "-", "datatype": "float"},
            ])
        elif industry_type in ["food_processing", "brewery"]:
            outputs.extend([
                {"name": "wastewater_BOD", "unit": "mg/L", "datatype": "float"},
                {"name": "wastewater_TSS", "unit": "mg/L", "datatype": "float"},
                {"name": "wastewater_fat", "unit": "mg/L", "datatype": "float"},
                {"name": "wastewater_pH", "unit": "-", "datatype": "float"},
            ])
        elif industry_type == "electronics":
            outputs.extend([
                {"name": "wastewater_TSS", "unit": "mg/L", "datatype": "float"},
                {"name": "wastewater_metals", "unit": "mg/L", "datatype": "float"},
                {"name": "wastewater_pH", "unit": "-", "datatype": "float"},
            ])
        elif industry_type == "pharmaceutical":
            outputs.extend([
                {"name": "wastewater_BOD", "unit": "mg/L", "datatype": "float"},
                {"name": "wastewater_TSS", "unit": "mg/L", "datatype": "float"},
                {"name": "wastewater_pH", "unit": "-", "datatype": "float"},
                {"name": "wastewater_residuals", "unit": "mg/L", "datatype": "float"},
            ])

        metadata = {
            "industry_type": industry_type,
            "discharges_to": self.industry_config.get("discharges_to", "WWTP1"),
            "water_reuse_rate": self.industry_config.get("water_reuse_rate", 0.1),
        }

        super().__init__(
            entity_id=entity_id,
            entity_name=entity_name,
            entity_type="Industry",
            port=port,
            capabilities=capabilities,
            inputs=inputs,
            outputs=outputs,
            metadata=metadata,
        )

        # Create FastAPI app for this model
        self.app = FastAPI(
            title=f"{entity_name} Model",
            description=f"Stub {industry_type} industry model with waterFRAME ontology self-description",
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
        async def simulate(inputs: IndustrySimulationInput):
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
                    "wf:industryType": self.industry_config.get("industry_type", "generic"),
                }
            ],
        }

    async def simulate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run industry water use simulation.

        Calculates wastewater generation and quality based on water use.
        """
        # Extract input values
        supply_flow = self._get_parameter_value(inputs, "supply_water_flow", 1000.0)
        supply_quality = self._get_parameter_value(inputs, "supply_water_quality", 1.0)

        # Water reuse reduces effective wastewater
        reuse_rate = self.industry_config.get("water_reuse_rate", 0.1)
        wastewater_flow = supply_flow * (1 - reuse_rate)

        # Generate wastewater characteristics
        waste_chars = self.industry_config.get("wastewater_characteristics", {})
        industry_type = self.industry_config.get("industry_type", "generic")

        result = {
            "wastewater_flow": round(wastewater_flow, 2),
            "wastewater_COD": self._generate_characteristic(waste_chars, "COD", supply_quality),
            "energy_consumption": round(supply_flow * 0.25, 1),
            "water_reuse_rate": round(reuse_rate * 100, 1),
        }

        # Add industry-specific outputs
        if industry_type in ["textile"]:
            result.update({
                "wastewater_TSS": self._generate_characteristic(waste_chars, "TSS", supply_quality),
                "wastewater_color": self._generate_characteristic(waste_chars, "color", supply_quality),
                "wastewater_pH": self._generate_characteristic(waste_chars, "pH", supply_quality),
            })
        elif industry_type in ["food_processing", "brewery"]:
            result.update({
                "wastewater_BOD": self._generate_characteristic(waste_chars, "BOD", supply_quality),
                "wastewater_TSS": self._generate_characteristic(waste_chars, "TSS", supply_quality),
                "wastewater_fat": self._generate_characteristic(waste_chars, "fat", supply_quality),
                "wastewater_pH": self._generate_characteristic(waste_chars, "pH", supply_quality),
            })
        elif industry_type == "electronics":
            result.update({
                "wastewater_TSS": self._generate_characteristic(waste_chars, "TSS", supply_quality),
                "wastewater_metals": self._generate_characteristic(waste_chars, "metals", supply_quality),
                "wastewater_pH": self._generate_characteristic(waste_chars, "pH", supply_quality),
            })
        elif industry_type == "pharmaceutical":
            result.update({
                "wastewater_BOD": self._generate_characteristic(waste_chars, "BOD", supply_quality),
                "wastewater_TSS": self._generate_characteristic(waste_chars, "TSS", supply_quality),
                "wastewater_pH": self._generate_characteristic(waste_chars, "pH", supply_quality),
                "wastewater_residuals": self._generate_characteristic(waste_chars, "residuals", supply_quality),
            })

        self._update_state(result)
        return result

    def _generate_characteristic(
        self, waste_chars: Dict, param: str, supply_quality: float
    ) -> float:
        """Generate a wastewater characteristic value.

        Args:
            waste_chars: Dictionary of waste characteristics
            param: Parameter name
            supply_quality: Supply water quality (affects dilution)

        Returns:
            Generated value for the parameter
        """
        if param not in waste_chars:
            return 0.0

        mean, std = waste_chars[param]
        value = random.gauss(mean, std)

        # Apply supply quality effect (better quality = lower pollution)
        quality_factor = 1.0 - (1.0 - supply_quality) * 0.2
        value = value * quality_factor

        return round(max(0, value), 2)

    async def get_state(self) -> Dict[str, Any]:
        """Return current model state."""
        return self._state


def create_industry_model(
    entity_id: str = "Texfin", port: int = 8005
) -> IndustryStub:
    """Factory function to create an Industry model.

    Args:
        entity_id: Entity identifier (Texfin, FoodPro, ChipTech, PharmaGen, BrewCo)
        port: Service port

    Returns:
        Configured IndustryStub instance
    """
    port_map = {
        "Texfin": 8005,
        "FoodPro": 8006,
        "ChipTech": 8007,
        "PharmaGen": 8008,
        "BrewCo": 8009,
    }

    return IndustryStub(
        entity_id=entity_id,
        entity_name=f"{entity_id} Industry",
        port=port or port_map.get(entity_id, 8005),
        industry_config=INDUSTRY_CONFIGS.get(entity_id),
    )
