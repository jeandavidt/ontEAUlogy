"""HTTP client for communicating with the orchestrator API."""

import httpx
from typing import Any, Optional


class OrchestratorClient:
    """Async HTTP client for the ontEAUlogy orchestrator API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the client with the orchestrator base URL.
        
        Args:
            base_url: Base URL of the orchestrator API (default: http://localhost:8000)
        """
        self.base_url = base_url
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def get_models(self) -> list[dict]:
        """Get list of available models.
        
        Returns:
            List of model dictionaries with id, name, type, and description.
        """
        client = await self._get_client()
        response = await client.get(f"{self.base_url}/api/v1/models/")
        response.raise_for_status()
        return response.json()

    async def get_model_description(self, model_id: str) -> dict:
        """Get detailed description of a specific model.
        
        Args:
            model_id: The unique identifier of the model.
            
        Returns:
            Model description including inputs, outputs, and parameters.
        """
        client = await self._get_client()
        response = await client.get(f"{self.base_url}/api/v1/models/{model_id}/describe")
        response.raise_for_status()
        return response.json()

    async def run_sparql_query(self, query: str, format: str = "json") -> dict:
        """Execute a SPARQL query against the ontology.
        
        Args:
            query: SPARQL query string.
            format: Response format - "json", "table", or "json-ld".
            
        Returns:
            Query results in the specified format.
        """
        client = await self._get_client()
        response = await client.post(
            f"{self.base_url}/api/v1/query/sparql",
            json={"query": query, "format": format}
        )
        response.raise_for_status()
        return response.json()

    async def run_natural_query(self, question: str) -> dict:
        """Execute a natural language query.
        
        Args:
            question: Natural language question about the water system.
            
        Returns:
            Parsed answer with supporting data and provenance.
        """
        client = await self._get_client()
        response = await client.post(
            f"{self.base_url}/api/v1/query/natural",
            json={"question": question}
        )
        response.raise_for_status()
        return response.json()

    async def run_simulation(self, model_id: str, inputs: dict) -> dict:
        """Run a simulation for a specific model.
        
        Args:
            model_id: The unique identifier of the model to run.
            inputs: Dictionary of input parameters for the simulation.
            
        Returns:
            Job information including job_id and initial status.
        """
        client = await self._get_client()
        response = await client.post(
            f"{self.base_url}/api/v1/models/{model_id}/run",
            json=inputs
        )
        response.raise_for_status()
        return response.json()

    async def get_job_status(self, job_id: str) -> dict:
        """Get the status of a simulation job.
        
        Args:
            job_id: The unique identifier of the job.
            
        Returns:
            Job status including state, progress, and results when complete.
        """
        client = await self._get_client()
        response = await client.get(f"{self.base_url}/api/v1/jobs/{job_id}")
        response.raise_for_status()
        return response.json()

    async def get_ontology(self) -> str:
        """Get the ontology turtle content.
        
        Returns:
            Turtle-formatted ontology string.
        """
        client = await self._get_client()
        response = await client.get(f"{self.base_url}/api/v1/ontology/")
        response.raise_for_status()
        return response.text

    async def get_entities(self, entity_type: Optional[str] = None) -> list[dict]:
        """Get list of entities in the water system.
        
        Args:
            entity_type: Optional filter by entity type (e.g., "WWTP", "DWP").
            
        Returns:
            List of entity dictionaries with id, name, type, and coordinates.
        """
        client = await self._get_client()
        params = {"type": entity_type} if entity_type else {}
        response = await client.get(f"{self.base_url}/api/v1/entities/", params=params)
        response.raise_for_status()
        return response.json()

    async def get_entity_details(self, entity_id: str) -> dict:
        """Get detailed information about a specific entity.
        
        Args:
            entity_id: The unique identifier of the entity.
            
        Returns:
            Entity details including properties, inputs, and outputs.
        """
        client = await self._get_client()
        response = await client.get(f"{self.base_url}/api/v1/entities/{entity_id}")
        response.raise_for_status()
        return response.json()
