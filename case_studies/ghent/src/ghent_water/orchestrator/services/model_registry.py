"""Model registry service for tracking registered models."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from ..schemas.models import ModelInfo, ModelRegistrationRequest

logger = logging.getLogger(__name__)


class ModelRegistry:
    """Registry for tracking registered models and their capabilities."""

    def __init__(self):
        self._models: Dict[str, ModelInfo] = {}
        self._jobs: Dict[str, dict] = {}
        self._agent_ttl_cache: Dict[str, str] = {}  # Store agent TTL for each model
    
    def register_model(self, request: ModelRegistrationRequest) -> ModelInfo:
        """Register a new model or update existing one."""
        if request.id in self._models:
            logger.info(f"Updating existing model: {request.id}")
        else:
            logger.info(f"Registering new model: {request.id}")
        
        model = ModelInfo(
            id=request.id,
            name=request.name,
            description=request.description,
            endpoint=request.endpoint,
            capabilities=request.capabilities,
            entities=request.entities,
            registered_at=datetime.utcnow()
        )
        self._models[request.id] = model
        return model
    
    def unregister_model(self, model_id: str) -> bool:
        """Unregister a model."""
        if model_id in self._models:
            del self._models[model_id]
            logger.info(f"Unregistered model: {model_id}")
            return True
        return False
    
    def get_model(self, model_id: str) -> Optional[ModelInfo]:
        """Get a model by ID."""
        return self._models.get(model_id)
    
    def list_models(self) -> List[ModelInfo]:
        """List all registered models."""
        return list(self._models.values())
    
    def find_models_by_capability(self, capability: str) -> List[ModelInfo]:
        """Find models that have a specific capability."""
        return [m for m in self._models.values() if capability in m.capabilities]
    
    def find_models_by_entity(self, entity_uri: str) -> List[ModelInfo]:
        """Find models that handle a specific entity."""
        return [m for m in self._models.values() if entity_uri in m.entities]
    
    def create_job(self, model_id: str, parameters: Dict[str, Any]) -> str:
        """Create a new simulation job with timestamp and initial state."""
        import uuid
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = {
            "job_id": job_id,
            "model_id": model_id,
            "status": "pending",
            "progress": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "parameters": parameters,
            "results": None,
            "error": None,
        }
        logger.info(f"Created job {job_id} for model {model_id}")
        return job_id
    
    def get_job(self, job_id: str) -> Optional[dict]:
        """Get a job by ID."""
        return self._jobs.get(job_id)
    
    def list_jobs(self, model_id: Optional[str] = None, status: Optional[str] = None) -> List[dict]:
        """List jobs with optional filtering.
        
        Args:
            model_id: Optional model ID to filter by.
            status: Optional status to filter by.
            
        Returns:
            List of matching jobs.
        """
        jobs = list(self._jobs.values())
        if model_id:
            jobs = [j for j in jobs if j.get("model_id") == model_id]
        if status:
            jobs = [j for j in jobs if j.get("status") == status]
        return jobs
    
    def update_job_status(self, job_id: str, status: str, 
                          results: Optional[Dict] = None, 
                          error: Optional[str] = None,
                          progress: Optional[int] = None) -> Optional[dict]:
        """Update job status with progress tracking."""
        if job_id in self._jobs:
            self._jobs[job_id]["status"] = status
            self._jobs[job_id]["updated_at"] = datetime.utcnow()
            if progress is not None:
                self._jobs[job_id]["progress"] = progress
            if status == "running":
                self._jobs[job_id]["started_at"] = datetime.utcnow()
            elif status in ("completed", "failed"):
                self._jobs[job_id]["completed_at"] = datetime.utcnow()
            if results is not None:
                self._jobs[job_id]["results"] = results
            if error is not None:
                self._jobs[job_id]["error"] = error
            return self._jobs[job_id]
        return None
    
    def register_agent_ttl(self, model_id: str, agent_ttl: str) -> bool:
        """Register agent-aware TTL for a model and add to ontology store.

        Args:
            model_id: Model identifier.
            agent_ttl: Agent TTL string.

        Returns:
            True if successful, False otherwise.
        """
        try:
            # Store in cache
            self._agent_ttl_cache[model_id] = agent_ttl

            # Add to ontology store
            from .ontology_store import ontology_store

            if ontology_store.is_loaded():
                triples_added = ontology_store.add_triples(agent_ttl, format="turtle")
                logger.info(
                    f"Added {triples_added} agent triples for model {model_id} to ontology store"
                )
            else:
                logger.warning(
                    "Ontology not loaded, agent TTL cached but not added to store"
                )

            return True
        except Exception as e:
            logger.error(f"Failed to register agent TTL for {model_id}: {e}")
            return False

    def get_agent_ttl(self, model_id: str) -> Optional[str]:
        """Get cached agent TTL for a model.

        Args:
            model_id: Model identifier.

        Returns:
            Agent TTL string or None if not found.
        """
        return self._agent_ttl_cache.get(model_id)

    def find_agents_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        """Find computational agents with a specific capability using SPARQL.

        Args:
            capability: Capability name (e.g., "DynamicSimulation").

        Returns:
            List of agent dictionaries with IRI, label, and model info.
        """
        from .ontology_store import ontology_store

        if not ontology_store.is_loaded():
            logger.warning("Ontology not loaded, returning empty result")
            return []

        query = f"""
        PREFIX wf: <https://w3id.org/waterframe/>
        PREFIX cap: <https://w3id.org/waterframe/capability/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?agent ?label ?model ?software ?endpoint WHERE {{
            ?agent a wf:ComputationalAgent ;
                   wf:hasCapability cap:{capability} ;
                   wf:implements ?model ;
                   wf:runsOn ?software .
            OPTIONAL {{ ?agent rdfs:label ?label }}
            OPTIONAL {{ ?software wf:apiEndpoint ?endpoint }}
        }}
        """

        try:
            results = ontology_store.query_sparql(query)
            agents = []
            for binding in results.get("results", {}).get("bindings", []):
                agents.append(
                    {
                        "agent_uri": binding.get("agent", {}).get("value"),
                        "label": binding.get("label", {}).get("value"),
                        "model_uri": binding.get("model", {}).get("value"),
                        "software_uri": binding.get("software", {}).get("value"),
                        "endpoint": binding.get("endpoint", {}).get("value"),
                    }
                )
            return agents
        except Exception as e:
            logger.error(f"SPARQL query failed: {e}")
            return []

    def find_operations_by_input(self, input_name: str) -> List[Dict[str, Any]]:
        """Find operations that require a specific input using SPARQL.

        Args:
            input_name: Input parameter name.

        Returns:
            List of operation dictionaries.
        """
        from .ontology_store import ontology_store

        if not ontology_store.is_loaded():
            logger.warning("Ontology not loaded, returning empty result")
            return []

        query = f"""
        PREFIX wf: <https://w3id.org/waterframe/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?operation ?label ?agent ?input WHERE {{
            ?operation a wf:Operation ;
                       wf:requiresInput ?input .
            ?input wf:parameterName "{input_name}" .
            ?agent wf:offersOperation ?operation .
            OPTIONAL {{ ?operation rdfs:label ?label }}
        }}
        """

        try:
            results = ontology_store.query_sparql(query)
            operations = []
            for binding in results.get("results", {}).get("bindings", []):
                operations.append(
                    {
                        "operation_uri": binding.get("operation", {}).get("value"),
                        "label": binding.get("label", {}).get("value"),
                        "agent_uri": binding.get("agent", {}).get("value"),
                        "input_uri": binding.get("input", {}).get("value"),
                    }
                )
            return operations
        except Exception as e:
            logger.error(f"SPARQL query failed: {e}")
            return []

    def get_operation_chain(
        self, start_data: List[str], target_data: str
    ) -> List[Dict[str, Any]]:
        """Find operation sequences that transform start data into target data.

        Uses SPARQL with dataFlowsTo property chain inference.

        Args:
            start_data: List of starting input parameter names.
            target_data: Target output parameter name.

        Returns:
            List of operation chain dictionaries.
        """
        from .ontology_store import ontology_store

        if not ontology_store.is_loaded():
            logger.warning("Ontology not loaded, returning empty result")
            return []

        # Build VALUES clause for start data
        start_values = " ".join(f'"{d}"' for d in start_data)

        query = f"""
        PREFIX wf: <https://w3id.org/waterframe/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?op1 ?op2 ?intermediate WHERE {{
            VALUES ?startParam {{ {start_values} }}

            # Op1 requires starting data, produces intermediate
            ?op1 wf:requiresInput ?input1 ;
                 wf:producesOutput ?intermediate .
            ?input1 wf:parameterName ?startParam .

            # Op2 requires intermediate, produces target
            ?op2 wf:requiresInput ?intermediate ;
                 wf:producesOutput ?output2 .
            ?output2 wf:parameterName "{target_data}" .

            # Verify data flow relationship
            ?op1 wf:dataFlowsTo ?op2 .
        }}
        LIMIT 10
        """

        try:
            results = ontology_store.query_sparql(query)
            chains = []
            for binding in results.get("results", {}).get("bindings", []):
                chains.append(
                    {
                        "first_operation": binding.get("op1", {}).get("value"),
                        "second_operation": binding.get("op2", {}).get("value"),
                        "intermediate_data": binding.get("intermediate", {}).get(
                            "value"
                        ),
                    }
                )
            return chains
        except Exception as e:
            logger.error(f"SPARQL query failed: {e}")
            return []

    def get_job_stats(self) -> dict:
        """Get statistics about jobs."""
        total = len(self._jobs)
        pending = sum(1 for j in self._jobs.values() if j.get("status") == "pending")
        running = sum(1 for j in self._jobs.values() if j.get("status") == "running")
        completed = sum(1 for j in self._jobs.values() if j.get("status") == "completed")
        failed = sum(1 for j in self._jobs.values() if j.get("status") == "failed")

        return {
            "total": total,
            "pending": pending,
            "running": running,
            "completed": completed,
            "failed": failed,
        }


# Global registry instance
registry = ModelRegistry()
