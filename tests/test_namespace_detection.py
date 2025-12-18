"""Tests for ontology namespace detection."""

import sys
from pathlib import Path

import pytest

# Add the scripts directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from generate_docs import OntologyDocGenerator


class TestNamespaceDetection:
    """Test suite for namespace detection logic."""

    def test_uses_default_prefix_from_ontology(self, tmp_path):
        """Test that namespace is extracted from default prefix."""
        # Use the minimal ontology fixture
        fixture_path = Path(__file__).parent / "fixtures" / "minimal_ontology.ttl"
        generator = OntologyDocGenerator(ontology_path=fixture_path)

        assert generator.ontology_namespace == "http://test.example.org/onto#"
        assert generator.ontology_base == "http://test.example.org/onto"

    def test_uses_default_prefix_when_declaration_differs(self):
        """Test that default prefix is used even if declaration URI differs.

        This is a regression test for the examxxxple vs example bug.
        """
        fixture_path = (
            Path(__file__).parent / "fixtures" / "namespace_edge_cases.ttl"
        )
        generator = OntologyDocGenerator(ontology_path=fixture_path)

        # Should use the default prefix, not the declaration URI
        assert generator.ontology_namespace == "http://mismatch.example.org/test#"
        assert generator.ontology_base == "http://mismatch.example.org/test"

    def test_namespace_ends_with_hash(self):
        """Test that namespace always ends with #."""
        fixture_path = Path(__file__).parent / "fixtures" / "minimal_ontology.ttl"
        generator = OntologyDocGenerator(ontology_path=fixture_path)

        assert generator.ontology_namespace.endswith("#")

    def test_base_does_not_end_with_hash(self):
        """Test that base URI does not end with #."""
        fixture_path = Path(__file__).parent / "fixtures" / "minimal_ontology.ttl"
        generator = OntologyDocGenerator(ontology_path=fixture_path)

        assert not generator.ontology_base.endswith("#")

    def test_namespace_extracted_during_load(self):
        """Test that namespace is available after loading ontology."""
        fixture_path = Path(__file__).parent / "fixtures" / "minimal_ontology.ttl"
        generator = OntologyDocGenerator(ontology_path=fixture_path)

        # Namespace should be set immediately after initialization
        assert hasattr(generator, "ontology_namespace")
        assert hasattr(generator, "ontology_base")
        assert generator.ontology_namespace is not None

    def test_handles_missing_ontology_file_gracefully(self, tmp_path):
        """Test that missing ontology file doesn't crash."""
        nonexistent = tmp_path / "nonexistent.ttl"
        generator = OntologyDocGenerator(ontology_path=nonexistent)

        # Should have fallback namespace
        assert generator.ontology_namespace == "http://example.org/waterFRAME#"
        assert generator.ontology_base == "http://example.org/waterFRAME"

    def test_namespace_used_for_entity_links(self):
        """Test that detected namespace is used when generating entity links."""
        fixture_path = Path(__file__).parent / "fixtures" / "minimal_ontology.ttl"
        generator = OntologyDocGenerator(ontology_path=fixture_path)

        # Get entity info
        test_class_uri = "http://test.example.org/onto#TestClass"
        entity_info = generator._get_entity_info(test_class_uri)

        # Generate section content
        content = generator._generate_entity_section(entity_info)

        # Should contain links with the correct namespace
        assert "http://test.example.org/onto#" in content.lower() or \
               "http___test.example.org_onto_" in content.lower()
