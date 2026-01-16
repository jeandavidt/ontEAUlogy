"""Query router for SPARQL and natural language query endpoints."""
import logging
from fastapi import APIRouter, HTTPException
from ..schemas.models import (
    SparqlQueryRequest, SparqlQueryResponse,
    NaturalLanguageQueryRequest, NaturalLanguageQueryResponse
)
from ..services.sparql_engine import sparql_engine
from ..services.llm_sparql import llm_sparql_translator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/query", tags=["Query"])


@router.post("/sparql", response_model=SparqlQueryResponse)
async def execute_sparql_query(request: SparqlQueryRequest):
    """Execute a SPARQL query against the unified graph."""
    try:
        result = sparql_engine.execute_query(request.query, request.format)
        return SparqlQueryResponse(
            results=result.get("results", []),
            format=result.get("format", "json"),
            query_time_ms=result.get("query_time_ms", 0.0)
        )
    except Exception as e:
        logger.error(f"SPARQL query failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/natural", response_model=NaturalLanguageQueryRequest)
async def execute_natural_query(request: NaturalLanguageQueryRequest):
    """Execute a natural language query (NL → SPARQL → results)."""
    try:
        # Translate and execute
        result = await llm_sparql_translator.execute_query(
            request.question, 
            sparql_engine
        )
        
        return NaturalLanguageQueryResponse(
            original_question=request.question,
            generated_sparql=result.get("generated_sparql"),
            results=result.get("results"),
            execution_plan=result.get("execution_plan"),
            simulation_required=result.get("simulation_required", False),
            suggested_models=result.get("suggested_models", [])
        )
    except Exception as e:
        logger.error(f"Natural language query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/translate")
async def translate_question(question: str):
    """Translate a natural language question to SPARQL (without executing)."""
    try:
        result = await llm_sparql_translator.translate(question)
        return result
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
