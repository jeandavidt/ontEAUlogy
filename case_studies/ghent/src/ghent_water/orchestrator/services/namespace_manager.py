"""Namespace manager service for dynamically loading ontology prefixes."""

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

    def __init__(self, ontology_base_path: Optional[Path] = None, case_study_data_path: Optional[Path] = None):
        """Initialize the namespace manager.

        Args:
            ontology_base_path: Path to the ontology data directory.
                               Defaults to ../../data relative to case study root.
            case_study_data_path: Path to case study data directory.
                                  Defaults to ../data relative to case study root.
        """
        case_study_root = Path(__file__).parent.parent.parent.parent.parent

        if ontology_base_path is None:
            # Default: use /app/data for container, or relative path for local dev
            if Path("/app/data").exists():
                ontology_base_path = Path("/app/data")
            else:
                ontology_base_path = case_study_root.parent.parent / "data"

        if case_study_data_path is None:
            case_study_data_path = case_study_root / "data"

        self._ontology_base_path = Path(ontology_base_path)
        self._case_study_data_path = Path(case_study_data_path)
        self._namespaces: Dict[str, Namespace] = {}
        self._prefix_uris: Dict[str, str] = {}
        self._loaded = False

        # Standard namespaces that are always available
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
        """Load namespaces from the ontology files.

        Returns:
            True if namespaces loaded successfully, False otherwise.
        """
        try:
            # Start with standard prefixes
            self._prefix_uris = dict(self._standard_prefixes)

            # Load main ontology to extract prefixes
            main_ontology = self._ontology_base_path / "ontology" / "waterframe.ttl"
            if main_ontology.exists():
                logger.info(f"Loading namespaces from {main_ontology}")
                graph = Graph()
                graph.parse(str(main_ontology), format="turtle")

                # Extract namespace bindings from the graph
                for prefix, namespace_uri in graph.namespaces():
                    if prefix:  # Skip empty prefix
                        uri_str = str(namespace_uri)
                        self._prefix_uris[prefix] = uri_str
                        self._namespaces[prefix] = Namespace(uri_str)
                        logger.debug(f"Loaded prefix {prefix}: {uri_str}")
            else:
                logger.warning(f"Main ontology not found: {main_ontology}")
                # Use fallback for waterframe namespace
                self._prefix_uris["wf"] = "https://ugentbiomath.github.io/waterframe#"

            # Also check for ghent case study prefix in system and instance files
            # Load from case study data path (ghent/data/)
            case_study_system_file = self._case_study_data_path / "system.ttl"
            if case_study_system_file.exists():
                try:
                    graph = Graph()
                    graph.parse(str(case_study_system_file), format="turtle")
                    for prefix, namespace_uri in graph.namespaces():
                        if prefix and prefix not in self._prefix_uris:
                            uri_str = str(namespace_uri)
                            self._prefix_uris[prefix] = uri_str
                            self._namespaces[prefix] = Namespace(uri_str)
                            logger.info(
                                f"Loaded namespace prefix: {prefix} -> {uri_str}"
                            )
                except Exception as e:
                    logger.warning(f"Could not parse {case_study_system_file} for namespaces: {e}")
            else:
                # Fall back to ontology base path for system.ttl
                system_file = self._ontology_base_path / "system.ttl"
                if system_file.exists():
                    try:
                        graph = Graph()
                        graph.parse(str(system_file), format="turtle")
                        for prefix, namespace_uri in graph.namespaces():
                            if prefix and prefix not in self._prefix_uris:
                                uri_str = str(namespace_uri)
                                self._prefix_uris[prefix] = uri_str
                                self._namespaces[prefix] = Namespace(uri_str)
                                logger.info(
                                    f"Loaded namespace prefix: {prefix} -> {uri_str}"
                                )
                    except Exception as e:
                        logger.warning(f"Could not parse {system_file} for namespaces: {e}")
                else:
                    logger.warning(f"System file not found (checked: {case_study_system_file} and {system_file})")

            # Load case study instance files for additional prefixes
            case_study_instances = self._case_study_data_path / "instances"
            if case_study_instances.exists():
                for ttl_file in case_study_instances.glob("**/*.ttl"):
                    try:
                        graph = Graph()
                        graph.parse(str(ttl_file), format="turtle")
                        for prefix, namespace_uri in graph.namespaces():
                            if prefix and prefix not in self._prefix_uris:
                                uri_str = str(namespace_uri)
                                self._prefix_uris[prefix] = uri_str
                                self._namespaces[prefix] = Namespace(uri_str)
                    except Exception as e:
                        logger.warning(
                            f"Could not parse {ttl_file} for namespaces: {e}"
                        )
            else:
                # Fall back to ontology base path for instances
                ghent_instances = self._ontology_base_path / "instances"
                if ghent_instances.exists():
                    for ttl_file in ghent_instances.glob("*.ttl"):
                        try:
                            graph = Graph()
                            graph.parse(str(ttl_file), format="turtle")
                            for prefix, namespace_uri in graph.namespaces():
                                if prefix and prefix not in self._prefix_uris:
                                    uri_str = str(namespace_uri)
                                    self._prefix_uris[prefix] = uri_str
                                    self._namespaces[prefix] = Namespace(uri_str)
                        except Exception as e:
                            logger.warning(
                                f"Could not parse {ttl_file} for namespaces: {e}"
                            )

            # Create Namespace objects for all prefixes
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
        """Get SPARQL PREFIX declarations for queries.

        Returns:
            String containing PREFIX declarations for SPARQL queries.
        """
        if not self._loaded:
            self.load_namespaces()

        # Build PREFIX declarations
        prefix_lines = []
        for prefix, uri in sorted(self._prefix_uris.items()):
            prefix_lines.append(f"PREFIX {prefix}: <{uri}>")

        return "\n".join(prefix_lines) + "\n"

    def get_namespace(self, prefix: str) -> Optional[Namespace]:
        """Get an rdflib Namespace object for a prefix.

        Args:
            prefix: The namespace prefix (e.g., 'wf', 'rdfs').

        Returns:
            The Namespace object, or None if not found.
        """
        if not self._loaded:
            self.load_namespaces()

        return self._namespaces.get(prefix)

    def get_namespace_uri(self, prefix: str) -> Optional[str]:
        """Get the URI for a namespace prefix.

        Args:
            prefix: The namespace prefix (e.g., 'wf', 'rdfs').

        Returns:
            The namespace URI string, or None if not found.
        """
        if not self._loaded:
            self.load_namespaces()

        return self._prefix_uris.get(prefix)

    def get_all_prefixes(self) -> Dict[str, str]:
        """Get all prefix-to-URI mappings.

        Returns:
            Dictionary mapping prefixes to their URIs.
        """
        if not self._loaded:
            self.load_namespaces()

        return dict(self._prefix_uris)

    @property
    def wf(self) -> Namespace:
        """Get the waterframe namespace."""
        ns = self.get_namespace("wf")
        if ns is None:
            # Fallback
            return Namespace("https://ugentbiomath.github.io/waterframe#")
        return ns

    @property
    def ontology_base_path(self) -> Path:
        """Get the ontology base path."""
        return self._ontology_base_path

    def is_loaded(self) -> bool:
        """Check if namespaces have been loaded."""
        return self._loaded


# Global namespace manager instance
# Honour ONTOLOGY_BASE_PATH env var so Docker bind-mounts work correctly
import os as _os
_ontology_base_override = _os.environ.get("ONTOLOGY_BASE_PATH")
namespace_manager = NamespaceManager(
    ontology_base_path=Path(_ontology_base_override) if _ontology_base_override else None
)
