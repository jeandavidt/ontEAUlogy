"""Namespace management for case studies."""

from dataclasses import dataclass
from typing import Dict, Optional
from rdflib import Namespace


WATERFRAME_BASE = "https://ugentbiomath.github.io/waterframe#"
CAPABILITY_BASE = "https://ugentbiomath.github.io/waterframe/capability#"


@dataclass
class CaseStudyNamespaces:
    """Namespace configuration for a case study."""

    # Base namespaces (always present)
    wf: Namespace = Namespace(WATERFRAME_BASE)
    cap: Namespace = Namespace(CAPABILITY_BASE)

    # Case study specific namespaces
    case: Optional[Namespace] = None
    entities: Optional[Namespace] = None

    def __post_init__(self):
        """Ensure all namespaces are Namespace objects."""
        if isinstance(self.case, str):
            self.case = Namespace(self.case)
        if isinstance(self.entities, str):
            self.entities = Namespace(self.entities)

    def to_dict(self) -> Dict[str, Namespace]:
        """Convert to dictionary for RDFLib binding."""
        result = {
            "wf": self.wf,
            "cap": self.cap,
        }
        if self.case:
            result["case"] = self.case
        if self.entities:
            result["entities"] = self.entities
        return result

    def get_prefix_map(self) -> Dict[str, str]:
        """Get prefix to URI mapping."""
        result = {
            "wf": str(self.wf),
            "cap": str(self.cap),
        }
        if self.case:
            result["case"] = str(self.case)
        if self.entities:
            result["entities"] = str(self.entities)
        return result


class NamespaceManager:
    """Manage namespaces for multiple case studies."""

    def __init__(self):
        self._namespaces: Dict[str, CaseStudyNamespaces] = {}

    def register_case_study(
        self, name: str, case_uri: str, entity_uri: Optional[str] = None
    ) -> CaseStudyNamespaces:
        """Register a case study namespace.

        Args:
            name: Case study identifier (e.g., 'ghent', 'household')
            case_uri: Base URI for case study concepts
            entity_uri: Base URI for case study entities (defaults to case_uri)

        Returns:
            CaseStudyNamespaces instance
        """
        ns = CaseStudyNamespaces(
            case=Namespace(case_uri), entities=Namespace(entity_uri or case_uri)
        )
        self._namespaces[name] = ns
        return ns

    def get_namespaces(self, name: str) -> Optional[CaseStudyNamespaces]:
        """Get namespaces for a case study."""
        return self._namespaces.get(name)

    def resolve_curie(self, curie: str) -> Optional[str]:
        """Resolve a CURIE (e.g., 'ghent:DWP1') to full URI.

        Args:
            curie: CURIE in prefix:localName format

        Returns:
            Full URI or None if prefix not found
        """
        if ":" not in curie:
            return None

        prefix, local = curie.split(":", 1)
        ns = self._namespaces.get(prefix)

        if ns:
            if prefix in ["wf", "cap"]:
                return str(ns.wf) + local if prefix == "wf" else str(ns.cap) + local
            elif ns.case:
                return str(ns.case) + local

        return None

    def compact_uri(self, uri: str, preferred_prefix: Optional[str] = None) -> str:
        """Compact a full URI to CURIE format.

        Args:
            uri: Full URI
            preferred_prefix: Preferred prefix to use if multiple match

        Returns:
            CURIE or original URI if no match
        """
        for name, ns in self._namespaces.items():
            for prefix, namespace in ns.to_dict().items():
                ns_str = str(namespace)
                if uri.startswith(ns_str):
                    local = uri[len(ns_str) :]
                    prefix_name = preferred_prefix or name
                    return f"{prefix_name}:{local}"

        return uri


# Global instance
_global_ns_manager: Optional[NamespaceManager] = None


def get_namespace_manager() -> NamespaceManager:
    """Get global namespace manager."""
    global _global_ns_manager
    if _global_ns_manager is None:
        _global_ns_manager = NamespaceManager()
    return _global_ns_manager
