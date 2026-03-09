"""Shared utilities for ontEAUlogy case studies.

This package provides common functionality used across all case studies:
- Ontology loading and management
- RDF/JSON-LD serialization
- Namespace utilities
"""

__version__ = "0.1.0"

from .ontology import OntologyLoader, OntologyManager
from .namespaces import get_namespace_manager, CaseStudyNamespaces

__all__ = [
    "OntologyLoader",
    "OntologyManager",
    "get_namespace_manager",
    "CaseStudyNamespaces",
]
