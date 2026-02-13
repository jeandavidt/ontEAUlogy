"""Ontology store service for managing the waterFRAME ontology."""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS

from ghent_water.orchestrator.services.namespace_manager import namespace_manager

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
                               Defaults to ../../data relative to case study root.
            case_study_data_path: Path to case study data directory.
                                  Defaults to data/ relative to case study root.
        """
        # Case study root: ghent/
        self._case_study_root = Path(__file__).parent.parent.parent.parent.parent

        # Ontology base path (ontEAUlogy/data)
        if ontology_base_path:
            self._ontology_base = Path(ontology_base_path)
            if not self._ontology_base.is_absolute():
                self._ontology_base = self._case_study_root / self._ontology_base
        else:
            # Default: ../../data from case study root
            self._ontology_base = self._case_study_root.parent.parent / "data"

        # Case study data path (ghent/data)
        if case_study_data_path:
            self._case_data_path = Path(case_study_data_path)
            if not self._case_data_path.is_absolute():
                self._case_data_path = self._case_study_root / case_study_data_path
        else:
            self._case_data_path = self._case_study_root / "data"

        self._graph: Optional[Graph] = None
        self._loaded = False
        self._load_lock: Optional[asyncio.Lock] = None
        self._write_lock: Optional[asyncio.Lock] = None

    async def load_ontology(self, force: bool = False) -> bool:
        """Load the ontology from TTL files.

        Loads from:
        1. Main ontology: ontEAUlogy/data/ontology/waterframe.ttl
        2. Ontology modules: ontEAUlogy/data/ontology/modules/*.ttl
        3. Ontology instances: ontEAUlogy/data/ontology/instances/*.ttl
        4. Case study data: ghent/data/system.ttl
        5. Case study instances: ghent/data/instances/*.ttl

        Args:
            force: If True, reload even if already loaded.

        Returns:
            True if ontology loaded successfully, False otherwise.
        """
        # Initialize lock on first use (after event loop is running)
        if self._load_lock is None:
            self._load_lock = asyncio.Lock()

        async with self._load_lock:
            if self._loaded and not force:
                return True

            try:
                self._graph = Graph()
                files_loaded = 0

                # Initialize namespace manager
                if not namespace_manager.is_loaded():
                    namespace_manager.load_namespaces()

                # 1. Load main ontology from ontEAUlogy/data/ontology/
                main_ontology_path = self._ontology_base / "ontology" / "waterframe.ttl"
                if main_ontology_path.exists():
                    logger.info(f"Loading main ontology from {main_ontology_path}")
                    self._graph.parse(str(main_ontology_path), format="turtle")
                    files_loaded += 1
                else:
                    logger.warning(f"Main ontology not found: {main_ontology_path}")

                # 2. Load ontology modules from ontEAUlogy/data/ontology/modules/
                modules_path = self._ontology_base / "ontology" / "modules"
                if modules_path.exists():
                    # Load top-level module files
                    for module_file in modules_path.glob("*.ttl"):
                        logger.info(f"Loading module: {module_file.name}")
                        self._graph.parse(str(module_file), format="turtle")
                        files_loaded += 1
                    # Load nested modules (e.g., core/)
                    for module_file in modules_path.glob("**/*.ttl"):
                        if module_file.parent != modules_path:
                            logger.info(f"Loading nested module: {module_file}")
                            self._graph.parse(str(module_file), format="turtle")
                            files_loaded += 1

                # 2b. Load ontology bridge modules from ontEAUlogy/data/ontology/bridges/
                bridges_path = self._ontology_base / "ontology" / "bridges"
                if bridges_path.exists():
                    for bridge_file in bridges_path.glob("*.ttl"):
                        logger.info(f"Loading bridge module: {bridge_file.name}")
                        self._graph.parse(str(bridge_file), format="turtle")
                        files_loaded += 1

                # 3. Load ontology instances from ontEAUlogy/data/ontology/instances/
                instances_path = self._ontology_base / "ontology" / "instances"
                if instances_path.exists():
                    for instance_file in instances_path.glob("*.ttl"):
                        logger.info(f"Loading ontology instance: {instance_file.name}")
                        self._graph.parse(str(instance_file), format="turtle")
                        files_loaded += 1

                # 4. Load case study system definition from ghent/data/
                system_ttl = self._case_data_path / "system.ttl"
                if system_ttl.exists():
                    logger.info(f"Loading case study system: {system_ttl}")
                    self._graph.parse(str(system_ttl), format="turtle")
                    files_loaded += 1

                # 4.1. Load display metadata from ghent/data/display_metadata.ttl
                display_metadata_ttl = self._case_data_path / "display_metadata.ttl"
                if display_metadata_ttl.exists():
                    logger.info(f"Loading display metadata: {display_metadata_ttl}")
                    self._graph.parse(str(display_metadata_ttl), format="turtle")
                    files_loaded += 1

                # 5. Load case study instances from ghent/data/instances/ (including nested sensors)
                case_instances_path = self._case_data_path / "instances"
                if case_instances_path.exists():
                    for instance_file in sorted(case_instances_path.glob("**/*.ttl")):
                        logger.info(f"Loading case instance: {instance_file}")
                        self._graph.parse(str(instance_file), format="turtle")
                        files_loaded += 1

                # 6. Load household case study instances from household/data/instances/
                household_instances = self._case_study_root.parent / "household" / "data" / "instances"
                if household_instances.exists():
                    for ttl_file in sorted(household_instances.glob("**/*.ttl")):
                        logger.info(f"Loading household instance: {ttl_file}")
                        self._graph.parse(str(ttl_file), format="turtle")
                        files_loaded += 1

                self._loaded = True
                logger.info(
                    f"Ontology loaded successfully: {len(self._graph)} triples from {files_loaded} files"
                )
                return True

            except Exception as e:
                logger.error(f"Failed to load ontology: {e}")
                self._loaded = False
                return False

    def get_graph(self) -> Graph:
        """Get the loaded ontology graph.

        Returns:
            The RDF graph.

        Raises:
            RuntimeError: If ontology not loaded.
        """
        if not self._loaded or self._graph is None:
            raise RuntimeError("Ontology not loaded. Call load_ontology() first.")
        return self._graph

    def get_entity(self, entity_uri: str) -> Optional[Dict[str, Any]]:
        """Get entity details from the ontology.

        Args:
            entity_uri: URI of the entity.

        Returns:
            Dictionary with entity details or None if not found.
        """
        if not self._loaded or self._graph is None:
            return None

        try:
            entity_ref = URIRef(entity_uri)
            result = {"uri": entity_uri}

            # Get label
            labels = list(self._graph.objects(entity_ref, RDFS.label))
            if labels:
                result["label"] = str(labels[0])

            # Get type
            types = list(self._graph.objects(entity_ref, RDF.type))
            if types:
                result["type"] = [str(t) for t in types]

            # Get properties
            for pred, obj in self._graph.predicate_objects(entity_ref):
                if pred not in (RDF.type, RDFS.label):
                    # Strip both # and / from the predicate URI
                    prop_name = str(pred).split("/")[-1].split("#")[-1]
                    result[prop_name] = str(obj)

            return result

        except Exception as e:
            logger.error(f"Error getting entity {entity_uri}: {e}")
            return None

    def query_sparql(self, query: str) -> Dict[str, Any]:
        """Execute a SPARQL query against the ontology.

        Args:
            query: SPARQL query string.

        Returns:
            Query results as dictionary.
        """
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
        """Check if ontology is loaded.

        Returns:
            True if ontology is loaded, False otherwise.
        """
        return self._loaded

    def get_triple_count(self) -> int:
        """Get the number of triples in the ontology.

        Returns:
            Number of triples.
        """
        if self._graph is None:
            return 0
        return len(self._graph)

    def get_namespaces(self) -> Dict[str, str]:
        """Get all namespace prefixes from the graph.

        Returns:
            Dictionary mapping prefixes to URIs.
        """
        if self._graph is None:
            return {}
        return {str(prefix): str(uri) for prefix, uri in self._graph.namespaces()}

    def get_entity_count(self) -> Dict[str, int]:
        """Get counts of entities by type.

        Returns:
            Dictionary with entity counts including total triples.
        """
        if self._graph is None:
            return {"triples": 0}

        counts = {"triples": len(self._graph)}

        # Count entities by type using SPARQL
        query = """
        SELECT ?type (COUNT(?s) as ?count)
        WHERE { ?s a ?type }
        GROUP BY ?type
        """
        try:
            results = self._graph.query(query)
            for row in results:
                # Strip both # and / from the type URI
                type_uri = str(row[0]).split("#")[-1].split("/")[-1]
                counts[type_uri] = int(row[1])
        except Exception as e:
            logger.warning(f"Could not count entities: {e}")

        return counts

    def get_triples_for_entity(self, uri: str) -> list:
        """Get all triples where the entity is subject or object.

        Args:
            uri: The entity URI.

        Returns:
            List of triple dictionaries.
        """
        if self._graph is None:
            return []

        triples = []
        entity_ref = URIRef(uri)

        # Triples where entity is subject
        for pred, obj in self._graph.predicate_objects(entity_ref):
            triples.append(
                {
                    "subject": uri,
                    "predicate": str(pred),
                    "object": str(obj),
                    "isUri": isinstance(obj, URIRef),
                }
            )

        # Triples where entity is object
        for subj, pred in self._graph.subject_predicates(entity_ref):
            triples.append(
                {
                    "subject": str(subj),
                    "predicate": str(pred),
                    "object": uri,
                    "isUri": True,
                }
            )

        return triples

    def serialize(self, format: str = "turtle") -> str:
        """Serialize the graph to a string.

        Args:
            format: Output format (turtle, xml, json-ld, etc.)

        Returns:
            Serialized graph string.
        """
        if self._graph is None:
            return ""
        return self._graph.serialize(format=format)

    async def merge_model_description(self, model_id: str, rdf_data: str) -> int:
        """Merge RDF data from a model into the graph.

        Args:
            model_id: Identifier for the model.
            rdf_data: RDF data in turtle format.

        Returns:
            Number of triples added.
        """
        # Initialize lock on first use
        if self._write_lock is None:
            self._write_lock = asyncio.Lock()

        async with self._write_lock:
            if self._graph is None:
                raise RuntimeError("Ontology not loaded")

            initial_count = len(self._graph)
            temp_graph = Graph()
            temp_graph.parse(data=rdf_data, format="turtle")

            # Atomic merge operation
            self._graph += temp_graph
            return len(self._graph) - initial_count

    def add_triples(self, rdf_data: str, format: str = "turtle") -> int:
        """Add RDF triples to the graph from raw data.

        Args:
            rdf_data: RDF data as a string.
            format: RDF serialization format.

        Returns:
            Number of triples added.
        """
        if self._graph is None:
            raise RuntimeError("Ontology not loaded")

        initial_count = len(self._graph)
        temp_graph = Graph()
        temp_graph.parse(data=rdf_data, format=format)
        self._graph += temp_graph
        return len(self._graph) - initial_count

    async def reload(self) -> bool:
        """Reload the ontology from disk.

        Returns:
            True if reload successful.
        """
        self._loaded = False
        self._graph = None
        return await self.load_ontology()


# Global ontology store instance
# Honour ONTOLOGY_BASE_PATH env var so Docker bind-mounts work correctly
import os as _os
ontology_store = OntologyStore(
    ontology_base_path=_os.environ.get("ONTOLOGY_BASE_PATH") or None
)
