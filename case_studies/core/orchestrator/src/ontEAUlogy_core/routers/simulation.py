"""Simulation router for model simulation endpoints."""

import asyncio
import logging
from collections import OrderedDict
from datetime import datetime
from typing import Any, Dict, Optional

import httpx
from fastapi import APIRouter, HTTPException

from ..schemas.models import SimulationRequest, JobResponse
from ..services.model_registry import registry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/simulation", tags=["Simulation"])

# MODEL_PORTS is now handled through the model registry
# No hardcoded ports - models are discovered from configuration

# Track running background tasks with metadata (using OrderedDict for LRU-style cleanup)
_running_tasks: OrderedDict[str, Dict[str, Any]] = OrderedDict()
_task_lock = asyncio.Lock()
MAX_CONCURRENT_TASKS = 50

# Shared HTTP client with connection pooling
_http_client: Optional[httpx.AsyncClient] = None
_client_lock = asyncio.Lock()


async def get_http_client() -> httpx.AsyncClient:
    """Get or create shared HTTP client with connection pooling."""
    global _http_client
    async with _client_lock:
        if _http_client is None:
            limits = httpx.Limits(
                max_keepalive_connections=20, max_connections=50, keepalive_expiry=30.0
            )
            _http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(5.0, read=300.0),  # 5s connect, 300s read
                limits=limits,
            )
        return _http_client


async def cleanup_stale_tasks():
    """Remove completed or cancelled tasks from the tracking dictionary."""
    async with _task_lock:
        to_remove = []
        for job_id, task_info in _running_tasks.items():
            task = task_info["task"]
            if task.done():
                try:
                    await task  # Retrieve any exceptions
                except Exception as e:
                    logger.error(f"Task {job_id} failed with: {e}")
                to_remove.append(job_id)

        for job_id in to_remove:
            del _running_tasks[job_id]
            logger.debug(f"Cleaned up completed task {job_id}")


# Model discovery is now handled in main.py during application startup
# This router uses the registry which is populated from configuration


@router.get("/models")
async def list_models():
    """List all registered models.

    Returns:
        List of model information dictionaries.
    """
    models = registry.list_models()
    return {
        "models": [
            {
                "id": m.id,
                "name": m.name,
                "description": m.description,
                "endpoint": m.endpoint,
                "capabilities": m.capabilities,
            }
            for m in models
        ],
        "count": len(models),
    }


async def try_register_model(model_id: str, endpoint: str) -> bool:
    """Try to discover and register a model on-demand.

    Args:
        model_id: The model ID to register.
        endpoint: The HTTP endpoint of the model service.

    Returns:
        True if registration succeeded, False otherwise.
    """
    # Check if already registered
    if registry.get_model(model_id):
        return True

    try:
        client = await get_http_client()
        resp = await client.get(f"{endpoint}/describe")
        if resp.status_code == 200:
            description = resp.json()
            graph = description.get("@graph", [{}])
            model_info = graph[0] if graph else {}

            from ..schemas.models import ModelRegistrationRequest

            registry.register_model(
                ModelRegistrationRequest(
                    id=model_id,
                    name=model_info.get("rdfs:label", model_id.upper()),
                    description=model_info.get("rdfs:comment", ""),
                    endpoint=endpoint,
                    capabilities=["SteadyStateSimulation", "MassBalance"],
                    entities=[f"case:{model_id.upper()}"],
                )
            )
            logger.info(f"On-demand registered model: {model_id} at {endpoint}")
            return True
        else:
            logger.warning(f"Model {model_id} returned status {resp.status_code}")
            return False
    except httpx.ConnectError:
        logger.warning(f"Could not connect to model {model_id} at {endpoint}")
        return False
    except Exception as e:
        logger.error(f"Error registering model {model_id}: {e}")
        return False


async def execute_simulation(
    job_id: str, model_id: str, model_endpoint: str, parameters: Dict[str, Any]
) -> None:
    """Background task to execute a simulation by calling the model's endpoint.

    Args:
        job_id: The job ID to update.
        model_id: The model being simulated.
        model_endpoint: The HTTP endpoint of the model service.
        parameters: Simulation parameters to pass to the model.
    """
    try:
        logger.info(f"Starting simulation for job {job_id} on model {model_id}")
        registry.update_job_status(job_id, "running")

        # Use shared client with connection pooling
        client = await get_http_client()
        response = await client.post(
            f"{model_endpoint}/simulate", json=parameters.get("parameters", {})
        )
        response.raise_for_status()
        results = response.json()

        logger.info(f"Simulation completed for job {job_id}")
        registry.update_job_status(job_id, "completed", results=results)

    except httpx.HTTPStatusError as e:
        error_msg = f"Model returned error: {e.response.status_code}"
        logger.error(f"Simulation failed for job {job_id}: {error_msg}")
        registry.update_job_status(job_id, "failed", error=error_msg)

    except httpx.ConnectError:
        error_msg = f"Could not connect to model at {model_endpoint}"
        logger.error(f"Simulation failed for job {job_id}: {error_msg}")
        registry.update_job_status(job_id, "failed", error=error_msg)

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Simulation failed for job {job_id}: {error_msg}")
        registry.update_job_status(job_id, "failed", error=error_msg)

    finally:
        async with _task_lock:
            _running_tasks.pop(job_id, None)


@router.post("/models/{model_id}/run", response_model=JobResponse)
async def run_simulation(model_id: str, request: SimulationRequest):
    """Run a simulation for a specific model.

    Args:
        model_id: ID of the model to run.
        request: Simulation request with inputs and parameters.

    Returns:
        Job response with job ID.
    """
    # Cleanup before checking limit
    await cleanup_stale_tasks()

    # Check concurrent task limit
    async with _task_lock:
        if len(_running_tasks) >= MAX_CONCURRENT_TASKS:
            raise HTTPException(
                status_code=503,
                detail=f"Too many concurrent simulations ({MAX_CONCURRENT_TASKS} max). Please try again later.",
            )

    model = registry.get_model(model_id)

    if not model:
        raise HTTPException(
            status_code=404,
            detail=f"Model {model_id} not found. Ensure the model service is running and registered.",
        )

    # Create job
    job_id = registry.create_job(model_id, request.model_dump())

    # Start background task with tracking metadata
    task = asyncio.create_task(
        execute_simulation(job_id, model_id, model.endpoint, request.model_dump())
    )

    async with _task_lock:
        _running_tasks[job_id] = {
            "task": task,
            "created_at": datetime.utcnow(),
            "model_id": model_id,
        }

    return JobResponse(
        job_id=job_id,
        model_id=model_id,
        status="pending",
        message=f"Simulation started for model {model_id}",
    )


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get the status of a simulation job.

    Args:
        job_id: ID of the job.

    Returns:
        Job details.
    """
    job = registry.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return job


@router.get("/models/{model_id}/state")
async def get_model_state(model_id: str):
    """Get the current state of a model.

    Args:
        model_id: ID of the model.

    Returns:
        Model state.
    """
    model = registry.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")

    # In a real system, this would call the model's /state endpoint
    return {
        "model_id": model_id,
        "status": "idle",
        "last_run": None,
        "message": "Model is ready for simulation",
    }


@router.post("/models/{model_id}/register")
async def register_model_with_orchestrator(model_id: str, description: Dict[str, Any]):
    """Register a model with the orchestrator.

    Args:
        model_id: ID of the model.
        description: Model self-description.

    Returns:
        Registration result.
    """
    from ..schemas.models import ModelRegistrationRequest

    # Extract model info from description
    request = ModelRegistrationRequest(
        id=model_id,
        name=description.get("name", model_id),
        description=description.get("description", ""),
        endpoint=description.get("endpoint", f"http://localhost:8000"),
        capabilities=description.get("capabilities", []),
        entities=description.get("entities", []),
    )

    model_info = registry.register_model(request)
    return {
        "status": "registered",
        "model_id": model_info.id,
        "name": model_info.name,
        "capabilities": model_info.capabilities,
    }


@router.on_event("shutdown")
async def cleanup_http_client():
    """Close shared HTTP client on shutdown."""
    global _http_client
    if _http_client:
        await _http_client.aclose()
        _http_client = None
        logger.info("Closed shared HTTP client")
