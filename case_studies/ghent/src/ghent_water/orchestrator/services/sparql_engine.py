"""SPARQL engine for executing queries against RDF graphs."""
import csv
import io
import logging
import time
from typing import Any, Dict, List, Optional, Union
from rdflib import Graph

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
    
    def _format_results(self, results: List, format: str, 
                        query_time_ms: float) -> Dict:
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
        """Format results as JSON."""
        formatted_results = []
        
        for row in results:
            result = {}
            # Handle both SPARQLResult and regular results
            if hasattr(row, 'labels'):
                for var in row.labels:
                    result[var] = str(row[var])
            else:
                # For simple CONSTRUCT/DESCRIBE results
                result = {"subject": str(row[0]), 
                         "predicate": str(row[1]), 
                         "object": str(row[2])}
            
            formatted_results.append(result)
        
        return {
            "results": formatted_results,
            "format": "json",
            "query_time_ms": query_time_ms
        }
    
    def _to_csv(self, results: List, query_time_ms: float) -> Dict:
        """Format results as CSV."""
        if not results:
            return {
                "results": "",
                "format": "csv",
                "query_time_ms": query_time_ms
            }
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        if hasattr(results[0], 'labels'):
            headers = list(results[0].labels.keys())
        else:
            headers = ["subject", "predicate", "object"]
        writer.writerow(headers)
        
        # Write data rows
        for row in results:
            if hasattr(row, 'labels'):
                row_data = [str(row[var]) for var in row.labels]
            else:
                row_data = [str(row[0]), str(row[1]), str(row[2])]
            writer.writerow(row_data)
        
        return {
            "results": output.getvalue(),
            "format": "csv",
            "query_time_ms": query_time_ms
        }
    
    def _to_json_ld(self, results: List, query_time_ms: float) -> Dict:
        """Format results as JSON-LD."""
        # For JSON-LD, return the graph serialization
        if hasattr(results, 'graph'):
            graph = results.graph.serialize(format="json-ld")
            return {
                "results": graph,
                "format": "json-ld",
                "query_time_ms": query_time_ms
            }
        
        # Fall back to regular JSON for SELECT results
        return self._to_json(results, query_time_ms)
    
    def validate_query(self, query: str) -> Dict[str, Any]:
        """Validate a SPARQL query without executing it."""
        if self._graph is None:
            raise RuntimeError("No graph set. Call set_graph() first.")
        
        try:
            # Try to parse and validate the query
            self._graph.query("ASK { VALUES ?test { true } }")
            return {"valid": True, "error": None}
        except Exception as e:
            return {"valid": False, "error": str(e)}


# Global engine instance
sparql_engine = SparqlEngine()
