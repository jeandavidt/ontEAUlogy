"""Parse Turtle / JSON-LD input to plain dict."""
from typing import Dict

from rdflib import Graph
from rdflib.namespace import XSD


def parse_turtle_to_dict(body: bytes, field_mapping: Dict[str, str] = None) -> Dict:
    """Parse Turtle-encoded request body into a plain Python dict.

    Strategy: SPARQL query for wf:parameterName / rdf:value pairs,
    then fallback triple scan for typed literals.
    """
    g = Graph()
    g.parse(data=body.decode(), format="turtle")

    query = """
    PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?name ?value WHERE {
        ?input wf:parameterName ?name ;
               rdf:value ?value .
    }
    """
    result = {}
    for row in g.query(query):
        name = str(row.name)
        try:
            result[name] = float(row.value)
        except (ValueError, TypeError):
            result[name] = str(row.value)

    if not result:
        for s, p, o in g:
            local = str(p).split("#")[-1].split("/")[-1]
            if hasattr(o, "datatype") and o.datatype in (XSD.float, XSD.double, XSD.decimal):
                result[local] = float(o)
            elif hasattr(o, "datatype") and o.datatype is not None:
                try:
                    result[local] = float(o)
                except (ValueError, TypeError):
                    result[local] = str(o)

    return result


def parse_jsonld_to_dict(body: bytes, field_mapping: Dict[str, str] = None) -> Dict:
    """Parse JSON-LD encoded request body into a plain Python dict."""
    g = Graph()
    g.parse(data=body.decode(), format="json-ld")
    return parse_turtle_to_dict(g.serialize(format="turtle").encode(), field_mapping)
