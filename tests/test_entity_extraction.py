"""Tests for entity information extraction."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from generate_docs import OntologyDocGenerator


class TestEntityExtraction:
    """Test suite for entity information extraction."""

    @pytest.fixture
    def generator(self):
        """Create a generator with the minimal ontology."""
        fixture_path = Path(__file__).parent / "fixtures" / "minimal_ontology.ttl"
        return OntologyDocGenerator(ontology_path=fixture_path)

    def test_all_classes_are_found(self, generator):
        """Test that all OWL classes in the ontology are found."""
        from rdflib.namespace import RDF, OWL

        # Count classes in the graph
        expected_classes = set(generator.graph.subjects(RDF.type, OWL.Class))

        # Generate docs and check they're all included
        generator.output_dir.mkdir(parents=True, exist_ok=True)
        output_file = generator.generate_all_docs()

        with open(output_file, 'r') as f:
            content = f.read()

        # Check each class appears in the documentation
        for class_uri in expected_classes:
            local_name = generator._get_local_name(class_uri)
            assert local_name in content, \
                f"Class {local_name} should appear in documentation"

    def test_all_properties_are_found(self, generator):
        """Test that all properties in the ontology are found."""
        from rdflib.namespace import RDF, OWL

        # Count properties
        obj_props = set(generator.graph.subjects(RDF.type, OWL.ObjectProperty))
        data_props = set(generator.graph.subjects(RDF.type, OWL.DatatypeProperty))
        all_props = obj_props | data_props

        # Generate docs
        generator.output_dir.mkdir(parents=True, exist_ok=True)
        output_file = generator.generate_all_docs()

        with open(output_file, 'r') as f:
            content = f.read()

        # Check each property appears
        for prop_uri in all_props:
            local_name = generator._get_local_name(prop_uri)
            assert local_name in content, \
                f"Property {local_name} should appear in documentation"

    def test_all_individuals_are_found(self, generator):
        """Test that all named individuals are found."""
        from rdflib.namespace import RDF, OWL

        individuals = set(
            generator.graph.subjects(RDF.type, OWL.NamedIndividual)
        )

        # Generate docs
        generator.output_dir.mkdir(parents=True, exist_ok=True)
        output_file = generator.generate_all_docs()

        with open(output_file, 'r') as f:
            content = f.read()

        for individual_uri in individuals:
            local_name = generator._get_local_name(individual_uri)
            assert local_name in content, \
                f"Individual {local_name} should appear in documentation"

    def test_entity_has_label(self, generator):
        """Test that entity information includes labels."""
        test_class_uri = "http://test.example.org/onto#TestClass"
        entity_info = generator._get_entity_info(test_class_uri)

        assert 'labels' in entity_info
        assert len(entity_info['labels']) > 0
        assert "Test Class" in entity_info['labels']

    def test_entity_has_description(self, generator):
        """Test that entity information includes descriptions/comments."""
        test_class_uri = "http://test.example.org/onto#TestClass"
        entity_info = generator._get_entity_info(test_class_uri)

        assert 'descriptions' in entity_info
        assert len(entity_info['descriptions']) > 0

    def test_class_has_subclasses(self, generator):
        """Test that class information includes subclasses."""
        test_class_uri = "http://test.example.org/onto#TestClass"
        entity_info = generator._get_entity_info(test_class_uri)

        assert 'subclasses' in entity_info
        # TestClass has SubClass as a subclass
        assert 'SubClass' in entity_info['subclasses']

    def test_subclass_has_superclass(self, generator):
        """Test that subclass information includes superclasses."""
        subclass_uri = "http://test.example.org/onto#SubClass"
        entity_info = generator._get_entity_info(subclass_uri)

        assert 'superclasses' in entity_info
        # SubClass has TestClass as a superclass
        assert 'TestClass' in entity_info['superclasses']

    def test_property_has_domain(self, generator):
        """Test that property information includes domain."""
        prop_uri = "http://test.example.org/onto#testProperty"
        entity_info = generator._get_entity_info(prop_uri)

        assert 'domains' in entity_info
        assert 'TestClass' in entity_info['domains']

    def test_property_has_range(self, generator):
        """Test that property information includes range."""
        prop_uri = "http://test.example.org/onto#testProperty"
        entity_info = generator._get_entity_info(prop_uri)

        assert 'ranges' in entity_info
        assert 'SubClass' in entity_info['ranges']

    def test_individual_has_type(self, generator):
        """Test that individual information includes its class."""
        individual_uri = "http://test.example.org/onto#testIndividual"
        entity_info = generator._get_entity_info(individual_uri)

        assert 'instance_of' in entity_info
        assert 'TestClass' in entity_info['instance_of']

    def test_individual_has_property_values(self, generator):
        """Test that individual information includes property values."""
        individual_uri = "http://test.example.org/onto#testIndividual"
        entity_info = generator._get_entity_info(individual_uri)

        assert 'property_values' in entity_info
        assert len(entity_info['property_values']) > 0

        # Should have testProperty value
        prop_names = [pv['property'] for pv in entity_info['property_values']]
        assert 'testProperty' in prop_names

    def test_local_name_extraction(self, generator):
        """Test that local names are correctly extracted from URIs."""
        test_cases = [
            ("http://test.example.org/onto#TestClass", "TestClass"),
            ("http://test.example.org/onto#testProperty", "testProperty"),
            ("http://www.w3.org/2002/07/owl#Class", "Class"),
        ]

        for uri, expected_name in test_cases:
            from rdflib import URIRef
            local_name = generator._get_local_name(URIRef(uri))
            assert local_name == expected_name, \
                f"Local name of {uri} should be {expected_name}, got {local_name}"

    def test_entity_count_is_accurate(self, generator):
        """Test that the total entity count matches what's in the graph."""
        from rdflib.namespace import RDF, OWL

        classes = len(list(generator.graph.subjects(RDF.type, OWL.Class)))
        obj_props = len(
            list(generator.graph.subjects(RDF.type, OWL.ObjectProperty))
        )
        data_props = len(
            list(generator.graph.subjects(RDF.type, OWL.DatatypeProperty))
        )
        individuals = len(
            list(generator.graph.subjects(RDF.type, OWL.NamedIndividual))
        )

        total_expected = classes + obj_props + data_props + individuals

        # Generate index and check counts
        generator.output_dir.mkdir(parents=True, exist_ok=True)
        index_file = generator.generate_index()

        with open(index_file, 'r') as f:
            content = f.read()

        # Check that counts are mentioned
        assert f"Classes:** {classes}" in content
        assert f"Object Properties:** {obj_props}" in content
        assert f"Total Entities:** {total_expected}" in content
