"""Interactive Folium map component for displaying the water system."""

import folium
from streamlit_folium import st_folium
import streamlit as st

# Entity coordinates and metadata (from Appendix B)
ENTITIES = {
    "dwp1": {
        "name": "DWP-1",
        "lat": 51.0620,
        "lon": 3.7300,
        "icon": "💧",
        "zone": "upstream",
        "type": "DWP",
        "description": "Drinking Water Plant - Upstream Zone",
        "status": "idle",
    },
    "dwp2": {
        "name": "DWP-2",
        "lat": 51.0540,
        "lon": 3.7450,
        "icon": "💧",
        "zone": "downstream",
        "type": "DWP",
        "description": "Drinking Water Plant - Downstream Zone",
        "status": "idle",
    },
    "wwtp1": {
        "name": "WWTP-1",
        "lat": 51.0560,
        "lon": 3.7400,
        "icon": "🚰",
        "zone": "upstream",
        "type": "WWTP",
        "description": "Wastewater Treatment Plant - Upstream Zone",
        "status": "running",
    },
    "wwtp2": {
        "name": "WWTP-2",
        "lat": 51.0480,
        "lon": 3.7560,
        "icon": "🚰",
        "zone": "downstream",
        "type": "WWTP",
        "description": "Wastewater Treatment Plant - Downstream Zone",
        "status": "idle",
    },
    "texfin": {
        "name": "Texfin NV",
        "lat": 51.0585,
        "lon": 3.7340,
        "icon": "👔",
        "zone": "upstream",
        "type": "Industry",
        "description": "Textile Industry",
        "status": "idle",
    },
    "foodpro": {
        "name": "FoodPro BVBA",
        "lat": 51.0575,
        "lon": 3.7360,
        "icon": "🍕",
        "zone": "upstream",
        "type": "Industry",
        "description": "Food Processing Company",
        "status": "idle",
    },
    "chiptech": {
        "name": "ChipTech NV",
        "lat": 51.0510,
        "lon": 3.7490,
        "icon": "💻",
        "zone": "downstream",
        "type": "Industry",
        "description": "Electronics Manufacturing",
        "status": "idle",
    },
    "pharmagen": {
        "name": "PharmaGen NV",
        "lat": 51.0500,
        "lon": 3.7510,
        "icon": "💊",
        "zone": "downstream",
        "type": "Industry",
        "description": "Pharmaceutical Manufacturing",
        "status": "error",
    },
    "brewco": {
        "name": "BrewCo BVBA",
        "lat": 51.0495,
        "lon": 3.7530,
        "icon": "🍺",
        "zone": "downstream",
        "type": "Industry",
        "description": "Brewery",
        "status": "idle",
    },
    "dampoort": {
        "name": "Dampoort Residential",
        "lat": 51.0600,
        "lon": 3.7320,
        "icon": "🏠",
        "zone": "upstream",
        "type": "Residential",
        "description": "Residential Area - Dampoort",
        "status": "idle",
    },
    "muide": {
        "name": "Muide Residential",
        "lat": 51.0520,
        "lon": 3.7470,
        "icon": "🏠",
        "zone": "downstream",
        "type": "Residential",
        "description": "Residential Area - Muide",
        "status": "idle",
    },
    "lieve_river": {
        "name": "Lieve River",
        "lat": 51.0550,
        "lon": 3.7430,
        "icon": "🌊",
        "zone": "both",
        "type": "River",
        "description": "Lieve River - Main waterway",
        "status": "idle",
    },
}

# Flow connections between entities
FLOW_CONNECTIONS = [
    # Water supply flows
    {"from": "lieve_river", "to": "dwp1", "type": "intake", "color": "blue"},
    {"from": "lieve_river", "to": "dwp2", "type": "intake", "color": "blue"},
    # Wastewater collection
    {"from": "dampoort", "to": "wwtp1", "type": "wastewater", "color": "orange"},
    {"from": "muide", "to": "wwtp2", "type": "wastewater", "color": "orange"},
    {"from": "texfin", "to": "wwtp1", "type": "wastewater", "color": "orange"},
    {"from": "foodpro", "to": "wwtp1", "type": "wastewater", "color": "orange"},
    {"from": "chiptech", "to": "wwtp2", "type": "wastewater", "color": "orange"},
    {"from": "pharmagen", "to": "wwtp2", "type": "wastewater", "color": "orange"},
    {"from": "brewco", "to": "wwtp2", "type": "wastewater", "color": "orange"},
    # Treated water discharge
    {"from": "wwtp1", "to": "lieve_river", "type": "discharge", "color": "green"},
    {"from": "wwtp2", "to": "lieve_river", "type": "discharge", "color": "green"},
    # DWP supply to residential
    {"from": "dwp1", "to": "dampoort", "type": "supply", "color": "cyan"},
    {"from": "dwp2", "to": "muide", "type": "supply", "color": "cyan"},
]


def _get_status_color(status: str) -> str:
    """Get marker color based on entity status."""
    status_colors = {
        "idle": "green",
        "running": "orange",
        "error": "red",
    }
    return status_colors.get(status, "gray")


def _create_marker(entity_id: str, entity_data: dict) -> folium.Marker:
    """Create a folium marker for an entity.
    
    Args:
        entity_id: Unique identifier for the entity.
        entity_data: Entity metadata including name, coordinates, type, and status.
        
    Returns:
        Configured folium Marker with popup and icon.
    """
    popup_html = f"""
    <div style="width: 200px;">
        <h4>{entity_data['name']}</h4>
        <p><b>Type:</b> {entity_data['type']}</p>
        <p><b>Zone:</b> {entity_data['zone']}</p>
        <p><b>Status:</b> {entity_data['status']}</p>
        <p><i>{entity_data['description']}</i></p>
    </div>
    """
    return folium.Marker(
        location=[entity_data["lat"], entity_data["lon"]],
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=f"{entity_data['icon']} {entity_data['name']}",
        icon=folium.Icon(
            icon=entity_data["icon"],
            color=_get_status_color(entity_data["status"]),
            prefix="emoji",
        ),
    )


def _add_flow_connections(m: folium.Map, show_labels: bool = True) -> None:
    """Add polyline flow connections to the map.
    
    Args:
        m: Folium map to add connections to.
        show_labels: Whether to show connection type labels.
    """
    for connection in FLOW_CONNECTIONS:
        from_entity = ENTITIES.get(connection["from"])
        to_entity = ENTITIES.get(connection["to"])
        
        if from_entity and to_entity:
            points = [
                [from_entity["lat"], from_entity["lon"]],
                [to_entity["lat"], to_entity["lon"]],
            ]
            
            flow_type = connection["type"]
            weight = 2 if flow_type in ["intake", "discharge"] else 1.5
            opacity = 0.8 if flow_type in ["intake", "discharge"] else 0.6
            
            folium.PolyLine(
                locations=points,
                weight=weight,
                color=connection["color"],
                opacity=opacity,
                popup=f"{flow_type.title()}: {from_entity['name']} → {to_entity['name']}",
                tooltip=f"{flow_type.title()} Flow",
            ).add_to(m)


def create_map_view(
    height: int = 500,
    center_lat: float = 51.055,
    center_lon: float = 3.743,
    zoom: int = 14,
    show_flows: bool = True,
    selected_entity: str | None = None,
) -> str | None:
    """Create and render the interactive Folium map.
    
    Args:
        height: Height of the map container in pixels.
        center_lat: Initial center latitude.
        center_lon: Initial center longitude.
        zoom: Initial zoom level.
        show_flows: Whether to display flow connection lines.
        selected_entity: Currently selected entity ID for highlighting.
        
    Returns:
        ID of the clicked entity, or None if no entity was clicked.
    """
    # Create the map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles="OpenStreetMap",
    )
    
    # Add flow connections
    if show_flows:
        _add_flow_connections(m)
    
    # Add entity markers
    for entity_id, entity_data in ENTITIES.items():
        marker = _create_marker(entity_id, entity_data)
        marker.add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Render with st_folium
    result = st_folium(
        m,
        height=height,
        width=None,
        key="map_view",
        returned_objects=["last_object_clicked"],
    )
    
    # Extract clicked entity ID
    if result and result.get("last_object_clicked"):
        clicked = result["last_object_clicked"]
        # Find the entity that was clicked
        for entity_id, entity_data in ENTITIES.items():
            if (
                abs(entity_data["lat"] - clicked["lat"]) < 0.001
                and abs(entity_data["lon"] - clicked["lng"]) < 0.001
            ):
                return entity_id
    
    return None


def get_entity_by_id(entity_id: str) -> dict | None:
    """Get entity data by ID.
    
    Args:
        entity_id: The unique identifier of the entity.
        
    Returns:
        Entity data dictionary or None if not found.
    """
    return ENTITIES.get(entity_id)


def get_all_entities() -> dict:
    """Get all entities.
    
    Returns:
        Dictionary of all entities indexed by ID.
    """
    return ENTITIES
