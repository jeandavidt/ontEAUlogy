"""Ontology router for ontology management endpoints."""

import logging
from typing import Dict
from fastapi import APIRouter, HTTPException, Query
from ..schemas.models import (
    OntologyInfo,
    EntityTriplesResponse,
    ValidationRequest,
    ValidationResponse,
)
from ..services.ontology_store import ontology_store
from ..services.namespace_manager import namespace_manager
from ..services.mapping_agent import mapping_agent
from ..services.type_mappings import TYPE_MAPPING
from ..services.type_registry import type_registry

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
            entities_count=entity_counts,
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


@router.get("/entities/{entity_id}/triplets")
async def get_entity_triplets_by_id(entity_id: str):
    """Get all triples for an entity by its ID (slug)."""
    try:
        await ontology_store.load_ontology()

        # 1. Try direct match with the Ghent namespace
        uri = f"https://w3id.org/waterframe/case/ghent/{entity_id}"
        triples = ontology_store.get_triples_for_entity(uri)

        # 2. If no triples, try case-insensitive URI match or ID search
        if not triples:
            # Search for the entity URI in the graph by comparing the local name case-insensitively
            query = f"""
            SELECT ?entity WHERE {{
                ?entity a ?type .
                FILTER(LCASE(REPLACE(STR(?entity), "^.*[/|#]", "")) = LCASE("{entity_id}"))
                FILTER(STRSTARTS(STR(?entity), "https://w3id.org/waterframe/case/ghent/"))
            }} LIMIT 1
            """
            search_results = ontology_store.query_sparql(query)
            bindings = search_results.get("results", {}).get("bindings", [])
            if bindings:
                uri = bindings[0].get("entity", {}).get("value")
                triples = ontology_store.get_triples_for_entity(uri)

        return EntityTriplesResponse(uri=uri, triples=triples)
    except Exception as e:
        logger.error(f"Failed to get entity triples for {entity_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entities/{entity_id}")
async def get_entity_by_id(entity_id: str):
    """Get entity details by its ID (slug).

    Returns the same shape as /ontology/entities for frontend compatibility.
    """
    try:
        await ontology_store.load_ontology()

        query = f"""
        PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
        PREFIX sosa: <http://www.w3.org/ns/sosa/>

        SELECT ?entity ?label ?type ?description ?lat ?lon ?zone ?capacity ?population ?observes ?monitorsPort ?attachedTo
        WHERE {{
            ?entity a ?type ;
                    rdfs:label ?label .
            FILTER(STRSTARTS(STR(?entity), "https://w3id.org/waterframe/case/ghent/"))
            FILTER(LCASE(REPLACE(STR(?entity), "^.*[/|#]", "")) = LCASE("{entity_id}"))
            OPTIONAL {{ ?entity rdfs:comment ?description }}
            OPTIONAL {{ ?entity geo:lat ?lat }}
            OPTIONAL {{ ?entity geo:long ?lon }}
            OPTIONAL {{ ?entity wf:locatedInZone ?zone }}
            OPTIONAL {{ ?entity wf:hasCapacity ?capacity }}
            OPTIONAL {{ ?entity wf:hasPopulation ?population }}
            OPTIONAL {{ ?entity sosa:observes ?observes }}
            OPTIONAL {{ ?entity wf:monitorsPort ?monitorsPort }}
            OPTIONAL {{ ?entity wf:attachedTo ?attachedTo }}
        }}
        LIMIT 1
        """

        results = ontology_store.query_sparql(query)
        if "error" in results:
            raise HTTPException(status_code=500, detail=results["error"])

        bindings = results.get("results", {}).get("bindings", [])
        if not bindings:
            raise HTTPException(
                status_code=404, detail=f"Entity not found: {entity_id}"
            )

        def safe_float(value, default=0.0):
            try:
                return float(value)
            except (ValueError, TypeError):
                return default

        binding = bindings[0]
        entity_uri = binding.get("entity", {}).get("value", "")
        entity_id_value = entity_uri.split("/")[-1].split("#")[-1]
        raw_type = (
            binding.get("type", {}).get("value", "").split("/")[-1].split("#")[-1]
        )
        mapped_type = TYPE_MAPPING.get(raw_type, raw_type)

        return {
            "uri": entity_uri,
            "id": entity_id_value,
            "label": binding.get("label", {}).get("value", entity_id_value),
            "type": mapped_type,
            "raw_type": raw_type,
            "description": binding.get("description", {}).get("value", ""),
            "lat": safe_float(binding.get("lat", {}).get("value")),
            "lon": safe_float(binding.get("lon", {}).get("value")),
            "zone": binding.get("zone", {}).get("value", ""),
            "capacity": binding.get("capacity", {}).get("value", ""),
            "population": binding.get("population", {}).get("value", ""),
            "observes": binding.get("observes", {}).get("value", ""),
            "monitorsPort": binding.get("monitorsPort", {}).get("value", ""),
            "attachedTo": binding.get("attachedTo", {}).get("value", ""),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get entity for {entity_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate", response_model=ValidationResponse)
async def validate_graph(request: ValidationRequest):
    """Validate RDF data against SHACL shapes."""
    # Stub implementation - would use a SHACL validator
    logger.info(f"Validating graph (stub implementation)")

    return ValidationResponse(conforms=True, results=[])


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
async def merge_model_description(
    model_id: str = Query(...), rdf_data: str = Query(...)
):
    """Merge a model's self-description RDF into the unified graph."""
    try:
        await ontology_store.load_ontology()
        triples_count = await ontology_store.merge_model_description(model_id, rdf_data)
        return {"success": True, "model_id": model_id, "triples_added": triples_count}
    except Exception as e:
        logger.error(f"Failed to merge model description: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate")
async def translate_ontology(rdf_data: str, source_format: str = "turtle"):
    """Translate RDF from foreign ontology to waterFRAME."""
    try:
        detected = mapping_agent.detect_ontology(rdf_data)
        translated = mapping_agent.translate_to_waterframe(rdf_data, source_format)
        return {"detected_ontologies": detected, "translated_rdf": translated}
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


@router.get("/prefixes")
async def get_sparql_prefixes() -> Dict:
    """Get SPARQL PREFIX declarations for queries.

    Returns a dictionary with:
    - prefixes: The full SPARQL PREFIX block ready to use in queries
    - namespaces: Dictionary mapping prefix names to URIs
    """
    try:
        if not namespace_manager.is_loaded():
            namespace_manager.load_namespaces()

        return {
            "prefixes": namespace_manager.get_sparql_prefixes(),
            "namespaces": namespace_manager.get_all_prefixes(),
        }
    except Exception as e:
        logger.error(f"Failed to get prefixes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/namespaces")
async def get_namespaces() -> Dict[str, str]:
    """Get namespace URI mappings.

    Returns dictionary mapping prefix names to their URIs.
    """
    try:
        if not namespace_manager.is_loaded():
            namespace_manager.load_namespaces()

        return namespace_manager.get_all_prefixes()
    except Exception as e:
        logger.error(f"Failed to get namespaces: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types")
async def get_entity_types():
    """Get all entity types with their display metadata.

    Returns a list of entity types with visual properties for frontend rendering.
    Each type includes display label, color, icon, and description.
    """
    try:
        types = await type_registry.get_all_types()
        return {"types": types, "count": len(types)}
    except Exception as e:
        logger.error(f"Failed to get entity types: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entities")
async def get_all_entities():
    """Get all entities from the ontology.

    Returns a list of all entities with their properties including:
    - URI, label, type, description
    - Coordinates (lat, lon)
    - Zone, capacity, population (if available)
    """
    try:
        await ontology_store.load_ontology()

        # SPARQL query to get all entities with their properties
        query = """
        PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
        PREFIX sosa: <http://www.w3.org/ns/sosa/>
        PREFIX ghent: <https://w3id.org/waterframe/case/ghent/>

        SELECT ?entity ?label ?type ?description ?lat ?lon ?zone ?capacity ?population ?observes ?monitorsPort ?attachedTo
        WHERE {
            ?entity a ?type ;
                   rdfs:label ?label .
            # Filter to only include ghent case study entities
            FILTER(STRSTARTS(STR(?entity), "https://w3id.org/waterframe/case/ghent/"))
            OPTIONAL { ?entity rdfs:comment ?description }
            OPTIONAL { ?entity geo:lat ?lat }
            OPTIONAL { ?entity geo:long ?lon }
            OPTIONAL { ?entity wf:locatedInZone ?zone }
            OPTIONAL { ?entity wf:hasCapacity ?capacity }
            OPTIONAL { ?entity wf:hasPopulation ?population }
            OPTIONAL { ?entity sosa:observes ?observes }
            OPTIONAL { ?entity wf:monitorsPort ?monitorsPort }
            OPTIONAL { ?entity wf:attachedTo ?attachedTo }
        }
        ORDER BY ?label
        """

        results = ontology_store.query_sparql(query)

        if "error" in results:
            raise HTTPException(status_code=500, detail=results["error"])

        def safe_float(value, default=0.0):
            try:
                return float(value)
            except (ValueError, TypeError):
                return default

        # Type mapping for frontend compatibility

        entities = []
        for binding in results.get("results", {}).get("bindings", []):
            entity_uri = binding.get("entity", {}).get("value", "")
            # Extract entity ID from URI and PRESERVE casing
            # URI usually ends with /ID or #ID
            entity_id = entity_uri.split("/")[-1].split("#")[-1]

            raw_type = (
                binding.get("type", {}).get("value", "").split("/")[-1].split("#")[-1]
            )
            mapped_type = TYPE_MAPPING.get(raw_type, raw_type)

            entity_data = {
                "uri": entity_uri,
                "id": entity_id,
                "label": binding.get("label", {}).get("value", entity_id),
                "type": mapped_type,
                "raw_type": raw_type,
                "description": binding.get("description", {}).get("value", ""),
                "lat": safe_float(binding.get("lat", {}).get("value")),
                "lon": safe_float(binding.get("lon", {}).get("value")),
                "zone": binding.get("zone", {}).get("value", ""),
                "capacity": binding.get("capacity", {}).get("value", ""),
                "population": binding.get("population", {}).get("value", ""),
                "observes": binding.get("observes", {}).get("value", ""),
                "monitorsPort": binding.get("monitorsPort", {}).get("value", ""),
                "attachedTo": binding.get("attachedTo", {}).get("value", ""),
            }
            entities.append(entity_data)

        return {"entities": entities, "count": len(entities)}
    except Exception as e:
        logger.error(f"Failed to get entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))
