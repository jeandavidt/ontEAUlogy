"""Serialize simulation outputs to Turtle / JSON-LD."""
from typing import Dict, Optional
from uuid import uuid4

from rdflib import Graph, Literal, URIRef, BNode
from rdflib.namespace import RDF, XSD

from .namespaces import WF, CASE, HC1

_DEFAULT_SCENARIO_IRI = str(HC1) + "Baseline_Scenario"


def serialize_outputs_to_turtle(
    outputs: Dict,
    model_id: str,
    var_iris: Dict,
    simulation_mode: str = "steady_state",
    scenario_iri: Optional[str] = None,
    run_id: Optional[str] = None,
) -> str:
    """Serialize a simulation output dict to Turtle RDF string."""
    g = Graph()
    g.bind("wf", WF)
    g.bind("case", CASE)
    g.bind("hc1", HC1)
    g.bind("xsd", XSD)

    run_id = run_id or uuid4().hex[:8]
    run_uri = CASE[f"{model_id}_Run_{run_id}"]
    scenario_uri = URIRef(scenario_iri or _DEFAULT_SCENARIO_IRI)
    model_uri = CASE[f"{model_id}_Model"]

    g.add((run_uri, RDF.type, WF.SimulationRun))
    g.add((run_uri, WF.hasSimulationMode, Literal(simulation_mode)))
    g.add((run_uri, WF.inScenario, scenario_uri))
    g.add((run_uri, WF.producedBy, model_uri))

    for field, value in outputs.items():
        if isinstance(value, (list, dict)):
            continue  # skip dynamic arrays
        bnode = BNode()
        g.add((run_uri, WF.hasOutput, bnode))
        g.add((bnode, RDF.type, WF.StateVariable))
        g.add((bnode, WF.parameterName, Literal(field)))
        if field in var_iris:
            g.add((bnode, RDF.type, URIRef(var_iris[field])))
        g.add((bnode, RDF.value, Literal(float(value), datatype=XSD.float)))

    return g.serialize(format="turtle")


def params_to_turtle(model_id: str, params_dict: Dict) -> str:
    """Serialize calibrated parameters to Turtle."""
    g = Graph()
    g.bind("wf", WF)
    g.bind("case", CASE)
    g.bind("xsd", XSD)

    model_uri = CASE[f"{model_id}_Model"]
    for name, value in params_dict.items():
        bnode = BNode()
        g.add((model_uri, WF.hasParameter, bnode))
        g.add((bnode, RDF.type, WF.Parameter))
        g.add((bnode, WF.parameterName, Literal(name)))
        g.add((bnode, RDF.value, Literal(float(value), datatype=XSD.float)))

    return g.serialize(format="turtle")
