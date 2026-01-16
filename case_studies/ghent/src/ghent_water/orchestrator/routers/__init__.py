"""API routers package."""

from .discovery import router as discovery_router
from .query import router as query_router
from .simulation import router as simulation_router
from .ontology import router as ontology_router

__all__ = ["discovery_router", "query_router", "simulation_router", "ontology_router"]
