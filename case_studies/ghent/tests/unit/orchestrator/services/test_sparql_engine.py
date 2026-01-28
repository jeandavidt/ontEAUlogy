# tests/unit/orchestrator/services/test_sparql_engine.py

import pytest
from ghent_water.orchestrator.services.sparql_engine import SparqlEngine
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS


@pytest.fixture
def sample_graph():
    """Create a sample RDF graph for testing."""
    g = Graph()
    wf = Namespace("https://w3id.org/waterframe/")
    g.bind("wf", wf)

    # Add test data
    g.add((wf.DWP1, RDF.type, wf.DrinkingWaterPlant))
    g.add((wf.DWP1, RDFS.label, Literal("DWP1")))
    g.add((wf.DWP1, wf.hasCapacity, Literal(2000)))

    return g


@pytest.fixture
def engine(sample_graph):
    """Create SPARQL engine with test graph."""
    # The SparqlEngine expects a graph to be set, so we pass it here
    engine = SparqlEngine(sample_graph)
    return engine


def test_execute_simple_select_query(engine):
    """Test executing a basic SELECT query."""
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX wf: <https://w3id.org/waterframe/>
    
    SELECT ?plant WHERE {
        ?plant rdf:type wf:DrinkingWaterPlant .
    }
    """

    result = engine.execute_query(query, format="json")

    assert result["format"] == "json"
    assert "results" in result
    assert "bindings" in result["results"]
    assert len(result["results"]["bindings"]) > 0
    assert result["query_time_ms"] >= 0


def test_execute_query_with_filter(engine):
    """Test query with FILTER clause."""
    query = """
    PREFIX wf: <https://w3id.org/waterframe/>
    
    SELECT ?plant ?capacity WHERE {
        ?plant wf:hasCapacity ?capacity .
        FILTER(?capacity > 1500)
    }
    """

    result = engine.execute_query(query)
    bindings = result["results"]["bindings"]

    assert len(bindings) > 0
    for binding in bindings:
        assert int(binding["capacity"]["value"]) > 1500


def test_execute_query_no_graph(monkeypatch):
    """Test error handling when no graph is set."""
    engine = SparqlEngine()

    def mock_is_loaded():
        return False

    monkeypatch.setattr(
        "ghent_water.orchestrator.services.ontology_store.ontology_store.is_loaded",
        mock_is_loaded,
    )

    with pytest.raises(RuntimeError, match="No graph set"):
        engine.execute_query("SELECT * WHERE { ?s ?p ?o }")


def test_format_results_csv(engine):
    """Test CSV formatting of query results."""
    query = "SELECT * WHERE { ?s ?p ?o } LIMIT 5"
    result = engine.execute_query(query, format="csv")

    assert result["format"] == "csv"
    assert isinstance(result["results"], str)
    assert "\n" in result["results"]  # Contains rows


def test_validate_query_syntax(engine):
    """Test query validation."""
    # The SparqlEngine's validate_query method is expected to return a dictionary
    # indicating validity and any errors.
    valid_query = "SELECT ?s WHERE { ?s ?p ?o }"
    invalid_query = "INVALID SPARQL SYNTAX"

    valid_result = engine.validate_query(valid_query)
    assert valid_result["valid"] is True
    assert valid_result["error"] is None

    invalid_result = engine.validate_query(invalid_query)
    assert invalid_result["valid"] is False
    assert invalid_result["error"] is not None
