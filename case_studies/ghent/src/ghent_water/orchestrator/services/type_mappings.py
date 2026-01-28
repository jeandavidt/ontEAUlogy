"""Shared type mappings for ontology entities.

This module provides centralized type mappings to ensure consistency
across the application between frontend and backend.
"""

# Type mapping for frontend compatibility
TYPE_MAPPING = {
    "DrinkingWaterPlant": "DWP",
    "WastewaterTreatmentPlant": "WWTP",
    "IndustrialFacility": "Industry",
    "RiverSegment": "River",
    "ResidentialDistrict": "Residential",
    "WaterQualitySensor": "Sensor",
    "FlowSensor": "Sensor",
    "WeatherSensor": "Sensor",
}


def get_display_label(ontology_type: str) -> str:
    """Get the display label for an ontology type.

    Args:
        ontology_type: The ontology type name.

    Returns:
        The display label, or the original type if not found.
    """
    return TYPE_MAPPING.get(ontology_type, ontology_type)


def get_all_mappings() -> dict:
    """Get all type mappings.

    Returns:
        Dictionary of all ontology type to display label mappings.
    """
    return TYPE_MAPPING.copy()
