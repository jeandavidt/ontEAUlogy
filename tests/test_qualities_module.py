"""
Test script for the qualities.ttl module (Water Quality Parameters).

Tests:
1. Loading of qualities module
2. Water quality parameter class existence
3. Water quality requirement class existence
4. SPARQL queries for water quality observations and regulatory limits
"""

from pathlib import Path

try:
    from rdflib import Graph, Namespace, URIRef
    from rdflib.namespace import RDF, RDFS, OWL
    HAS_RDFLIB = True
except ImportError:
    HAS_RDFLIB = False


WF = Namespace("https://ugentbiomath.github.io/waterframe#")


def test_qualities_module_loading():
    """Test that the qualities module loads correctly."""
    print("=" * 60)
    print("TEST: Qualities Module Loading")
    print("=" * 60)
    
    if not HAS_RDFLIB:
        print("SKIPPED: rdflib not installed")
        return False
    
    base_path = Path(__file__).parent.parent / "data" / "ontology"
    g = Graph()
    
    g.parse(str(base_path / "waterframe.ttl"), format="turtle")
    g.parse(str(base_path / "instances" / "ghent_case_study_test.ttl"), format="turtle")
    
    print(f"Loaded {len(g)} triples")
    return True


def test_water_quality_parameters():
    """Test that all required water quality parameter classes exist."""
    print("\n" + "=" * 60)
    print("TEST: Water Quality Parameter Classes")
    print("=" * 60)
    
    if not HAS_RDFLIB:
        print("SKIPPED: rdflib not installed")
        return False
    
    base_path = Path(__file__).parent.parent / "data" / "ontology"
    g = Graph()
    g.parse(str(base_path / "waterframe.ttl"), format="turtle")
    
    required_parameters = [
        WF.WaterQualityParameter,
        WF.BOD,
        WF.COD,
        WF.TSS,
        WF.TDS,
        WF.pH,
        WF.Temperature,
        WF.Turbidity,
        WF.Conductivity,
        WF.DissolvedOxygen,
        WF.TotalNitrogen,
        WF.TotalPhosphorus,
        WF.Ammonia,
        WF.Nitrate,
        WF.Nitrite,
        WF.Orthophosphate,
    ]
    
    print("\nChecking required water quality parameters:")
    all_found = True
    for param in required_parameters:
        found = any(param in s for s in g.subjects(RDF.type, OWL.Class))
        status = "✓" if found else "✗"
        param_name = str(param).split('#')[-1].split('/')[-1]
        print(f"  {status} {param_name}")
        if not found:
            all_found = False
    
    return all_found


def test_water_quality_requirements():
    """Test water quality requirement classes and properties."""
    print("\n" + "=" * 60)
    print("TEST: Water Quality Requirements")
    print("=" * 60)
    
    if not HAS_RDFLIB:
        print("SKIPPED: rdflib not installed")
        return False
    
    base_path = Path(__file__).parent.parent / "data" / "ontology"
    g = Graph()
    g.parse(str(base_path / "waterframe.ttl"), format="turtle")
    
    required_classes = [
        WF.WaterQualityRequirement,
        WF.WaterQualityObservation,
        WF.RegulatoryStandard,
        WF.WaterQualityClass,
        WF.FitForPurpose,
        WF.LimitType,
        WF.MaximumLimit,
        WF.MinimumLimit,
    ]
    
    print("\nChecking required requirement classes:")
    all_found = True
    for cls in required_classes:
        found = any(cls in s for s in g.subjects(RDF.type, OWL.Class))
        status = "✓" if found else "✗"
        cls_name = str(cls).split('#')[-1].split('/')[-1]
        print(f"  {status} {cls_name}")
        if not found:
            all_found = False
    
    return all_found


def test_qualities_sparql_queries():
    """Test SPARQL queries for water quality."""
    print("\n" + "=" * 60)
    print("TEST: SPARQL Queries for Water Quality")
    print("=" * 60)
    
    if not HAS_RDFLIB:
        print("SKIPPED: rdflib not installed")
        return False
    
    base_path = Path(__file__).parent.parent / "data" / "ontology"
    g = Graph()
    g.parse(str(base_path / "waterframe.ttl"), format="turtle")
    g.parse(str(base_path / "instances" / "ghent_case_study_test.ttl"), format="turtle")
    
    # Test: Find water quality observations
    print("\nCQ10 - Water quality observations:")
    query_obs = """
    PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
    SELECT ?obs ?param ?value WHERE {
        ?obs wf:observedParameter ?param ;
             wf:observedValue ?value .
    }
    """
    results = list(g.query(query_obs))
    print(f"  Found {len(results)} observations")
    for row in results:
        param_name = str(row[1]).split('#')[-1].split('/')[-1]
        print(f"    - {param_name}: {row[2]}")
    
    # Test: Find regulatory limits
    print("\nCQ11 - Regulatory limits:")
    query_limits = """
    PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
    SELECT ?req ?param ?limit ?type WHERE {
        ?req wf:hasWaterQualityParameter ?param ;
             wf:hasLimitValue ?limit ;
             wf:hasLimitType ?type .
    }
    """
    results = list(g.query(query_limits))
    print(f"  Found {len(results)} regulatory requirements")
    for row in results:
        param_name = str(row[1]).split('#')[-1].split('/')[-1]
        print(f"    - {param_name}: {row[2]} ({row[3].split('#')[-1]})")
    
    return True


def run_all_tests():
    """Run all qualities module tests."""
    print("\n" + "=" * 60)
    print("QUALITIES MODULE TEST SUITE")
    print("=" * 60)
    
    results = {}
    results["loading"] = test_qualities_module_loading()
    results["parameters"] = test_water_quality_parameters()
    results["requirements"] = test_water_quality_requirements()
    results["sparql"] = test_qualities_sparql_queries()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASSED" if result else "FAILED"
        print(f"  {test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
