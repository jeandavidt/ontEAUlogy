"""
Main Streamlit application entry point for the ontEAUlogy Ghent Water System Explorer.

This application provides an interactive web interface for exploring the water system
through a map view, SPARQL query panel, and natural language interface.
"""

import asyncio
from datetime import datetime
import streamlit as st

from .config import Config
from .components.map_view import create_map_view, get_entity_by_id
from .components.query_panel import render_query_panel
from .components.entity_details import render_entity_details
from .components.simulation_status import render_simulation_status
from .components.results_display import render_results, export_results
from .services.api_client import OrchestratorClient


def init_session_state() -> None:
    """Initialize Streamlit session state variables."""
    if "selected_entity" not in st.session_state:
        st.session_state.selected_entity = None
    if "query_results" not in st.session_state:
        st.session_state.query_results = None
    if "last_query_type" not in st.session_state:
        st.session_state.last_query_type = None
    if "jobs" not in st.session_state:
        st.session_state.jobs = []
    if "orchestrator_url" not in st.session_state:
        st.session_state.orchestrator_url = Config.ORCHESTRATOR_URL


def run_async(coro):
    """Run an async coroutine in the Streamlit context.
    
    Args:
        coro: The async coroutine to run.
        
    Returns:
        The result of the coroutine.
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


def handle_sparql_query(query: str, format: str) -> None:
    """Handle SPARQL query submission.
    
    Args:
        query: The SPARQL query string.
        format: The result format (json, table, json-ld).
    """
    with st.spinner("Executing SPARQL query..."):
        try:
            client = OrchestratorClient(st.session_state.orchestrator_url)
            results = run_async(client.run_sparql_query(query, format))
            st.session_state.query_results = results
            st.session_state.last_query_type = "sparql"
        except Exception as e:
            st.error(f"Error executing query: {e}")
            # Demo results for development
            st.session_state.query_results = {
                "results": {
                    "bindings": [
                        {"plant": {"type": "uri", "value": "http://example.org/WWTP-1"}},
                        {"plant": {"type": "uri", "value": "http://example.org/WWTP-2"}},
                    ]
                }
            }
            st.session_state.last_query_type = "sparql"


def handle_nl_query(question: str) -> None:
    """Handle natural language query submission.
    
    Args:
        question: The natural language question.
    """
    with st.spinner("Processing your question..."):
        try:
            client = OrchestratorClient(st.session_state.orchestrator_url)
            results = run_async(client.run_natural_query(question))
            st.session_state.query_results = results
            st.session_state.last_query_type = "natural"
        except Exception as e:
            st.error(f"Error processing question: {e}")
            # Demo results for development
            st.session_state.query_results = {
                "answer": f"Based on the analysis, the answer to '{question}' is: The BOD discharge from WWTP-1 is 15 mg/L under current conditions.",
                "data": [
                    {"parameter": "BOD", "value": 15, "unit": "mg/L", "location": "WWTP-1 Effluent"},
                    {"parameter": "COD", "value": 45, "unit": "mg/L", "location": "WWTP-1 Effluent"},
                ],
            }
            st.session_state.last_query_type = "natural"


def handle_view_model(entity_id: str) -> None:
    """Handle view model request for an entity.
    
    Args:
        entity_id: The entity ID to view.
    """
    st.info(f"Viewing model for {entity_id}")
    # In production, this would open a model detail view


def handle_run_simulation(entity_id: str) -> None:
    """Handle run simulation request for an entity.
    
    Args:
        entity_id: The entity ID to run simulation for.
    """
    st.info(f"Running simulation for {entity_id}")
    # In production, this would open a simulation input form


def main():
    """Main application function."""
    # Page configuration
    st.set_page_config(
        page_title=Config.PAGE_TITLE,
        page_icon=Config.PAGE_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Initialize session state
    init_session_state()
    
    # Load custom CSS
    try:
        with open("static/styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass
    
    # Main layout
    st.title(f"{Config.PAGE_ICON} {Config.PAGE_TITLE}")
    st.markdown("Explore the Ghent water system through the interactive map and query interface.")
    
    # Settings in sidebar
    with st.sidebar:
        st.header("Settings")
        st.session_state.orchestrator_url = st.text_input(
            "Orchestrator URL",
            value=st.session_state.orchestrator_url,
            help="URL of the running orchestrator API",
        )
        
        st.markdown("---")
        st.markdown("### Legend")
        st.markdown("💧 DWP - Drinking Water Plant")
        st.markdown("🚰 WWTP - Wastewater Treatment Plant")
        st.markdown("🏭 Industry - Industrial facility")
        st.markdown("🏠 Residential - Residential area")
        st.markdown("🌊 River - Waterway")
        
        st.markdown("---")
        st.markdown("### Status")
        st.markdown("🟢 Idle")
        st.markdown("🟠 Running")
        st.markdown("🔴 Error")
    
    # Main content area
    col_map, col_right = st.columns([1.5, 1])
    
    # Map view (left column)
    with col_map:
        st.markdown("#### System Map")
        clicked_entity = create_map_view(
            height=500,
            center_lat=Config.MAP_CENTER_LAT,
            center_lon=Config.MAP_CENTER_LON,
            zoom=Config.MAP_ZOOM,
            show_flows=True,
            selected_entity=st.session_state.selected_entity,
        )
        
        # Update selected entity if map was clicked
        if clicked_entity:
            st.session_state.selected_entity = clicked_entity
    
    # Right column - Entity details and Query panel
    with col_right:
        # Entity details panel
        render_entity_details(
            entity_id=st.session_state.selected_entity,
            on_view_model=handle_view_model,
            on_run_simulation=handle_run_simulation,
        )
        
        st.markdown("---")
        
        # Simulation status panel
        render_simulation_status(
            jobs=st.session_state.jobs,
            auto_refresh=True,
            refresh_interval=5,
        )
    
    # Query panel (full width below)
    st.markdown("---")
    render_query_panel(
        on_sparql_submit=handle_sparql_query,
        on_nl_submit=handle_nl_query,
    )
    
    # Results display
    if st.session_state.query_results is not None:
        st.markdown("---")
        render_results(
            results=st.session_state.query_results,
            result_type=st.session_state.last_query_type,
        )
        
        # Export options
        col_exp1, col_exp2, col_exp3 = st.columns(3)
        with col_exp1:
            export_results(
                st.session_state.query_results,
                format="csv",
                filename="query_results",
            )
        with col_exp2:
            export_results(
                st.session_state.query_results,
                format="json",
                filename="query_results",
            )
        with col_exp3:
            export_results(
                st.session_state.query_results,
                format="json-ld",
                filename="query_results",
            )


if __name__ == "__main__":
    main()
