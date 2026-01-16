"""Discovery router for API and model discovery endpoints."""
import logging
from fastapi import APIRouter, HTTPException
from ..schemas.models import (
    SystemInfo, ModelListResponse, ModelInfo, ModelDescription,
    RegistrationResponse, ModelRegistrationRequest
)
from ..services.model_registry import registry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Discovery"])


@router.get("/", response_model=SystemInfo)
async def get_system_info():
    """Get system description in JSON-LD format."""
    return SystemInfo(
        name="ontEAUlogy Ghent Backend",
        version="0.1.0",
        description="FastAPI orchestrator for Ghent water system ontology management",
        endpoints={
            "discovery": "/api/v1/",
            "models": "/api/v1/models/",
            "sparql_query": "/api/v1/query/sparql",
            "natural_query": "/api/v1/query/natural",
            "ontology": "/api/v1/ontology/",
            "health": "/health"
        }
    )


@router.get("/models/", response_model=ModelListResponse)
async def list_models():
    """List all registered models."""
    models = registry.list_models()
    return ModelListResponse(models=models, count=len(models))


@router.get("/models/{model_id}/describe", response_model=ModelDescription)
async def describe_model(model_id: str):
    """Get model self-description."""
    model = registry.get_model(model_id)
    if model is None:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    return ModelDescription(
        model=model,
        inputs=[],
        outputs=[]
    )


@router.post("/register", response_model=RegistrationResponse)
async def register_model(request: ModelRegistrationRequest):
    """Register a new model or update existing one."""
    try:
        model = registry.register_model(request)
        return RegistrationResponse(
            success=True,
            model_id=model.id,
            message=f"Model {model.name} registered successfully"
        )
    except Exception as e:
        logger.error(f"Failed to register model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/models/{model_id}")
async def unregister_model(model_id: str):
    """Unregister a model."""
    if registry.unregister_model(model_id):
        return {"success": True, "message": f"Model {model_id} unregistered"}
    raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
