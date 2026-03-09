"""Type Registry service for dynamic entity type metadata."""

import logging
from typing import Dict, List, Optional, Any
from ..services.ontology_store import ontology_store

logger = logging.getLogger(__name__)


class TypeRegistry:
    """Registry for entity type display metadata."""

    def __init__(self):
        self._types: Dict[str, Dict[str, Any]] = {}
        self._loaded = False

    async def _ensure_loaded(self):
        """Ensure type metadata is loaded from ontology."""
        if self._loaded:
            return

        try:
            await ontology_store.load_ontology()

            # SPARQL query to get display metadata for all entity types
            query = """
            PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?type ?label ?displayLabel ?displayColor ?displayIcon ?comment
            WHERE {
                {
                    ?type a rdfs:Class .
                    FILTER(STRSTARTS(STR(?type), "https://ugentbiomath.github.io/waterframe#"))
                } UNION {
                    ?type wf:displayLabel ?displayLabel .
                    FILTER(STRSTARTS(STR(?type), "https://ugentbiomath.github.io/waterframe#"))
                }
                OPTIONAL { ?type rdfs:label ?label }
                OPTIONAL { ?type wf:displayLabel ?displayLabel }
                OPTIONAL { ?type wf:displayColor ?displayColor }
                OPTIONAL { ?type wf:displayIcon ?displayIcon }
                OPTIONAL { ?type rdfs:comment ?comment }
            }
            """

            results = ontology_store.query_sparql(query)

            if "error" in results:
                logger.error(f"Failed to query type metadata: {results['error']}")
                return

            bindings = results.get("results", {}).get("bindings", [])

            for binding in bindings:
                type_uri = binding.get("type", {}).get("value", "")
                if not type_uri:
                    continue

                # Extract local name from URI
                local_name = type_uri.split("/")[-1].split("#")[-1]

                # Get display metadata with fallbacks
                display_label = (
                    binding.get("displayLabel", {}).get("value")
                    or binding.get("label", {}).get("value")
                    or local_name
                )

                display_color = binding.get("displayColor", {}).get("value", "#94a3b8")
                display_icon = binding.get("displayIcon", {}).get("value", "cube")
                comment = binding.get("comment", {}).get("value", "")

                self._types[local_name] = {
                    "uri": type_uri,
                    "localName": local_name,
                    "displayLabel": display_label,
                    "displayColor": display_color,
                    "displayIcon": display_icon,
                    "description": comment,
                    "label": binding.get("label", {}).get("value", local_name),
                }

            self._loaded = True
            logger.info(f"Loaded display metadata for {len(self._types)} entity types")

        except Exception as e:
            logger.error(f"Failed to load type registry: {e}")
            # Fallback to basic types if ontology loading fails
            self._load_fallback_types()

    def _load_fallback_types(self):
        """Load basic fallback types when ontology is unavailable."""
        fallback_types = {
            "DrinkingWaterPlant": {
                "uri": "https://ugentbiomath.github.io/waterframe#DrinkingWaterPlant",
                "localName": "DrinkingWaterPlant",
                "displayLabel": "DWP",
                "displayColor": "#15aabf",
                "displayIcon": "droplet-filled",
                "description": "Drinking Water Plant",
                "label": "Drinking Water Plant",
            },
            "WastewaterTreatmentPlant": {
                "uri": "https://ugentbiomath.github.io/waterframe#WastewaterTreatmentPlant",
                "localName": "WastewaterTreatmentPlant",
                "displayLabel": "WWTP",
                "displayColor": "#f59e0b",
                "displayIcon": "building-factory",
                "description": "Wastewater Treatment Plant",
                "label": "Wastewater Treatment Plant",
            },
            "River": {
                "uri": "https://ugentbiomath.github.io/waterframe#River",
                "localName": "River",
                "displayLabel": "River",
                "displayColor": "#06b6d4",
                "displayIcon": "wave",
                "description": "River or natural water body",
                "label": "River",
            },
            "WaterSensor": {
                "uri": "https://ugentbiomath.github.io/waterframe#WaterSensor",
                "localName": "WaterSensor",
                "displayLabel": "Sensor",
                "displayColor": "#8b5cf6",
                "displayIcon": "radar",
                "description": "Water quality or flow sensor",
                "label": "Water Sensor",
            },
            "IndustrialFacility": {
                "uri": "https://ugentbiomath.github.io/waterframe#IndustrialFacility",
                "localName": "IndustrialFacility",
                "displayLabel": "Industry",
                "displayColor": "#ef4444",
                "displayIcon": "factory",
                "description": "Industrial facility with water requirements",
                "label": "Industrial Facility",
            },
            "ResidentialArea": {
                "uri": "https://ugentbiomath.github.io/waterframe#ResidentialArea",
                "localName": "ResidentialArea",
                "displayLabel": "Residential",
                "displayColor": "#22c55e",
                "displayIcon": "home",
                "description": "Residential area or district",
                "label": "Residential Area",
            },
        }

        self._types = fallback_types
        self._loaded = True
        logger.info(f"Loaded {len(self._types)} fallback entity types")

    async def get_all_types(self) -> List[Dict[str, Any]]:
        """Get all entity types with display metadata."""
        await self._ensure_loaded()
        return list(self._types.values())

    async def get_display_label(self, type_name: str) -> str:
        """Get display label for a type."""
        await self._ensure_loaded()
        return self._types.get(type_name, {}).get("displayLabel", type_name)

    async def get_display_color(self, type_name: str) -> str:
        """Get display color for a type."""
        await self._ensure_loaded()
        return self._types.get(type_name, {}).get("displayColor", "#94a3b8")

    async def get_display_icon(self, type_name: str) -> str:
        """Get display icon for a type."""
        await self._ensure_loaded()
        return self._types.get(type_name, {}).get("displayIcon", "cube")

    async def get_type_metadata(self, type_name: str) -> Optional[Dict[str, Any]]:
        """Get complete metadata for a type."""
        await self._ensure_loaded()
        return self._types.get(type_name)

    async def reload(self):
        """Force reload type metadata from ontology."""
        self._loaded = False
        await self._ensure_loaded()


# Global type registry instance
type_registry = TypeRegistry()
