"""Model registry service for tracking registered models.

Adapted from ghent_water for reuse across case studies.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ModelInfo:
    """Information about a registered model."""

    def __init__(
        self,
        id: str,
        name: str,
        description: Optional[str] = None,
        endpoint: str = "",
        capabilities: Optional[List[str]] = None,
        entities: Optional[List[str]] = None,
        registered_at: Optional[datetime] = None,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.endpoint = endpoint
        self.capabilities = capabilities or []
        self.entities = entities or []
        self.registered_at = registered_at or datetime.utcnow()


class ModelRegistry:
    """Registry for tracking registered models and their capabilities."""

    def __init__(self):
        self._models: Dict[str, ModelInfo] = {}
        self._jobs: Dict[str, dict] = {}
        self._agent_ttl_cache: Dict[str, str] = {}

    def register_model(
        self,
        id: str,
        name: str,
        endpoint: str,
        capabilities: Optional[List[str]] = None,
        entities: Optional[List[str]] = None,
        description: Optional[str] = None,
    ) -> ModelInfo:
        """Register a new model or update existing one."""
        if id in self._models:
            logger.info(f"Updating existing model: {id}")
        else:
            logger.info(f"Registering new model: {id}")

        model = ModelInfo(
            id=id,
            name=name,
            description=description,
            endpoint=endpoint,
            capabilities=capabilities or [],
            entities=entities or [],
            registered_at=datetime.utcnow(),
        )
        self._models[id] = model
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

    def list_jobs(
        self, model_id: Optional[str] = None, status: Optional[str] = None
    ) -> List[dict]:
        """List jobs with optional filtering."""
        jobs = list(self._jobs.values())
        if model_id:
            jobs = [j for j in jobs if j.get("model_id") == model_id]
        if status:
            jobs = [j for j in jobs if j.get("status") == status]
        return jobs

    def update_job_status(
        self,
        job_id: str,
        status: str,
        results: Optional[Dict] = None,
        error: Optional[str] = None,
        progress: Optional[int] = None,
    ) -> Optional[dict]:
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

    def get_job_stats(self) -> dict:
        """Get statistics about jobs."""
        total = len(self._jobs)
        pending = sum(1 for j in self._jobs.values() if j.get("status") == "pending")
        running = sum(1 for j in self._jobs.values() if j.get("status") == "running")
        completed = sum(
            1 for j in self._jobs.values() if j.get("status") == "completed"
        )
        failed = sum(1 for j in self._jobs.values() if j.get("status") == "failed")

        return {
            "total": total,
            "pending": pending,
            "running": running,
            "completed": completed,
            "failed": failed,
        }


registry = ModelRegistry()
