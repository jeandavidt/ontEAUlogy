"""Service to analyze natural language queries for required outputs."""

import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from .namespace_manager import namespace_manager

logger = logging.getLogger(__name__)


@dataclass
class QueryRequirements:
    """What a query needs to be answered."""
    target_outputs: Set[str]  # Parameter names
    involved_entities: Set[str]  # Entity URIs or IDs
    requires_aggregation: bool
    aggregation_type: Optional[str]  # sum, avg, max, min
    simulation_required: bool  # Whether we need to run models


class QueryAnalyzer:
    """
    Analyzes natural language queries to extract:
    - What output parameters are being asked for
    - What entities are involved
    - Whether simulation/aggregation is needed
    """
    
    # Common patterns for water quality parameters
    PARAMETER_PATTERNS = {
        "cod": ["cod", "chemical oxygen demand"],
        "bod": ["bod", "biological oxygen demand"],
        "tss": ["tss", "total suspended solids", "suspended solids"],
        "tn": ["tn", "total nitrogen", "nitrogen"],
        "tp": ["tp", "total phosphorus", "phosphorus"],
        "flow": ["flow", "flow rate", "discharge", "influent", "effluent"],
        "concentration": ["concentration", "level", "amount"],
        "energy": ["energy", "power consumption", "kwh"],
        "sludge": ["sludge", "biosolids"],
    }
    
    # Entity patterns
    ENTITY_PATTERNS = {
        "mbr": ["mbr", "membrane bioreactor", "bioreactor"],
        "ro": ["ro", "reverse osmosis", "osmosis", "membrane filtration"],
        "infiltration": ["infiltration", "soil", "groundwater"],
        "wwtp": ["wwtp", "wastewater treatment", "treatment plant"],
        "dwp": ["dwp", "drinking water", "water treatment"],
    }
    
    def __init__(self):
        self._ns = namespace_manager
    
    async def analyze(self, question: str) -> QueryRequirements:
        """
        Analyze a natural language question.
        
        Examples:
        - "What is the RO permeate COD?" → {target_outputs: {"ro_permeate_cod"}}
        - "MBR effluent quality?" → {target_outputs: {"mbr_effluent_cod", "mbr_effluent_tss"}}
        - "Total energy consumption?" → {target_outputs: {"energy"}, aggregation: "sum"}
        """
        question_lower = question.lower()
        
        # Extract entities mentioned
        entities = self._extract_entities(question_lower)
        
        # Extract parameters
        params = self._extract_parameters(question_lower, entities)
        
        # Check for aggregation
        aggregation, agg_type = self._detect_aggregation(question_lower)
        
        # Simulation is required if asking about outputs not currently in KG
        simulation = self._requires_simulation(params)
        
        return QueryRequirements(
            target_outputs=params,
            involved_entities=entities,
            requires_aggregation=aggregation,
            aggregation_type=agg_type,
            simulation_required=simulation
        )
    
    def _extract_entities(self, question: str) -> Set[str]:
        """Find entity mentions in the question."""
        entities = set()
        for entity, patterns in self.ENTITY_PATTERNS.items():
            for pattern in patterns:
                if pattern in question:
                    entities.add(entity)
                    break
        return entities
    
    def _extract_parameters(self, question: str, entities: Set[str]) -> Set[str]:
        """
        Find parameter names being asked about.
        
        Combines entity context with parameter type.
        """
        params = set()
        
        # Check for compound mentions like "RO permeate COD"
        for entity in entities:
            for param, patterns in self.PARAMETER_PATTERNS.items():
                for pattern in patterns:
                    # Check for patterns like "{entity} {param}" or "{param} of {entity}"
                    if f"{entity} {pattern}" in question or \
                       f"{pattern} of the {entity}" in question or \
                       f"{entity}'s {pattern}" in question:
                        params.add(f"{entity}_{param}")
                        break
        
        # If no specific parameters found, infer from question type
        if not params:
            if "quality" in question:
                # Quality queries usually want multiple parameters
                for entity in entities:
                    params.update([f"{entity}_cod", f"{entity}_tss", f"{entity}_tn"])
            elif "performance" in question:
                params.add("efficiency")
                params.add("energy")
        
        return params
    
    def _detect_aggregation(self, question: str) -> tuple[bool, Optional[str]]:
        """Check if question asks for aggregated values."""
        agg_patterns = {
            "sum": ["total", "sum", "combined", "overall"],
            "avg": ["average", "mean"],
            "max": ["maximum", "max", "highest", "peak"],
            "min": ["minimum", "min", "lowest"],
        }
        
        for agg_type, patterns in agg_patterns.items():
            for pattern in patterns:
                if pattern in question:
                    return True, agg_type
        
        return False, None
    
    def _requires_simulation(self, params: Set[str]) -> bool:
        """
        Check if these parameters require simulation to obtain.
        
        This would query the KG to see if values exist, or check
        if they're classified as "simulated outputs" in ontology.
        """
        # For now, assume any effluent/permeate output requires simulation
        simulated_indicators = ["effluent", "permeate", "outlet", "output"]
        for param in params:
            for indicator in simulated_indicators:
                if indicator in param:
                    return True
        return False


# Global instance
query_analyzer: Optional[QueryAnalyzer] = None


def get_query_analyzer() -> QueryAnalyzer:
    """Get or create the global QueryAnalyzer instance."""
    global query_analyzer
    if query_analyzer is None:
        query_analyzer = QueryAnalyzer()
    return query_analyzer
