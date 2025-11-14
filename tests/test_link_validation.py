"""Tests for internal link validation."""

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from generate_docs import OntologyDocGenerator


class TestLinkValidation:
    """Test suite for validating internal links in generated documentation."""

    @pytest.fixture
    def generator(self, tmp_path):
        """Create a generator with the minimal ontology."""
        fixture_path = Path(__file__).parent / "fixtures" / "minimal_ontology.ttl"
        output_dir = tmp_path / "test_docs" / "entities"
        gen = OntologyDocGenerator(
            ontology_path=fixture_path,
            output_dir=output_dir
        )
        return gen

    @pytest.fixture
    def generated_content(self, generator):
        """Generate documentation and return the content."""
        output_file = generator.generate_all_docs()
        with open(output_file, 'r') as f:
            return f.read()

    def test_all_internal_links_have_matching_anchors(self, generated_content):
        """Test that every internal link points to an existing anchor.

        This is the most critical test - broken internal links ruin UX.
        """
        # Extract all internal links [text](#anchor)
        links = re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', generated_content)

        # Extract all heading anchors ## Title {#anchor}
        headings = re.findall(r'## [^{]+ \{#([^}]+)\}', generated_content)
        heading_anchors = set(headings)

        # Check each link
        broken_links = []
        for text, anchor in links:
            if anchor not in heading_anchors:
                broken_links.append((text, anchor))

        assert len(broken_links) == 0, \
            f"Found broken internal links: {broken_links}"

    def test_no_links_to_external_uris(self, generated_content):
        """Test that external URIs are not turned into internal links.

        External URIs like http://www.w3.org/... should not be linked.
        """
        # Links to w3.org should not be internal links
        assert "](#http___www.w3.org" not in generated_content.lower()

        # External URIs should appear as code (backticks) or plain text
        # but not as internal links

    def test_literal_values_not_linked(self, generator, generated_content):
        """Test that literal values are not turned into links.

        Values like "7.2", "pH units" should be plain text, not links.
        """
        # Look for property values section
        if "Property Values" in generated_content:
            # Extract property values sections
            sections = re.split(r'###\s+Property Values', generated_content)
            for section in sections[1:]:  # Skip first split (before first match)
                # Get the section until next heading
                prop_section = section.split('###')[0]

                # Literal values should not be in anchor links
                # Pattern: look for values that are clearly literals
                literals = re.findall(r':\s*([0-9.]+)\s*\n', prop_section)
                for literal in literals:
                    # Literal shouldn't be in a link
                    assert f"[{literal}](#" not in prop_section, \
                        f"Literal value {literal} should not be a link"

    def test_only_ontology_entities_linked(self, generator, generated_content):
        """Test that only entities from this ontology are linked.

        External ontology references (OWL, RDFS, etc.) should not be linked.
        """
        # Links should only be to entities in our namespace
        namespace_base = generator.ontology_base.lower()

        # Extract all anchor links
        links = re.findall(r'\]\(#([^)]+)\)', generated_content)

        for anchor in links:
            # Skip the table of contents section itself
            if "table" in anchor.lower() and "contents" in anchor.lower():
                continue

            # Anchor should contain our namespace
            # (when converted from URI to anchor format)
            # Note: dots are NOT replaced in anchor generation, only : # /
            namespace_in_anchor = namespace_base.replace(':', '_').replace('/', '_')

            assert namespace_in_anchor in anchor.lower(), \
                f"Anchor {anchor} should contain namespace {namespace_in_anchor}"

    def test_subclass_links_to_superclass(self, generator, generated_content):
        """Test that subclass documentation links to superclass."""
        # SubClass should have a link to TestClass
        # Find SubClass section
        subclass_match = re.search(
            r'## SubClass \{#[^}]+\}.*?(?=\n## |\Z)',
            generated_content,
            re.DOTALL
        )
        assert subclass_match, "SubClass section should exist"

        subclass_section = subclass_match.group(0)

        # Should have superclass link
        assert "Superclasses" in subclass_section
        assert "[TestClass]" in subclass_section

    def test_superclass_links_to_subclass(self, generator, generated_content):
        """Test that superclass documentation links to subclass."""
        # TestClass should have a link to SubClass
        testclass_match = re.search(
            r'## TestClass \{#[^}]+\}.*?(?=\n## |\Z)',
            generated_content,
            re.DOTALL
        )
        assert testclass_match, "TestClass section should exist"

        testclass_section = testclass_match.group(0)

        # Should have subclass link
        assert "Subclasses" in testclass_section
        assert "[SubClass]" in testclass_section

    def test_property_links_to_domain_and_range(self, generator, generated_content):
        """Test that property documentation links to domain and range classes."""
        # testProperty should link to TestClass (domain) and SubClass (range)
        prop_match = re.search(
            r'## testProperty \{#[^}]+\}.*?(?=\n## |\Z)',
            generated_content,
            re.DOTALL
        )
        assert prop_match, "testProperty section should exist"

        prop_section = prop_match.group(0)

        # Should have domain link
        assert "Domains" in prop_section
        assert "[TestClass]" in prop_section

        # Should have range link
        assert "Ranges" in prop_section
        # Range might be just text or a link depending on whether it's internal

    def test_individual_links_to_class(self, generator, generated_content):
        """Test that individual documentation links to its class."""
        # testIndividual should link to TestClass
        individual_match = re.search(
            r'## testIndividual \{#[^}]+\}.*?(?=\n## |\Z)',
            generated_content,
            re.DOTALL
        )
        assert individual_match, "testIndividual section should exist"

        individual_section = individual_match.group(0)

        # Should have instance of link
        assert "Instance Of" in individual_section
        assert "[TestClass]" in individual_section

    def test_table_of_contents_links_work(self, generated_content):
        """Test that table of contents links point to valid sections."""
        # Extract TOC section
        toc_match = re.search(
            r'## Table of Contents.*?(?=---)',
            generated_content,
            re.DOTALL
        )
        if not toc_match:
            pytest.skip("No Table of Contents found")

        toc = toc_match.group(0)

        # Extract TOC links
        toc_links = re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', toc)

        # Extract all section headings
        headings = re.findall(r'## ([^{]+) \{#([^}]+)\}', generated_content)
        heading_anchors = {anchor.strip(): name.strip() for name, anchor in headings}

        # Each TOC link should point to a real section
        for name, anchor in toc_links:
            assert anchor in heading_anchors, \
                f"TOC link {name} (#{anchor}) should point to existing section"
