"""Ontology loading and management utilities."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD

logger = logging.getLogger(__name__)


WATERFRAME_BASE = "https://ugentbiomath.github.io/waterframe#"
WF = Namespace(WATERFRAME_BASE)


class OntologyLoader:
    """Load ontology files from various sources."""

    def __init__(self):
        self.graph = Graph()
        self._bind_namespaces()

    def _bind_namespaces(self):
        """Bind common namespaces to the graph."""
        self.graph.bind("wf", WF)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        self.graph.bind("xsd", XSD)

    def load_file(self, filepath: Union[str, Path], format: Optional[str] = None) -> int:
        """Load a single ontology file.

        Args:
            filepath: Path to the ontology file
            format: RDF format (turtle, xml, etc.). Auto-detected if None.

        Returns:
            Number of triples loaded
        """
        path = Path(filepath)
        if not path.exists():
            logger.warning(f"Ontology file not found: {path}")
            return 0

        if format is None:
            format = self._detect_format(path)

        try:
            before = len(self.graph)
            self.graph.parse(str(path), format=format)
            after = len(self.graph)
            loaded = after - before
            logger.info(f"Loaded {loaded} triples from {path}")
            return loaded
        except Exception as e:
            logger.error(f"Failed to load ontology from {path}: {e}")
            return 0

    def load_directory(self, directory: Union[str, Path], pattern: str = "*.ttl") -> int:
        """Load all ontology files from a directory.

        Args:
            directory: Directory containing ontology files
            pattern: File pattern to match (default: *.ttl)

        Returns:
            Total number of triples loaded
        """
        path = Path(directory)
        if not path.exists():
            logger.warning(f"Directory not found: {path}")
            return 0

        total = 0
        for file in sorted(path.glob(pattern)):
            total += self.load_file(file)

        return total

    def _detect_format(self, path: Path) -> str:
        """Detect RDF format from file extension."""
        ext = path.suffix.lower()
        format_map = {
            ".ttl": "turtle",
            ".rdf": "xml",
            ".xml": "xml",
            ".n3": "n3",
            ".nt": "nt",
            ".jsonld": "json-ld",
        }
        return format_map.get(ext, "turtle")

    def get_graph(self) -> Graph:
        """Get the loaded graph."""
        return self.graph

    def get_triple_count(self) -> int:
        """Get the number of triples in the graph."""
        return len(self.graph)

    def query(self, sparql: str) -> List[Dict]:
        """Execute a SPARQL query.

        Args:
            sparql: SPARQL query string

        Returns:
            List of result bindings as dictionaries
        """
        try:
            results = self.graph.query(sparql)
            bindings = []
            for row in results:
                # Convert row to dict based on its type
                row_dict: Dict[str, str] = {}
                if isinstance(row, bool):
                    # ASK query result
                    row_dict["result"] = str(row)
                elif isinstance(row, tuple):
                    # SELECT query result
                    for i, value in enumerate(row):
                        row_dict[f"var_{i}"] = str(value)
                else:
                    # Single value or other
                    row_dict["value"] = str(row)
                bindings.append(row_dict)
            return bindings
        except Exception as e:
            logger.error(f"SPARQL query failed: {e}")
            return []


class OntologyManager:
    """Manage ontology state with caching and reloading."""

    def __init__(self):
        self.loader = OntologyLoader()
        self._loaded = False
        self._config: Optional[Dict] = None

    def configure(
        self, ontology_base_path: str, case_study_data_path: str, files: Optional[List[str]] = None
    ):
        """Configure the ontology manager.

        Args:
            ontology_base_path: Base path to shared ontology data
            case_study_data_path: Path to case study specific data
            files: List of specific files to load (relative to paths)
        """
        self._config = {
            "base_path": ontology_base_path,
            "case_path": case_study_data_path,
            "files": files or [],
        }

    async def load_ontology(self) -> bool:
        """Load ontology based on configuration.

        Returns:
            True if loaded successfully
        """
        if self._config is None:
            logger.warning("Ontology manager not configured")
            return False

        base_path = Path(self._config["base_path"])
        case_path = Path(self._config["case_path"])

        # Load base ontology
        if base_path.exists():
            self.loader.load_directory(base_path / "ontology", "*.ttl")

        # Load case study specific instances
        if case_path.exists():
            self.loader.load_directory(case_path / "instances", "*.ttl")
            # Also load any root level TTL files
            self.loader.load_directory(case_path, "*.ttl")

        # Load specific files if configured
        for file in self._config.get("files", []):
            # Try case path first, then base path
            case_file = case_path / file
            base_file = base_path / file

            if case_file.exists():
                self.loader.load_file(case_file)
            elif base_file.exists():
                self.loader.load_file(base_file)

        self._loaded = len(self.loader.graph) > 0
        if self._loaded:
            logger.info(f"Ontology loaded: {len(self.loader.graph)} triples")

        return self._loaded

    def is_loaded(self) -> bool:
        """Check if ontology is loaded."""
        return self._loaded

    def get_graph(self) -> Graph:
        """Get the ontology graph."""
        return self.loader.get_graph()

    def get_triple_count(self) -> int:
        """Get total triple count."""
        return self.loader.get_triple_count()

    async def reload(self) -> bool:
        """Reload ontology from disk."""
        self.loader = OntologyLoader()
        self._loaded = False
        return await self.load_ontology()


# Global instance for convenience
_global_manager: Optional[OntologyManager] = None


def get_ontology_manager() -> OntologyManager:
    """Get the global ontology manager instance."""
    global _global_manager
    if _global_manager is None:
        _global_manager = OntologyManager()
    return _global_manager
