#!/usr/bin/env python3
"""
Ontology consistency test using pytest
Tests that the ontology loads and can be reasoned over
"""

import pytest
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS, OWL
from pathlib import Path


@pytest.fixture
def ontology_graph():
    """Load the ontology for testing"""
    g = Graph()

    base_dir = Path(__file__).parent.parent

    # Load main ontology (this imports all modules)
    main_ontology_file = base_dir / "data" / "ontology" / "waterframe.ttl"
    if main_ontology_file.exists():
        g.parse(str(main_ontology_file), format="turtle")

        # Load core modules explicitly (RDFLib doesn't auto-download imports)
        modules_dir = base_dir / "data" / "ontology" / "modules" / "core"
        core_modules = ["material_entities.ttl", "properties.ttl"]

        for module_file in core_modules:
            module_path = modules_dir / module_file
            if module_path.exists():
                g.parse(str(module_path), format="turtle")

    # Load instances
    instances_file = (
        base_dir / "data" / "ontology" / "instances" / "household_case1.ttl"
    )
    if instances_file.exists():
        g.parse(str(instances_file), format="turtle")

    return g


def test_ontology_loads(ontology_graph):
    """Test that ontology loads without errors"""
    assert len(ontology_graph) > 0, "Ontology should contain triples"
    # Note: Triple count will change as modules are developed
    # Currently expecting ~310 triples after port-based refactoring
    assert len(ontology_graph) >= 300, (
        f"Expected at least 300 triples, got {len(ontology_graph)}"
    )


def test_bfo_alignment(ontology_graph):
    """Test that classes are properly aligned with BFO"""
    wf = Namespace("https://ugentbiomath.github.io/waterframe#")
    bfo = Namespace("http://purl.obolibrary.org/obo/")

    # Check that WaterSystemComponent subclasses MaterialEntity
    water_system_component = wf.WaterSystemComponent
    material_entity = bfo.BFO_0000040  # MaterialEntity

    # Verify the subclass relationship exists
    assert (
        water_system_component,
        RDFS.subClassOf,
        material_entity,
    ) in ontology_graph, (
        "WaterSystemComponent should be a subclass of BFO MaterialEntity"
    )


def test_instance_classification(ontology_graph):
    """Test that instances are properly classified"""
    wf = Namespace("https://ugentbiomath.github.io/waterframe#")

    # Check that we have the expected number of WaterSystemComponent instances
    water_system_components = list(
        ontology_graph.subjects(
            RDF.type,
            lambda x: str(x).startswith(wf)
            and ontology_graph.value(x, RDFS.subClassOf) is not None,
        )
    )

    # More direct check: count instances that have types that are subclasses of WaterSystemComponent
    component_instances = []
    for s, o in ontology_graph.subject_objects(RDF.type):
        if str(o).startswith(wf) and o != wf.WaterSystemComponent:
            # Check if this type is a subclass of WaterSystemComponent
            if ontology_graph.value(
                o, RDFS.subClassOf
            ) == wf.WaterSystemComponent or any(
                ontology_graph.value(ancestor, RDFS.subClassOf)
                == wf.WaterSystemComponent
                for ancestor in ontology_graph.transitive_objects(o, RDFS.subClassOf)
            ):
                component_instances.append(s)

    assert len(component_instances) == 16, (
        f"Expected 16 component instances, got {len(component_instances)}"
    )


def test_cq1_answerable(ontology_graph):
    """Test that CQ1 query can be answered"""
    wf = Namespace("https://ugentbiomath.github.io/waterframe#")

    # Execute CQ1 query
    query = """
    PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?node ?nodeType
    WHERE {
        ?node rdf:type/rdfs:subClassOf* wf:WaterSystemComponent .
        ?node rdf:type ?nodeType .
        FILTER(?nodeType != wf:WaterSystemComponent)
    }
    """

    results = list(ontology_graph.query(query))
    assert len(results) == 16, f"CQ1 should return 16 nodes, got {len(results)}"

    # Check we have different types
    node_types = set(str(row[1]).split("#")[-1] for row in results)
    assert len(node_types) >= 8, (
        f"Expected at least 8 different node types, got {len(node_types)}"
    )


def test_no_ontology_errors(ontology_graph):
    """Test for common ontology modeling errors"""
    # Check for undefined classes being used in rdf:type
    defined_classes = set(ontology_graph.subjects(RDF.type, OWL.Class))
    defined_classes.update(ontology_graph.subjects(RDFS.subClassOf, None))

    undefined_usage = []
    for s, o in ontology_graph.subject_objects(RDF.type):
        if (
            o != OWL.Class
            and o not in defined_classes
            and str(o).startswith("https://ugentbiomath.github.io/waterframe")
        ):
            undefined_usage.append((s, o))

    assert len(undefined_usage) == 0, (
        f"Found {len(undefined_usage)} uses of undefined classes"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
