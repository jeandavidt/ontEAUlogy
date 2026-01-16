"""Ontology router for ontology management endpoints."""
import logging
from fastapi import APIRouter, HTTPException
from ..schemas.models import (
    OntologyInfo, EntityTriplesResponse, ValidationRequest,
    ValidationResponse
)
from ..services.ontology_store import ontology_store
from ..services.mapping_agent import mapping_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ontology", tags=["Ontology"])


@router.get("/", response_model=OntologyInfo)
async def get_ontology_info():
    """Get information about the full merged graph."""
    try:
        await ontology_store.load_ontology()
        namespaces = ontology_store.get_namespaces()
        entity_counts = ontology_store.get_entity_count()
        
        return OntologyInfo(
            graph_size=entity_counts["triples"],
            namespaces=list(namespaces.keys()),
            entities_count=entity_counts
        )
    except Exception as e:
        logger.error(f"Failed to get ontology info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entity/{uri:path}")
async def get_entity_triples(uri: str):
    """Get all triples about a specific entity."""
    try:
        await ontology_store.load_ontology()
        triples = ontology_store.get_triples_for_entity(uri)
        return EntityTriplesResponse(uri=uri, triples=triples)
    except Exception as e:
        logger.error(f"Failed to get entity triples: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate", response_model=ValidationResponse)
async def validate_graph(request: ValidationRequest):
    """Validate RDF data against SHACL shapes."""
    # Stub implementation - would use a SHACL validator
    logger.info(f"Validating graph (stub implementation)")
    
    return ValidationResponse(
        conforms=True,
        results=[]
    )


@router.get("/serialize")
async def serialize_ontology(format: str = "turtle"):
    """Serialize the ontology to a specific format."""
    try:
        await ontology_store.load_ontology()
        serialized = ontology_store.serialize(format)
        return {"data": serialized, "format": format}
    except Exception as e:
        logger.error(f"Failed to serialize ontology: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/merge")
async def merge_model_description(model_id: str, rdf_data: str):
    """Merge a model's self-description RDF into the unified graph."""
    try:
        await ontology_store.load_ontology()
        triples_count = ontology_store.merge_model_description(model_id, rdf_data)
        return {
            "success": True,
            "model_id": model_id,
            "triples_added": triples_count
        }
    except Exception as e:
        logger.error(f"Failed to merge model description: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate")
async def translate_ontology(rdf_data: str, source_format: str = "turtle"):
    """Translate RDF from foreign ontology to waterFRAME."""
    try:
        detected = mapping_agent.detect_ontology(rdf_data)
        translated = mapping_agent.translate_to_waterframe(rdf_data, source_format)
        return {
            "detected_ontologies": detected,
            "translated_rdf": translated
        }
    except Exception as e:
        logger.error(f"Failed to translate ontology: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reload")
async def reload_ontology():
    """Reload the ontology from disk."""
    try:
        await ontology_store.reload()
        return {"success": True, "message": "Ontology reloaded"}
    except Exception as e:
        logger.error(f"Failed to reload ontology: {e}")
        raise HTTPException(status_code=500, detail=str(e))
