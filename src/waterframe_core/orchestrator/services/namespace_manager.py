"""Namespace manager service for dynamically loading ontology prefixes.

Adapted from ghent_water for reuse across case studies.
"""

import logging
from pathlib import Path
from typing import Dict, Optional
from rdflib import Graph, Namespace

logger = logging.getLogger(__name__)


class NamespaceManager:
    """Service for managing ontology namespaces and SPARQL prefixes.

    Reads prefix declarations from the ontology files rather than hardcoding them,
    allowing the system to adapt to ontology changes automatically.
    """

    def __init__(
        self,
        ontology_base_path: Optional[Path] = None,
        case_study_data_path: Optional[Path] = None,
    ):
        """Initialize the namespace manager.

        Args:
            ontology_base_path: Path to the ontology data directory.
            case_study_data_path: Path to case study data directory.
        """
        self._ontology_base_path = ontology_base_path
        self._case_study_data_path = case_study_data_path
        self._namespaces: Dict[str, Namespace] = {}
        self._prefix_uris: Dict[str, str] = {}
        self._loaded = False

        self._standard_prefixes = {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "owl": "http://www.w3.org/2002/07/owl#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "dc": "http://purl.org/dc/terms/",
            "qudt": "http://qudt.org/schema/qudt/",
            "unit": "http://qudt.org/vocab/unit/",
        }

    def load_namespaces(self) -> bool:
        """Load namespaces from the ontology files."""
        try:
            self._prefix_uris = dict(self._standard_prefixes)

            if self._ontology_base_path is None:
                return False

            main_ontology = self._ontology_base_path / "ontology" / "waterframe.ttl"
            if main_ontology.exists():
                logger.info(f"Loading namespaces from {main_ontology}")
                graph = Graph()
                graph.parse(str(main_ontology), format="turtle")

                for prefix, namespace_uri in graph.namespaces():
                    if prefix:
                        uri_str = str(namespace_uri)
                        self._prefix_uris[prefix] = uri_str
                        self._namespaces[prefix] = Namespace(uri_str)

            if self._case_study_data_path:
                system_file = self._case_study_data_path / "system.ttl"
                if system_file.exists():
                    try:
                        graph = Graph()
                        graph.parse(str(system_file), format="turtle")
                        for prefix, namespace_uri in graph.namespaces():
                            if prefix and prefix not in self._prefix_uris:
                                uri_str = str(namespace_uri)
                                self._prefix_uris[prefix] = uri_str
                                self._namespaces[prefix] = Namespace(uri_str)
                    except Exception as e:
                        logger.warning(f"Could not parse {system_file}: {e}")

            for prefix, uri in self._prefix_uris.items():
                if prefix not in self._namespaces:
                    self._namespaces[prefix] = Namespace(uri)

            self._loaded = True
            logger.info(f"Loaded {len(self._prefix_uris)} namespace prefixes")
            return True

        except Exception as e:
            logger.error(f"Failed to load namespaces: {e}")
            self._loaded = False
            return False

    def get_sparql_prefixes(self) -> str:
        """Get SPARQL PREFIX declarations for queries."""
        if not self._loaded:
            self.load_namespaces()

        prefix_lines = []
        for prefix, uri in sorted(self._prefix_uris.items()):
            prefix_lines.append(f"PREFIX {prefix}: <{uri}>")

        return "\n".join(prefix_lines) + "\n"

    def get_namespace(self, prefix: str) -> Optional[Namespace]:
        """Get an rdflib Namespace object for a prefix."""
        if not self._loaded:
            self.load_namespaces()

        return self._namespaces.get(prefix)

    def get_namespace_uri(self, prefix: str) -> Optional[str]:
        """Get the URI for a namespace prefix."""
        if not self._loaded:
            self.load_namespaces()

        return self._prefix_uris.get(prefix)

    def get_all_prefixes(self) -> Dict[str, str]:
        """Get all prefix-to-URI mappings."""
        if not self._loaded:
            self.load_namespaces()

        return dict(self._prefix_uris)

    @property
    def wf(self) -> Namespace:
        """Get the waterframe namespace."""
        ns = self.get_namespace("wf")
        if ns is None:
            return Namespace("https://ugentbiomath.github.io/waterframe#")
        return ns

    def is_loaded(self) -> bool:
        """Check if namespaces have been loaded."""
        return self._loaded


namespace_manager = NamespaceManager()
