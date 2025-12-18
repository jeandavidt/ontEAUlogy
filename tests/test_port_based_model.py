#!/usr/bin/env python3
"""
Tests for port-based water system modeling
Validates that the port-based approach enables answering key competency questions
"""

import pytest
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS
from pathlib import Path


@pytest.fixture
def port_based_graph():
    """Load the port-based ontology and instance data"""
    g = Graph()

    base_dir = Path(__file__).parent.parent

    # Load core modules
    modules_dir = base_dir / "data" / "ontology" / "modules" / "core"
    for module_file in ["material_entities.ttl", "properties.ttl"]:
        module_path = modules_dir / module_file
        if module_path.exists():
            g.parse(str(module_path), format="turtle")

    # Load port-based instances
    instances_file = (
        base_dir / "data" / "ontology" / "instances" / "household_case1_port_based.ttl"
    )
    if instances_file.exists():
        g.parse(str(instances_file), format="turtle")

    return g


def test_port_classes_exist(port_based_graph):
    """Test that Port classes are defined"""
    wf = Namespace("https://ugentbiomath.github.io/waterframe#")

    # Check Port classes are defined
    port_classes = [wf.Port, wf.InputPort, wf.OutputPort]
    for port_class in port_classes:
        assert (port_class, RDFS.subClassOf, None) in port_based_graph or \
               (port_class, RDF.type, None) in port_based_graph, \
               f"{port_class} should be defined"


def test_components_have_ports(port_based_graph):
    """Test that components have input and output ports"""
    wf = Namespace("https://ugentbiomath.github.io/waterframe#")
    housecase1 = Namespace("https://ugentbiomath.github.io/ontology/index.ttl#")

    # Query for components with ports (using actual properties, not inferred hasPort)
    query = """
    PREFIX wf: <https://ugentbiomath.github.io/waterframe#>

    SELECT ?component (COUNT(DISTINCT ?port) AS ?portCount)
    WHERE {
        { ?component wf:hasInputPort ?port . }
        UNION
        { ?component wf:hasOutputPort ?port . }
    }
    GROUP BY ?component
    """

    results = list(port_based_graph.query(query))
    assert len(results) > 0, "Should find components with ports"

    # Check that some components have multiple ports (e.g., MBR, storage tanks)
    multi_port_components = [row for row in results if int(row[1]) > 1]
    assert len(multi_port_components) > 0, "Some components should have multiple ports"


def test_cq2_flow_connections(port_based_graph):
    """Test CQ2: What flows connect Node A to Node B?"""
    query = """
    PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
    PREFIX housecase1: <https://ugentbiomath.github.io/ontology/index.ttl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?sourceComponent ?targetComponent
    WHERE {
        ?sourceComponent wf:hasOutputPort ?outPort .
        ?outPort wf:flowsTo ?inPort .
        ?targetComponent wf:hasInputPort ?inPort .
    }
    """

    results = list(port_based_graph.query(query))
    assert len(results) > 0, "Should find flow connections between components"

    # Verify we can find specific connections (e.g., greywater to MBR)
    found_connections = [(str(row[0]).split('#')[-1], str(row[1]).split('#')[-1])
                        for row in results]

    # Should have connection from bath to MBR
    mbr_inputs = [conn for conn in found_connections
                  if 'Membrane_bioreactor' in conn[1]]
    assert len(mbr_inputs) > 0, "Should find flows to MBR"


def test_cq18_model_inputs(port_based_graph):
    """Test CQ18: What are the input variables for Model M?
    (represented as input ports for a component)
    """
    query = """
    PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
    PREFIX housecase1: <https://ugentbiomath.github.io/ontology/index.ttl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?inputPort ?flowType
    WHERE {
        # MBR as example component
        housecase1:Membrane_bioreactor wf:hasInputPort ?inputPort .
        OPTIONAL { ?inputPort wf:hasFlowType ?flowType }
    }
    """

    results = list(port_based_graph.query(query))
    assert len(results) > 0, "MBR should have input ports"

    # MBR should have multiple greywater inputs
    assert len(results) >= 3, f"MBR should have at least 3 input ports, found {len(results)}"


def test_cq19_model_outputs(port_based_graph):
    """Test CQ19: What are the output variables for Model M?
    (represented as output ports for a component)
    """
    query = """
    PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
    PREFIX housecase1: <https://ugentbiomath.github.io/ontology/index.ttl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?outputPort ?flowType
    WHERE {
        # MBR as example component
        housecase1:Membrane_bioreactor wf:hasOutputPort ?outputPort .
        OPTIONAL { ?outputPort wf:hasFlowType ?flowType }
    }
    """

    results = list(port_based_graph.query(query))
    assert len(results) > 0, "MBR should have output ports"


def test_multi_input_treatment_unit(port_based_graph):
    """Test that treatment units with multiple inputs are correctly modeled"""
    query = """
    PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
    PREFIX housecase1: <https://ugentbiomath.github.io/ontology/index.ttl#>

    SELECT ?unit ?inputPort ?upstreamComponent
    WHERE {
        ?unit a wf:MembraneBioreactorUnit .
        ?unit wf:hasInputPort ?inputPort .

        # Find upstream components
        OPTIONAL {
            ?upstreamPort wf:flowsTo ?inputPort .
            ?upstreamComponent wf:hasOutputPort ?upstreamPort .
        }
    }
    """

    results = list(port_based_graph.query(query))
    assert len(results) > 0, "MBR should have input connections"

    # Count unique upstream components
    upstream_components = set(str(row[2]).split('#')[-1] for row in results if row[2])
    assert len(upstream_components) > 1, \
        f"MBR should receive from multiple sources, found {len(upstream_components)}"


def test_multi_output_components(port_based_graph):
    """Test components with multiple output ports (e.g., RO with permeate splits)"""
    query = """
    PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
    PREFIX housecase1: <https://ugentbiomath.github.io/ontology/index.ttl#>

    SELECT ?component (COUNT(?outputPort) AS ?outputCount)
    WHERE {
        ?component wf:hasOutputPort ?outputPort .
    }
    GROUP BY ?component
    HAVING (COUNT(?outputPort) > 1)
    """

    results = list(port_based_graph.query(query))
    assert len(results) > 0, "Should find components with multiple outputs"


def test_flow_types_at_ports(port_based_graph):
    """Test that flow types are properly assigned to ports"""
    query = """
    PREFIX wf: <https://ugentbiomath.github.io/waterframe#>

    SELECT ?port ?flowType
    WHERE {
        ?port a ?portType .
        FILTER(?portType IN (wf:InputPort, wf:OutputPort))
        ?port wf:hasFlowType ?flowType .
    }
    """

    results = list(port_based_graph.query(query))
    assert len(results) > 0, "Ports should have flow types assigned"

    # Check that we have different flow types
    flow_types = set(str(row[1]).split('#')[-1] for row in results)
    assert 'GreywaterFlow' in flow_types, "Should have greywater flows"
    assert 'RainwaterFlow' in flow_types or 'ReclaimedWaterFlow' in flow_types, \
        "Should have rainwater or reclaimed water flows"


def test_port_properties_defined(port_based_graph):
    """Test that port structural properties are defined"""
    wf = Namespace("https://ugentbiomath.github.io/waterframe#")

    port_properties = [
        wf.hasInputPort,
        wf.hasOutputPort,
        wf.hasPort,
        wf.flowsTo,
        wf.receivesFlowFrom
    ]

    for prop in port_properties:
        # Check property is used or defined
        assert (None, prop, None) in port_based_graph or \
               (prop, None, None) in port_based_graph, \
               f"Property {prop} should be defined or used"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
