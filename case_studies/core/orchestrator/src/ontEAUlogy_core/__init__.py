"""Core orchestrator for ontEAUlogy case studies.

This package provides a generic FastAPI orchestrator that can be configured
for different case studies (Ghent, Household, etc.) via YAML configuration files.
"""

__version__ = "0.1.0"

from .config import OrchestratorConfig, load_config
from .services.model_registry import ModelRegistry, registry
from .services.sparql_engine import SparqlEngine, sparql_engine
from .services.ontology_store import OntologyStore, ontology_store

__all__ = [
    "OrchestratorConfig",
    "load_config",
    "ModelRegistry",
    "registry",
    "SparqlEngine",
    "sparql_engine",
    "OntologyStore",
    "ontology_store",
]
