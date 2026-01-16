"""River/Water Body Stub Model.

Simulates river segments with mixing of upstream flow and
discharge flows from wastewater treatment plants and industries.
"""

import random
import math
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ..base import BaseWaterModel


# Pydantic models for request/response validation
class RiverSimulationInput(BaseModel):
    """Input parameters for river simulation."""

    upstream_flow: float = Field(..., description="Upstream flow rate (m³/d)")
    upstream_quality: float = Field(..., description="Upstream water quality index (0-1)")
    discharge_flows: List[float] = Field(..., description="List of discharge flow rates (m³/d)")
    discharge_qualities: List[float] = Field(..., description="List of discharge quality indices (0-1)")


class RiverSimulationOutput(BaseModel):
    """Output parameters from river simulation."""

    downstream_flow: float = Field(..., description="Downstream flow rate (m³/d)")
    downstream_quality: float = Field(..., description="Downstream water quality index (0-1)")
    flow_contribution_upstream: float = Field(..., description="Upstream flow contribution (%)")
    flow_contribution_total_discharge: float = Field(..., description="Total discharge flow contribution (%)")
    mixing_efficiency: float = Field(..., description="Mixing efficiency (%)")
    quality_change: float = Field(..., description="Change in quality from upstream to downstream")


class RiverStub(BaseWaterModel):
    """Stub implementation for River/Water Body model.

    Simulates flow and quality mixing in river segments.
    Uses flow-weighted averaging for quality parameters.
    """

    def __init__(
        self,
        entity_id: str = "River",
        entity_name: str = "Lieve River",
        port: int = 8010,
        river_length: float = 10.0,
        flow_rate: float = 5.0,
        **kwargs,
    ):
        """Initialize River stub.

        Args:
            entity_id: Entity identifier
            entity_name: Human-readable name
            port: Service port
            river_length: River length (km)
            flow_rate: Base flow rate (m³/s)
            **kwargs: Additional base class arguments
        """
        self.river_length = river_length
        self.base_flow_rate = flow_rate

        # Define capabilities
        capabilities = ["SteadyStateSimulation", "MassBalance"]

        # Define input parameters
        inputs = [
            {"name": "upstream_flow", "unit": "m³/d", "datatype": "float"},
            {"name": "upstream_quality", "unit": "-", "datatype": "float"},
            {"name": "discharge_flows", "unit": "m³/d", "datatype": "list[float]"},
            {"name": "discharge_qualities", "unit": "-", "datatype": "list[float]"},
        ]

        # Define output parameters
        outputs = [
            {"name": "downstream_flow", "unit": "m³/d", "datatype": "float"},
            {"name": "downstream_quality", "unit": "-", "datatype": "float"},
            {"name": "flow_contribution_upstream", "unit": "%", "datatype": "float"},
            {"name": "flow_contribution_total_discharge", "unit": "%", "datatype": "float"},
            {"name": "mixing_efficiency", "unit": "%", "datatype": "float"},
            {"name": "quality_change", "unit": "-", "datatype": "float"},
        ]

        metadata = {
            "river_length": river_length,
            "receives_from": ["WWTP1", "WWTP2"],
            "discharges_to": "River_mouth",
        }

        super().__init__(
            entity_id=entity_id,
            entity_name=entity_name,
            entity_type="RiverSegment",
            port=port,
            capabilities=capabilities,
            inputs=inputs,
            outputs=outputs,
            metadata=metadata,
        )

        # Create FastAPI app for this model
        self.app = FastAPI(
            title=f"{entity_name} Model",
            description="Stub river segment model with waterFRAME ontology self-description",
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
        async def simulate(inputs: RiverSimulationInput):
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
                    "wf:riverLength": self.river_length,
                    "wf:baseFlowRate": self.base_flow_rate,
                }
            ],
        }

    async def simulate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run river mixing simulation.

        Calculates flow-weighted quality mixing of upstream and discharge flows.
        """
        # Extract input values
        upstream_flow = self._get_parameter_value(inputs, "upstream_flow", 200000.0)
        upstream_quality = self._get_parameter_value(inputs, "upstream_quality", 0.8)

        # Handle discharge flows and qualities
        discharge_flows = inputs.get("discharge_flows", [50000, 30000])
        discharge_qualities = inputs.get("discharge_qualities", [0.6, 0.7])

        # Ensure lists are the same length
        if len(discharge_flows) != len(discharge_qualities):
            min_len = min(len(discharge_flows), len(discharge_qualities))
            discharge_flows = discharge_flows[:min_len]
            discharge_qualities = discharge_qualities[:min_len]

        # Calculate total discharge
        total_discharge_flow = sum(discharge_flows)

        # Flow-weighted quality mixing
        # Quality = (upstream_flow * upstream_quality + sum(discharge_flow_i * discharge_quality_i)) / total_flow
        total_quality_mass = (upstream_flow * upstream_quality) + sum(
            f * q for f, q in zip(discharge_flows, discharge_qualities)
        )
        total_flow = upstream_flow + total_discharge_flow

        downstream_quality = total_quality_mass / total_flow if total_flow > 0 else 0

        # Calculate flow contributions
        upstream_contribution = (upstream_flow / total_flow * 100) if total_flow > 0 else 0
        discharge_contribution = (total_discharge_flow / total_flow * 100) if total_flow > 0 else 0

        # Mixing efficiency (based on flow ratio - smaller discharge relative to river = poorer mixing)
        flow_ratio = upstream_flow / total_discharge_flow if total_discharge_flow > 0 else float('inf')
        if flow_ratio > 10:
            mixing_efficiency = 95 + random.uniform(-2, 2)
        elif flow_ratio > 5:
            mixing_efficiency = 90 + random.uniform(-3, 3)
        elif flow_ratio > 2:
            mixing_efficiency = 85 + random.uniform(-5, 5)
        else:
            mixing_efficiency = 75 + random.uniform(-10, 10)

        # Quality change (negative = degradation, positive = improvement)
        quality_change = downstream_quality - upstream_quality

        result = {
            "downstream_flow": round(total_flow, 2),
            "downstream_quality": round(downstream_quality, 4),
            "flow_contribution_upstream": round(upstream_contribution, 2),
            "flow_contribution_total_discharge": round(discharge_contribution, 2),
            "mixing_efficiency": round(mixing_efficiency, 2),
            "quality_change": round(quality_change, 4),
        }

        self._update_state(result)
        return result

    async def get_state(self) -> Dict[str, Any]:
        """Return current model state."""
        return self._state


def create_river_model(entity_id: str = "River", port: int = 8010) -> RiverStub:
    """Factory function to create a River model.

    Args:
        entity_id: Entity identifier
        port: Service port

    Returns:
        Configured RiverStub instance
    """
    return RiverStub(
        entity_id=entity_id,
        entity_name="Lieve River",
        port=port,
        river_length=10.0,
        flow_rate=5.0,
    )
