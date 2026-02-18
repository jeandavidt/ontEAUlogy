"""SPARQL engine for executing queries against RDF graphs.

Adapted from ghent_water for reuse across case studies.
"""

import csv
import io
import logging
import time
from typing import Any, Dict, List, Optional
from rdflib import Graph, URIRef, Literal, BNode

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
            raise RuntimeError("No graph set. Call set_graph() first.")

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
        """Format results as standard SPARQL JSON format."""
        bindings = []

        for row in results:
            binding = {}
            if hasattr(row, "labels"):
                for var in row.labels:
                    value = row[var]
                    if value is not None:
                        binding_data = self._value_to_json_binding(value)
                        binding[str(var)] = binding_data

            if binding:
                bindings.append(binding)

        vars_list = []
        if len(results) > 0 and hasattr(results[0], "labels"):
            vars_list = [str(v) for v in results[0].labels]

        return {
            "head": {"vars": vars_list},
            "results": {"bindings": bindings},
            "format": "json",
            "query_time_ms": query_time_ms,
        }

    def _value_to_json_binding(self, value):
        """Converts an RDFLib term to a JSON binding dictionary."""
        if isinstance(value, URIRef):
            return {"type": "uri", "value": str(value)}
        elif isinstance(value, BNode):
            return {"type": "bnode", "value": str(value)}
        elif isinstance(value, Literal):
            binding = {"type": "literal", "value": str(value)}
            if value.datatype:
                binding["datatype"] = str(value.datatype)
            if value.language:
                binding["xml:lang"] = value.language
            return binding
        else:
            return {"type": "literal", "value": str(value)}

    def _to_csv(self, results: List, query_time_ms: float) -> Dict:
        """Format results as CSV."""
        if not results:
            return {"results": "", "format": "csv", "query_time_ms": query_time_ms}

        output = io.StringIO()
        writer = csv.writer(output)

        if hasattr(results[0], "labels"):
            headers = list(results[0].labels.keys())
        else:
            headers = ["subject", "predicate", "object"]
        writer.writerow(headers)

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
        return self._to_json(results, query_time_ms)


sparql_engine = SparqlEngine()
