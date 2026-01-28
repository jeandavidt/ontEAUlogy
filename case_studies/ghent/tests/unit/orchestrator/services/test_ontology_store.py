"""Unit tests for the OntologyStore service."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from rdflib import Graph, URIRef, Namespace
from ghent_water.orchestrator.services.ontology_store import OntologyStore

@pytest.fixture
def mock_ontology_store():
    """Create an OntologyStore with mocked paths."""
    with patch("ghent_water.orchestrator.services.ontology_store.Path") as mock_path:
        # Configure mock paths to avoid hitting real disk during initialization
        store = OntologyStore(
            ontology_base_path="/mock/base",
            case_study_data_path="/mock/case"
        )
        return store

@pytest.mark.asyncio
async def test_load_ontology_caching():
    """Test that ontology is cached and not reloaded unless forced."""
    store = OntologyStore()
    
    with patch.object(Graph, "parse") as mock_parse:
        with patch.object(Path, "exists", return_value=True):
            with patch.object(Path, "glob", return_value=[]):
                # First load
                success = await store.load_ontology()
                assert success is True
                assert store.is_loaded() is True
                assert mock_parse.call_count > 0
                
                initial_call_count = mock_parse.call_count
                
                # Second load (should return early)
                success = await store.load_ontology()
                assert success is True
                assert mock_parse.call_count == initial_call_count
                
                # Forced reload
                success = await store.load_ontology(force=True)
                assert success is True
                assert mock_parse.call_count > initial_call_count

def test_get_entity_not_loaded():
    """Test get_entity when ontology is not loaded."""
    store = OntologyStore()
    entity = store.get_entity("https://example.org/entity1")
    assert entity is None

def test_get_entity_loaded():
    """Test basic entity retrieval."""
    store = OntologyStore()
    store._graph = Graph()
    store._loaded = True
    
    ghent = Namespace("https://w3id.org/waterframe/case/ghent/")
    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    
    store._graph.add((ghent.MyEntity, rdf.type, URIRef("https://example.org/TestType")))
    store._graph.add((ghent. MyEntity, rdfs.label, URIRef("My Label")))
    
    entity = store.get_entity(str(ghent.MyEntity))
    assert entity is not None
    assert entity["uri"] == str(ghent.MyEntity)
    assert "TestType" in str(entity["type"])
