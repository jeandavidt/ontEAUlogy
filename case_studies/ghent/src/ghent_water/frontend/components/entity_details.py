"""Entity details panel component for displaying selected entity information."""

import streamlit as st

from .map_view import ENTITIES


def render_entity_details(
    entity_id: str | None,
    on_view_model: callable | None = None,
    on_run_simulation: callable | None = None,
) -> None:
    """Render the entity details panel.
    
    Args:
        entity_id: The currently selected entity ID, or None if no entity selected.
        on_view_model: Callback when "View Model" button is clicked.
                       Receives (entity_id: str).
        on_run_simulation: Callback when "Run Simulation" button is clicked.
                          Receives (entity_id: str).
    """
    st.markdown("### Entity Details")
    
    if entity_id is None:
        st.info("👈 Click on an entity on the map to view its details.")
        return
    
    entity = ENTITIES.get(entity_id)
    if entity is None:
        st.error(f"Entity '{entity_id}' not found.")
        return
    
    # Display entity information
    st.markdown(f"**{entity['icon']} {entity['name']}**")
    st.markdown("---")
    
    # Basic info in a grid
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Type:** {entity['type']}")
        st.markdown(f"**Zone:** {entity['zone'].title()}")
    with col2:
        status_color = "🟢" if entity['status'] == "idle" else "🟠" if entity['status'] == "running" else "🔴"
        st.markdown(f"**Status:** {status_color} {entity['status'].title()}")
    
    st.markdown(f"_{entity['description']}_")
    
    st.markdown("#### Location")
    st.markdown(f"- **Latitude:** {entity['lat']:.4f}°N")
    st.markdown(f"- **Longitude:** {entity['lon']:.4f}°E")
    
    # Action buttons
    st.markdown("---")
    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        if on_view_model:
            if st.button("View Model", key=f"view_model_{entity_id}"):
                on_view_model(entity_id)
    
    with btn_col2:
        if on_run_simulation:
            if st.button("Run Simulation", key=f"run_sim_{entity_id}"):
                on_run_simulation(entity_id)


def render_entity_list(filter_type: str | None = None) -> str | None:
    """Render a selectable list of entities.
    
    Args:
        filter_type: Optional entity type to filter by (e.g., "WWTP", "DWP").
        
    Returns:
        ID of the selected entity, or None.
    """
    entities = ENTITIES
    
    if filter_type:
        entities = {k: v for k, v in entities.items() if v.get("type") == filter_type}
    
    options = [""] + list(entities.keys())
    labels = ["Select an entity..."] + [f"{v['icon']} {v['name']} ({v['type']})" for v in entities.values()]
    
    option_map = dict(zip(options, labels))
    
    selected = st.selectbox(
        "Select Entity",
        options=options,
        format_func=lambda x: option_map.get(x, x),
    )
    
    return selected if selected else None
