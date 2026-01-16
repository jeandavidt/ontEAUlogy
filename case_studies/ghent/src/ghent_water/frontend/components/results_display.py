"""Results display component for query and simulation results."""

import json
import pandas as pd
import streamlit as st


def render_results(
    results: dict | list | str | None,
    result_type: str = "sparql",
    provenance: dict | None = None,
) -> None:
    """Render query or simulation results.
    
    Args:
        results: Results data to display.
        result_type: Type of results - "sparql", "natural", or "simulation".
        provenance: Optional provenance information about how results were generated.
    """
    st.markdown("### Results")
    st.markdown("═" * 60)
    
    if results is None:
        st.info("No results to display. Run a query or simulation first.")
        return
    
    if result_type == "natural":
        _render_natural_results(results, provenance)
    elif result_type == "simulation":
        _render_simulation_results(results, provenance)
    else:
        _render_sparql_results(results, provenance)


def _render_natural_results(results: dict, provenance: dict | None) -> None:
    """Render natural language query results.
    
    Args:
        results: Results dictionary with 'answer' and optionally 'data'.
        provenance: Provenance information.
    """
    # Answer
    answer = results.get("answer", "No answer generated.")
    st.markdown(f"**Answer:** {answer}")
    
    # Supporting data
    if "data" in results:
        st.markdown("#### Supporting Data")
        data = results["data"]
        if isinstance(data, list):
            df = pd.DataFrame(data)
            if not df.empty:
                st.dataframe(df, use_container_width=True)
        elif isinstance(data, dict):
            st.json(data)
    
    # Provenance
    if provenance:
        _render_provenance(provenance)


def _render_simulation_results(results: dict, provenance: dict | None) -> None:
    """Render simulation results.
    
    Args:
        results: Simulation results dictionary.
        provenance: Provenance information.
    """
    # Summary metrics
    if "summary" in results:
        st.markdown("#### Summary")
        summary = results["summary"]
        cols = st.columns(len(summary))
        for i, (key, value) in enumerate(summary.items()):
            cols[i].metric(key.replace("_", " ").title(), value)
    
    # Output data
    if "outputs" in results:
        st.markdown("#### Outputs")
        outputs = results["outputs"]
        
        # Try to display as dataframe
        if isinstance(outputs, list):
            df = pd.DataFrame(outputs)
            if not df.empty:
                st.dataframe(df, use_container_width=True)
        elif isinstance(outputs, dict):
            for key, value in outputs.items():
                st.markdown(f"**{key}:** {value}")
    
    # Time series data
    if "time_series" in results:
        st.markdown("#### Time Series")
        ts_data = results["time_series"]
        if isinstance(ts_data, list) and ts_data:
            df = pd.DataFrame(ts_data)
            if "timestamp" in df.columns:
                st.line_chart(df.set_index("timestamp"))
            else:
                st.line_chart(df)
    
    # Provenance
    if provenance:
        _render_provenance(provenance)


def _render_sparql_results(results: dict | list, provenance: dict | None) -> None:
    """Render SPARQL query results.
    
    Args:
        results: SPARQL results in JSON or tabular format.
        provenance: Provenance information.
    """
    # Handle different result formats
    if isinstance(results, dict):
        if "results" in results:
            # JSON result format with bindings
            bindings = results["results"]["bindings"]
            if not bindings:
                st.info("Query returned no results.")
                return
            
            # Convert bindings to flat dict
            flat_data = []
            for binding in bindings:
                row = {}
                for key, value in binding.items():
                    row[key] = value.get("value", value)
                flat_data.append(row)
            
            df = pd.DataFrame(flat_data)
            st.dataframe(df, use_container_width=True)
            
            # Show raw JSON option
            with st.expander("View Raw JSON"):
                st.json(results)
        
        elif "boolean" in results:
            st.markdown(f"**Result:** {results['boolean']}")
        
        else:
            # Unknown format, show as JSON
            st.json(results)
    
    elif isinstance(results, list):
        if not results:
            st.info("Query returned no results.")
            return
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)
    
    elif isinstance(results, str):
        # Plain text or turtle
        st.markdown("```")
        st.text(results)
        st.markdown("```")
    
    else:
        st.json(results)
    
    # Provenance
    if provenance:
        _render_provenance(provenance)


def _render_provenance(provenance: dict) -> None:
    """Render provenance information.
    
    Args:
        provenance: Provenance dictionary.
    """
    with st.expander("Provenance Information"):
        st.markdown("**Query/Simulation Details:**")
        if "query" in provenance:
            st.markdown(f"Query: `{provenance['query']}`")
        if "model" in provenance:
            st.markdown(f"Model: {provenance['model']}")
        if "timestamp" in provenance:
            st.markdown(f"Timestamp: {provenance['timestamp']}")
        if "source" in provenance:
            st.markdown(f"Source: {provenance['source']}")


def export_results(
    results: dict | list,
    format: str = "csv",
    filename: str = "results",
) -> None:
    """Create download buttons for results in various formats.
    
    Args:
        results: Results data to export.
        format: Export format - "csv", "json", or "json-ld".
        filename: Base filename for download.
    """
    if format == "csv":
        if isinstance(results, dict) and "results" in results:
            bindings = results["results"]["bindings"]
            flat_data = []
            for binding in bindings:
                row = {}
                for key, value in binding.items():
                    row[key] = value.get("value", value)
                flat_data.append(row)
            df = pd.DataFrame(flat_data)
            csv = df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                f"{filename}.csv",
                "text/csv",
            )
        elif isinstance(results, list):
            df = pd.DataFrame(results)
            csv = df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                f"{filename}.csv",
                "text/csv",
            )
    
    elif format == "json":
        json_str = json.dumps(results, indent=2)
        st.download_button(
            "Download JSON",
            json_str,
            f"{filename}.json",
            "application/json",
        )
    
    elif format == "json-ld":
        json_str = json.dumps(results, indent=2)
        st.download_button(
            "Download JSON-LD",
            json_str,
            f"{filename}.jsonld",
            "application/ld+json",
        )
