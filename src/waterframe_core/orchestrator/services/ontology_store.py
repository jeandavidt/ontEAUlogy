"""Ontology store service for managing the waterFRAME ontology.

Adapted from ghent_water for reuse across case studies.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS

logger = logging.getLogger(__name__)


class OntologyStore:
    """Service for loading and managing the waterFRAME ontology."""

    def __init__(
        self,
        ontology_base_path: Optional[str] = None,
        case_study_data_path: Optional[str] = None,
    ):
        """Initialize the ontology store.

        Args:
            ontology_base_path: Path to the ontEAUlogy/data directory.
            case_study_data_path: Path to case study data directory.
        """
        self._ontology_base: Optional[Path] = None
        self._case_data_path: Optional[Path] = None

        if ontology_base_path:
            self._ontology_base = Path(ontology_base_path)
        if case_study_data_path:
            self._case_data_path = Path(case_study_data_path)

        self._graph: Optional[Graph] = None
        self._loaded = False
        self._load_lock: Optional[asyncio.Lock] = None
        self._write_lock: Optional[asyncio.Lock] = None

    def configure(
        self,
        ontology_base_path: Optional[str] = None,
        case_study_data_path: Optional[str] = None,
    ):
        """Configure paths after initialization."""
        if ontology_base_path:
            self._ontology_base = Path(ontology_base_path)
        if case_study_data_path:
            self._case_data_path = Path(case_study_data_path)

    async def load_ontology(self, force: bool = False) -> bool:
        """Load the ontology from TTL files."""
        if self._load_lock is None:
            self._load_lock = asyncio.Lock()

        async with self._load_lock:
            if self._loaded and not force:
                return True

            if self._ontology_base is None:
                logger.warning("Ontology base path not configured")
                return False

            try:
                self._graph = Graph()
                files_loaded = 0

                main_ontology_path = self._ontology_base / "ontology" / "waterframe.ttl"
                if main_ontology_path.exists():
                    logger.info(f"Loading main ontology from {main_ontology_path}")
                    self._graph.parse(str(main_ontology_path), format="turtle")
                    files_loaded += 1

                modules_path = self._ontology_base / "ontology" / "modules"
                if modules_path.exists():
                    for module_file in modules_path.glob("*.ttl"):
                        logger.info(f"Loading module: {module_file.name}")
                        self._graph.parse(str(module_file), format="turtle")
                        files_loaded += 1
                    for module_file in modules_path.glob("**/*.ttl"):
                        if module_file.parent != modules_path:
                            self._graph.parse(str(module_file), format="turtle")
                            files_loaded += 1

                bridges_path = self._ontology_base / "ontology" / "bridges"
                if bridges_path.exists():
                    for bridge_file in bridges_path.glob("*.ttl"):
                        logger.info(f"Loading bridge: {bridge_file.name}")
                        self._graph.parse(str(bridge_file), format="turtle")
                        files_loaded += 1

                instances_path = self._ontology_base / "ontology" / "instances"
                if instances_path.exists():
                    for instance_file in instances_path.glob("*.ttl"):
                        logger.info(f"Loading ontology instance: {instance_file.name}")
                        self._graph.parse(str(instance_file), format="turtle")
                        files_loaded += 1

                if self._case_data_path:
                    system_ttl = self._case_data_path / "system.ttl"
                    if system_ttl.exists():
                        logger.info(f"Loading case study system: {system_ttl}")
                        self._graph.parse(str(system_ttl), format="turtle")
                        files_loaded += 1

                    case_instances_path = self._case_data_path / "instances"
                    if case_instances_path.exists():
                        for instance_file in sorted(
                            case_instances_path.glob("**/*.ttl")
                        ):
                            logger.info(f"Loading case instance: {instance_file}")
                            self._graph.parse(str(instance_file), format="turtle")
                            files_loaded += 1

                self._loaded = True
                logger.info(
                    f"Ontology loaded: {len(self._graph)} triples from {files_loaded} files"
                )
                return True

            except Exception as e:
                logger.error(f"Failed to load ontology: {e}")
                self._loaded = False
                return False

    def get_graph(self) -> Graph:
        """Get the loaded ontology graph."""
        if not self._loaded or self._graph is None:
            raise RuntimeError("Ontology not loaded. Call load_ontology() first.")
        return self._graph

    def get_entity(self, entity_uri: str) -> Optional[Dict[str, Any]]:
        """Get entity details from the ontology."""
        if not self._loaded or self._graph is None:
            return None

        try:
            entity_ref = URIRef(entity_uri)
            result = {"uri": entity_uri}

            labels = list(self._graph.objects(entity_ref, RDFS.label))
            if labels:
                result["label"] = str(labels[0])

            types = list(self._graph.objects(entity_ref, RDF.type))
            if types:
                result["type"] = [str(t) for t in types]

            for pred, obj in self._graph.predicate_objects(entity_ref):
                if pred not in (RDF.type, RDFS.label):
                    prop_name = str(pred).split("/")[-1].split("#")[-1]
                    result[prop_name] = str(obj)

            return result

        except Exception as e:
            logger.error(f"Error getting entity {entity_uri}: {e}")
            return None

    def query_sparql(self, query: str) -> Dict[str, Any]:
        """Execute a SPARQL query against the ontology."""
        if not self._loaded or self._graph is None:
            return {"error": "Ontology not loaded"}

        try:
            results = self._graph.query(query)
            bindings = []
            for row in results:
                binding = {}
                for var in row.labels:
                    value = row[var]
                    if value:
                        binding[var] = {
                            "type": "uri"
                            if hasattr(value, "toPython")
                            and str(value).startswith("http")
                            else "literal",
                            "value": str(value),
                        }
                if binding:
                    bindings.append(binding)

            return {"results": {"bindings": bindings}}

        except Exception as e:
            logger.error(f"SPARQL query error: {e}")
            return {"error": str(e)}

    def is_loaded(self) -> bool:
        """Check if ontology is loaded."""
        return self._loaded

    def get_triple_count(self) -> int:
        """Get the number of triples in the ontology."""
        if self._graph is None:
            return 0
        return len(self._graph)

    def get_namespaces(self) -> Dict[str, str]:
        """Get all namespace prefixes from the graph."""
        if self._graph is None:
            return {}
        return {str(prefix): str(uri) for prefix, uri in self._graph.namespaces()}

    def serialize(self, format: str = "turtle") -> str:
        """Serialize the graph to a string."""
        if self._graph is None:
            return ""
        return self._graph.serialize(format=format)

    def add_triples(self, rdf_data: str, format: str = "turtle") -> int:
        """Add RDF triples to the graph from raw data."""
        if self._graph is None:
            raise RuntimeError("Ontology not loaded")

        initial_count = len(self._graph)
        temp_graph = Graph()
        temp_graph.parse(data=rdf_data, format=format)
        self._graph += temp_graph
        return len(self._graph) - initial_count

    async def reload(self) -> bool:
        """Reload the ontology from disk."""
        self._loaded = False
        self._graph = None
        return await self.load_ontology()


ontology_store = OntologyStore()
