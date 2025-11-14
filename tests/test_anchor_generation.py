"""Tests for anchor ID generation and consistency."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from generate_docs import OntologyDocGenerator


class TestAnchorGeneration:
    """Test suite for anchor ID generation."""

    @pytest.fixture
    def generator(self):
        """Create a generator with the minimal ontology."""
        fixture_path = Path(__file__).parent / "fixtures" / "minimal_ontology.ttl"
        return OntologyDocGenerator(ontology_path=fixture_path)

    def test_anchor_id_escapes_special_characters(self, generator):
        """Test that special characters in URIs are escaped in anchor IDs."""
        test_uri = "http://test.example.org/onto#TestClass"
        anchor = generator._get_anchor_id(test_uri)

        # Should replace :, #, / with underscores
        assert ":" not in anchor
        assert "#" not in anchor
        assert "/" not in anchor
        assert anchor == "http___test.example.org_onto_testclass"

    def test_anchor_id_is_lowercase(self, generator):
        """Test that anchor IDs are lowercase for consistency."""
        test_uri = "http://test.example.org/onto#TestClass"
        anchor = generator._get_anchor_id(test_uri)

        assert anchor == anchor.lower()
        assert "testclass" in anchor

    def test_entity_heading_anchor_matches_link_anchor(self, generator):
        """Test that entity heading anchors match the anchors in links.

        This is a critical test - if these don't match, internal links break.
        """
        test_class_uri = "http://test.example.org/onto#TestClass"
        entity_info = generator._get_entity_info(test_class_uri)

        # Generate the section
        content = generator._generate_entity_section(entity_info)

        # Extract the heading anchor
        import re
        heading_match = re.search(r'## \w+ \{#([^}]+)\}', content)
        assert heading_match, "Should find heading with anchor"
        heading_anchor = heading_match.group(1)

        # The heading anchor should match what _get_anchor_id produces
        expected_anchor = generator._get_anchor_id(test_class_uri)
        assert heading_anchor == expected_anchor

    def test_different_uris_produce_different_anchors(self, generator):
        """Test that different URIs produce different anchor IDs."""
        uri1 = "http://test.example.org/onto#TestClass"
        uri2 = "http://test.example.org/onto#SubClass"

        anchor1 = generator._get_anchor_id(uri1)
        anchor2 = generator._get_anchor_id(uri2)

        assert anchor1 != anchor2

    def test_same_uri_produces_same_anchor(self, generator):
        """Test that the same URI always produces the same anchor ID."""
        test_uri = "http://test.example.org/onto#TestClass"

        anchor1 = generator._get_anchor_id(test_uri)
        anchor2 = generator._get_anchor_id(test_uri)

        assert anchor1 == anchor2

    def test_anchor_contains_local_name(self, generator):
        """Test that anchor ID contains the entity's local name."""
        test_uri = "http://test.example.org/onto#TestClass"
        anchor = generator._get_anchor_id(test_uri)

        # Should contain 'testclass' (lowercase)
        assert "testclass" in anchor.lower()

    def test_reconstructed_uri_produces_correct_anchor(self, generator):
        """Test that reconstructing a URI produces the same anchor.

        When we create links, we reconstruct URIs like:
        f"{self.ontology_namespace}{entity_name}"

        This should produce the same anchor as the original entity URI.
        """
        # Original entity URI
        original_uri = "http://test.example.org/onto#TestClass"

        # Reconstructed URI (what we do for links)
        reconstructed = f"{generator.ontology_namespace}TestClass"

        # Both should produce the same anchor
        anchor_original = generator._get_anchor_id(original_uri)
        anchor_reconstructed = generator._get_anchor_id(reconstructed)

        assert anchor_original == anchor_reconstructed

    def test_anchor_in_table_of_contents_matches_heading(self, generator):
        """Test that TOC anchors match the actual heading anchors."""
        # Generate full documentation
        generator.output_dir.mkdir(parents=True, exist_ok=True)
        output_file = generator.generate_all_docs()

        # Read the generated file
        with open(output_file, 'r') as f:
            content = f.read()

        # Extract TOC links
        import re
        toc_links = re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', content)

        # Extract heading anchors
        heading_anchors = re.findall(r'## ([^{]+) \{#([^}]+)\}', content)

        # Each entity in TOC should have a matching heading
        toc_entity_names = {name.strip() for name, _ in toc_links}
        heading_entity_names = {name.strip() for name, _ in heading_anchors}

        # Not all TOC items are entities (e.g., "Table of Contents")
        # But entity names should match
        for name, anchor in toc_links:
            if name == "Table of Contents":
                continue
            # Find corresponding heading
            matching_headings = [
                (h_name, h_anchor) for h_name, h_anchor in heading_anchors
                if h_name.strip() == name.strip()
            ]
            if matching_headings:
                _, heading_anchor = matching_headings[0]
                assert anchor == heading_anchor, \
                    f"TOC anchor #{anchor} should match heading #{heading_anchor} for {name}"
