"""Ontology store service for managing RDF graphs."""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD

from ontEAUlogy_shared import OntologyManager, get_namespace_manager

logger = logging.getLogger(__name__)

WATERFRAME_BASE = "https://ugentbiomath.github.io/waterframe#"
WF = Namespace(WATERFRAME_BASE)


class OntologyStore:
    """Service for loading and managing ontologies in the orchestrator."""

    def __init__(self):
        self._manager = OntologyManager()
        self._config: Optional[Dict[str, Any]] = None
        self._load_lock: Optional[asyncio.Lock] = None

    def configure(self, base_path: str, case_study_path: str, files: Optional[List[str]] = None):
        """Configure the ontology store.

        Args:
            base_path: Path to shared ontology data
            case_study_path: Path to case study specific data
            files: Optional list of specific files to load
        """
        self._manager.configure(
            ontology_base_path=base_path, case_study_data_path=case_study_path, files=files or []
        )
        self._config = {
            "base_path": base_path,
            "case_study_path": case_study_path,
            "files": files or [],
        }

    async def load_ontology(self, force: bool = False) -> bool:
        """Load the ontology.

        Args:
            force: If True, reload even if already loaded

        Returns:
            True if loaded successfully
        """
        if self._load_lock is None:
            self._load_lock = asyncio.Lock()

        async with self._load_lock:
            if self._manager.is_loaded() and not force:
                return True

            return await self._manager.load_ontology()

    def is_loaded(self) -> bool:
        """Check if ontology is loaded."""
        return self._manager.is_loaded()

    def get_graph(self) -> Graph:
        """Get the loaded ontology graph."""
        if not self.is_loaded():
            raise RuntimeError("Ontology not loaded. Call load_ontology() first.")
        return self._manager.get_graph()

    def get_triple_count(self) -> int:
        """Get the number of triples in the graph."""
        return self._manager.get_triple_count()

    def get_entity(self, entity_uri: str) -> Optional[Dict[str, Any]]:
        """Get entity details from the ontology.

        Args:
            entity_uri: URI of the entity

        Returns:
            Dictionary with entity details or None
        """
        if not self.is_loaded():
            return None

        try:
            graph = self.get_graph()
            entity_ref = URIRef(entity_uri)
            result = {"uri": entity_uri}

            # Get label
            labels = list(graph.objects(entity_ref, RDFS.label))
            if labels:
                result["label"] = str(labels[0])

            # Get type
            types = list(graph.objects(entity_ref, RDF.type))
            if types:
                result["type"] = [str(t) for t in types]

            # Get other properties
            for pred, obj in graph.predicate_objects(entity_ref):
                if pred not in (RDF.type, RDFS.label):
                    prop_name = str(pred).split("/")[-1].split("#")[-1]
                    if prop_name not in result:
                        result[prop_name] = []
                    result[prop_name].append(str(obj))

            return result
        except Exception as e:
            logger.error(f"Error getting entity {entity_uri}: {e}")
            return None

    def query_sparql(self, query: str) -> Dict[str, Any]:
        """Execute a SPARQL query against the ontology.

        Args:
            query: SPARQL query string

        Returns:
            Query results as dictionary
        """
        if not self.is_loaded():
            return {"error": "Ontology not loaded"}

        try:
            graph = self.get_graph()
            results = graph.query(query)

            bindings = []
            vars_list = []

            for row in results:
                binding = {}
                if hasattr(row, "labels"):
                    # SELECT query
                    if not vars_list:
                        vars_list = list(row.labels)
                    for var in row.labels:
                        value = row[var]
                        if value:
                            binding[var] = {
                                "type": "uri" if isinstance(value, URIRef) else "literal",
                                "value": str(value),
                            }
                elif isinstance(row, tuple):
                    # CONSTRUCT/DESCRIBE returns triples
                    binding = {
                        "subject": {
                            "type": "uri" if isinstance(row[0], URIRef) else "bnode",
                            "value": str(row[0]),
                        },
                        "predicate": {"type": "uri", "value": str(row[1])},
                        "object": {
                            "type": "uri" if isinstance(row[2], URIRef) else "literal",
                            "value": str(row[2]),
                        },
                    }
                bindings.append(binding)

            return {
                "head": {"vars": vars_list},
                "results": {"bindings": bindings},
            }
        except Exception as e:
            logger.error(f"SPARQL query failed: {e}")
            return {"error": str(e)}

    def add_triples(self, ttl_data: str, format: str = "turtle") -> int:
        """Add triples to the graph.

        Args:
            ttl_data: TTL string containing triples
            format: RDF format

        Returns:
            Number of triples added
        """
        if not self.is_loaded():
            logger.warning("Cannot add triples - ontology not loaded")
            return 0

        try:
            graph = self.get_graph()
            before = len(graph)
            graph.parse(data=ttl_data, format=format)
            after = len(graph)
            added = after - before
            logger.info(f"Added {added} triples to ontology")
            return added
        except Exception as e:
            logger.error(f"Failed to add triples: {e}")
            return 0


# Global instance
ontology_store = OntologyStore()
