"""Service to analyze Knowledge Graph data availability."""

import logging
from typing import Dict, Optional, Set

logger = logging.getLogger(__name__)


class KGAnalyzer:
    """
    Analyzes the current state of the Knowledge Graph to determine
    what data is available and what needs to be computed.
    """
    
    def __init__(self, ontology_store):
        self._ontology = ontology_store
    
    async def get_available_parameters(self, entity_filter: Optional[str] = None) -> Set[str]:
        """
        Query the KG to find all parameters that have values.
        
        Returns set of parameter names (via wf:parameterName).
        """
        if not self._ontology.is_loaded():
            return set()
        
        entity_clause = ""
        if entity_filter:
            entity_clause = f'?entity wf:hasId "{entity_filter}" .'
        
        query = f"""
        PREFIX wf: <https://w3id.org/waterframe/>
        
        SELECT DISTINCT ?paramName
        WHERE {{
            {entity_clause}
            ?entity wf:hasParameter ?param .
            ?param wf:parameterName ?paramName ;
                   rdf:value ?value .
        }}
        """
        
        try:
            results = self._ontology.query_sparql(query)
            params = set()
            
            for binding in results.get("results", {}).get("bindings", []):
                param_name = binding.get("paramName", {}).get("value", "")
                if param_name:
                    params.add(param_name)
                    
            return params
            
        except Exception as e:
            logger.error(f"Failed to get available parameters: {e}")
            return set()
    
    async def has_parameter_value(self, param_name: str) -> bool:
        """Check if a specific parameter has a value in the KG."""
        query = f"""
        PREFIX wf: <https://w3id.org/waterframe/>
        
        ASK {{
            ?param wf:parameterName "{param_name}" ;
                   rdf:value ?value .
        }}
        """
        
        try:
            results = self._ontology.query_sparql(query)
            return results.get("boolean", False)
        except Exception as e:
            logger.error(f"Failed to check parameter {param_name}: {e}")
            return False


# Global instance
kg_analyzer: Optional[KGAnalyzer] = None


def get_kg_analyzer() -> KGAnalyzer:
    """Get or create the global KGAnalyzer instance."""
    global kg_analyzer
    if kg_analyzer is None:
        from .ontology_store import ontology_store
        kg_analyzer = KGAnalyzer(ontology_store)
    return kg_analyzer
