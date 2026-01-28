"""SPARQL engine for executing queries against RDF graphs."""

import csv
import io
import logging
import time
from typing import Any, Dict, List, Optional, Union
from rdflib import Graph, URIRef, Literal, BNode
from rdflib.query import ResultException

logger = logging.getLogger(__name__)


class SparqlEngine:
    """Engine for executing SPARQL queries."""

    def __init__(self, graph: Optional[Graph] = None):
        self._graph = graph

    def set_graph(self, graph: Graph):
        """Set the graph to query against."""
        self._graph = graph

    def execute_query(self, query: str, format: str = "json") -> Dict:
        """Execute a SPARQL query and return results."""
        if self._graph is None:
            # Try to get from global ontology_store if available
            from .ontology_store import ontology_store

            if ontology_store.is_loaded():
                self._graph = ontology_store.get_graph()
            else:
                raise RuntimeError(
                    "No graph set and ontology not loaded. Call set_graph() or load_ontology() first."
                )

        start_time = time.time()

        try:
            results = list(self._graph.query(query))
            query_time_ms = (time.time() - start_time) * 1000

            formatted_results = self._format_results(results, format, query_time_ms)

            logger.info(f"SPARQL query executed in {query_time_ms:.2f}ms")

            return formatted_results

        except Exception as e:
            logger.error(f"SPARQL query failed: {e}")
            raise

    def _format_results(self, results: List, format: str, query_time_ms: float) -> Dict:
        """Format query results in the requested format."""
        if format == "json":
            return self._to_json(results, query_time_ms)
        elif format == "csv":
            return self._to_csv(results, query_time_ms)
        elif format == "json-ld":
            return self._to_json_ld(results, query_time_ms)
        else:
            return self._to_json(results, query_time_ms)

    def _to_json(self, results: List, query_time_ms: float) -> Dict:
        """Format results as standard SPARQL JSON format.

        Returns results in W3C SPARQL JSON format with bindings structure:
        {"results": {"bindings": [{"var": {"type": "uri", "value": "..."}}]}}
        """
        bindings = []

        for row in results:
            binding = {}
            # Handle both SPARQLResult and regular results
            if hasattr(row, "labels"):
                for var in row.labels:
                    value = row[var]
                    if value is not None:
                        value_type, value_str, binding_data = (
                            self._value_to_json_binding(value)
                        )
                        binding[str(var)] = binding_data
            else:
                # For CONSTRUCT/DESCRIBE results (triples), handle subject, predicate, object as URIRef/BNode/Literal
                binding = {
                    "subject": self._value_to_json_binding(row[0])[2],
                    "predicate": self._value_to_json_binding(row[1])[2],
                    "object": self._value_to_json_binding(row[2])[2],
                }

            if binding:
                bindings.append(binding)

        vars_list = []
        if len(results) > 0 and hasattr(results[0], "labels"):
            vars_list = [str(v) for v in results[0].labels]
        elif hasattr(results, "vars"):
            vars_list = [str(v) for v in results.vars]

        return {
            "head": {"vars": vars_list},
            "results": {"bindings": bindings},
            "format": "json",
            "query_time_ms": query_time_ms,
        }

    def _value_to_json_binding(
        self, value: Union[URIRef, Literal, BNode, Any]
    ) -> tuple[str, str, dict]:
        """Converts an RDFLib term to a JSON binding dictionary."""
        if isinstance(value, URIRef):
            value_type = "uri"
            value_str = str(value)
            binding_data = {"type": value_type, "value": value_str}
        elif isinstance(value, BNode):
            value_type = "bnode"
            value_str = str(value)
            binding_data = {"type": value_type, "value": value_str}
        elif isinstance(value, Literal):
            value_type = "literal"
            value_str = str(value)
            binding_data = {"type": value_type, "value": value_str}
            if value.datatype:
                binding_data["datatype"] = str(value.datatype)
            if value.language:
                binding_data["xml:lang"] = value.language
        else:
            # Fallback for unexpected types
            value_type = "literal"
            value_str = str(value)
            binding_data = {"type": value_type, "value": value_str}
        return value_type, value_str, binding_data

    def _to_csv(self, results: List, query_time_ms: float) -> Dict:
        """Format results as CSV."""
        if not results:
            return {"results": "", "format": "csv", "query_time_ms": query_time_ms}

        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        if hasattr(results[0], "labels"):
            headers = list(results[0].labels.keys())
        else:
            headers = ["subject", "predicate", "object"]
        writer.writerow(headers)

        # Write data rows
        for row in results:
            if hasattr(row, "labels"):
                row_data = [str(row[var]) for var in row.labels]
            else:
                row_data = [str(row[0]), str(row[1]), str(row[2])]
            writer.writerow(row_data)

        return {
            "results": output.getvalue(),
            "format": "csv",
            "query_time_ms": query_time_ms,
        }

    def _to_json_ld(self, results: List, query_time_ms: float) -> Dict:
        """Format results as JSON-LD."""
        # For JSON-LD, return the graph serialization
        if hasattr(results, "graph"):
            graph = results.graph.serialize(format="json-ld")
            return {
                "results": graph,
                "format": "json-ld",
                "query_time_ms": query_time_ms,
            }

        # Fall back to regular JSON for SELECT results
        return self._to_json(results, query_time_ms)

    def validate_query(self, query: str) -> Dict[str, Any]:
        """Validate a SPARQL query syntax without executing it."""
        from rdflib.query import ResultException

        if self._graph is None:
            # If no graph is set, we can't fully validate queries that might depend on it.
            # For now, we'll return an error, but this might be refined to allow basic syntax checks.
            return {"valid": False, "error": "No graph set for validation."}

        try:
            # Attempt to parse and compile the query, which will catch syntax errors
            self._graph.query(query)
            return {"valid": True, "error": None}
        except ResultException as e:
            return {"valid": False, "error": str(e)}
        except Exception as e:
            # Catch any other unexpected errors during query parsing/compilation
            return {"valid": False, "error": f"Unexpected error during validation: {e}"}


# Global engine instance
sparql_engine = SparqlEngine()
