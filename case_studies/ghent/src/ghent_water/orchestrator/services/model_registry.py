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
        """Create a new simulation job."""
        import uuid
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = {
            "job_id": job_id,
            "model_id": model_id,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "parameters": parameters,
            "results": None,
            "error": None
        }
        logger.info(f"Created job {job_id} for model {model_id}")
        return job_id
    
    def get_job(self, job_id: str) -> Optional[dict]:
        """Get a job by ID."""
        return self._jobs.get(job_id)
    
    def update_job_status(self, job_id: str, status: str, 
                          results: Optional[Dict] = None, 
                          error: Optional[str] = None) -> Optional[dict]:
        """Update job status."""
        if job_id in self._jobs:
            self._jobs[job_id]["status"] = status
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


# Global registry instance
registry = ModelRegistry()
