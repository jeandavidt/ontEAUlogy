"""Query panel component with SPARQL editor and natural language interface."""

import streamlit as st

# Example SPARQL queries for the dropdown
EXAMPLE_SPARQL_QUERIES = {
    "All Water Treatment Plants": """SELECT ?plant ?label WHERE {
  ?plant a wf:WastewaterTreatmentPlant .
  ?plant rdfs:label ?label .
}""",
    "Entities in Upstream Zone": """SELECT ?entity ?type WHERE {
  ?entity wf:locatedInZone "upstream" .
  ?entity a ?type .
}""",
    "Decision Variables": """SELECT ?model ?param ?min ?max WHERE {
  ?model wf:hasInput ?input .
  ?input wf:isDecisionVariable true ;
         wf:parameterName ?param ;
         wf:minValue ?min ;
         wf:maxValue ?max .
}""",
    "Flow Connections": """SELECT ?from ?to ?flowType WHERE {
  ?connection a wf:FlowConnection ;
              wf:hasSource ?from ;
              wf:hasTarget ?to ;
              wf:flowType ?flowType .
}""",
    "Water Quality Parameters": """SELECT ?param ?unit ?description WHERE {
  ?param a wf:WaterQualityParameter ;
         wf:hasUnit ?unit ;
         rdfs:comment ?description .
}""",
}

# Example natural language questions
EXAMPLE_NL_QUESTIONS = [
    "What is the BOD at WWTP-1 effluent?",
    "What would happen to river quality if we doubled WWTP-1 discharge?",
    "Which industries have the highest water demand?",
    "What are the treatment capabilities of DWP-2?",
    "Show me all entities in the downstream zone",
    "What is the capacity of each WWTP?",
]


def render_query_panel(
    on_sparql_submit: callable,
    on_nl_submit: callable,
) -> None:
    """Render the query panel with SPARQL and natural language tabs.
    
    Args:
        on_sparql_submit: Callback function when SPARQL query is submitted.
                          Receives (query: str, format: str).
        on_nl_submit: Callback function when natural language question is submitted.
                      Receives (question: str).
    """
    tab_sparql, tab_nl = st.tabs(["SPARQL Query", "Natural Language"])
    
    # SPARQL Query Tab
    with tab_sparql:
        st.markdown("### SPARQL Editor")
        
        # Example query selector
        example_query = st.selectbox(
            "Example Queries",
            options=["Custom Query"] + list(EXAMPLE_SPARQL_QUERIES.keys()),
            key="sparql_example_selector",
        )
        
        if example_query != "Custom Query":
            default_query = EXAMPLE_SPARQL_QUERIES[example_query]
        else:
            default_query = ""
        
        # SPARQL editor
        query_text = st.text_area(
            "Enter your SPARQL query:",
            value=default_query,
            height=200,
            key="sparql_editor",
            help="Use PREFIX declarations if needed. Results will be displayed in selected format.",
        )
        
        # Format selector
        col1, col2 = st.columns([1, 3])
        with col1:
            result_format = st.selectbox(
                "Result Format",
                options=["json", "table", "json-ld"],
                key="sparql_format",
            )
        
        with col2:
            st.markdown("&nbsp;")
        
        # Submit button
        if st.button("Run SPARQL Query", key="run_sparql_btn", type="primary"):
            if query_text.strip():
                on_sparql_submit(query_text, result_format)
            else:
                st.warning("Please enter a SPARQL query.")
    
    # Natural Language Tab
    with tab_nl:
        st.markdown("### Ask Questions")
        st.markdown(
            "Ask questions about the water system in plain English. "
            "The system will interpret your question and provide answers."
        )
        
        # Example questions as clickable chips
        st.markdown("**Example questions:**")
        cols = st.columns(2)
        for i, question in enumerate(EXAMPLE_NL_QUESTIONS):
            with cols[i % 2]:
                if st.button(question, key=f"nl_example_{i}"):
                    st.session_state.nl_question_input = question
        
        # Question input
        default_question = st.session_state.get("nl_question_input", "")
        question_text = st.text_input(
            "Your question:",
            value=default_question,
            placeholder="e.g., What is the BOD discharge from WWTP-1?",
            key="nl_question_input",
        )
        
        # Clear the session state after using it
        if default_question:
            st.session_state.nl_question_input = ""
        
        # Submit button
        if st.button("Ask", key="ask_nl_btn", type="primary"):
            if question_text.strip():
                on_nl_submit(question_text)
            else:
                st.warning("Please enter a question.")
