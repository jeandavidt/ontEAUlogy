"""Test SOSA/SSN against waterFRAME competency questions."""

from pathlib import Path
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS

# Define namespaces
SOSA = Namespace("http://www.w3.org/ns/sosa/")
SSN = Namespace("http://www.w3.org/ns/ssn/")
EX = Namespace("http://example.org/waterFRAME/")

def load_test_data():
    """Load SOSA/SSN ontologies and test data."""
    base_path = Path(__file__).parent

    g = Graph()
    g.bind("sosa", SOSA)
    g.bind("ssn", SSN)
    g.bind("", EX)

    # Load ontologies
    g.parse(base_path / "sosa_updated.ttl", format="turtle")
    g.parse(base_path / "ssn.rdf", format="xml")

    # Load test data
    g.parse(base_path / "water_quality_test_data.ttl", format="turtle")

    print(f"Loaded {len(g)} triples\n")
    return g

def test_query(g: Graph, cq_number: str, description: str, query: str, expected_result: str):
    """Execute a SPARQL query and report results."""
    print("=" * 80)
    print(f"CQ{cq_number}: {description}")
    print("-" * 80)
    print("Query:")
    print(query)
    print("\nResults:")

    results = list(g.query(query))

    if len(results) == 0:
        print("  ⚠️  NO RESULTS")
        assessment = "FAIL" if "should return" in expected_result.lower() else "PARTIAL"
    else:
        for i, row in enumerate(results, 1):
            print(f"  {i}. {' | '.join(str(val) for val in row)}")
        assessment = "PASS"

    print(f"\nExpected: {expected_result}")
    print(f"Assessment: {assessment}")
    print(f"Result count: {len(results)}")
    print()

    return assessment, len(results)

def run_tests():
    """Run all competency question tests."""
    g = load_test_data()

    results = {}

    # ==========================================================================
    # CQ10: What quality parameters characterize the water at Node N?
    # ==========================================================================
    assessment, count = test_query(
        g,
        "10",
        "What quality parameters characterize the water at Node N?",
        """
        PREFIX sosa: <http://www.w3.org/ns/sosa/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX ex: <http://example.org/waterFRAME/>

        SELECT DISTINCT ?property ?propertyLabel
        WHERE {
            ?obs a sosa:Observation ;
                 sosa:hasFeatureOfInterest ex:WastewaterEffluent1 ;
                 sosa:observedProperty ?property .

            OPTIONAL { ?property rdfs:label ?propertyLabel }
        }
        ORDER BY ?propertyLabel
        """,
        "Should return all water quality parameters measured at WWTP-1 effluent (BOD5, TN, TP, E.coli, pH, DO, Temperature)"
    )
    results['CQ10'] = (assessment, count)

    # ==========================================================================
    # CQ10b: Get all observations for a specific location
    # ==========================================================================
    assessment, count = test_query(
        g,
        "10b",
        "Get all observation values for WWTP-1 effluent on 2025-01-15",
        """
        PREFIX sosa: <http://www.w3.org/ns/sosa/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX ex: <http://example.org/waterFRAME/>

        SELECT ?propertyLabel ?value ?unit ?phenomenonTime
        WHERE {
            ?obs a sosa:Observation ;
                 sosa:hasFeatureOfInterest ex:WastewaterEffluent1 ;
                 sosa:observedProperty ?property ;
                 sosa:hasSimpleResult ?value ;
                 sosa:phenomenonTime ?phenomenonTime .

            OPTIONAL { ?property rdfs:label ?propertyLabel }
            OPTIONAL { ?obs ex:hasUnit ?unit }

            FILTER(STRSTARTS(STR(?phenomenonTime), "2025-01-15"))
        }
        ORDER BY ?phenomenonTime ?propertyLabel
        """,
        "Should return all measurements from 2025-01-15 with values and units"
    )
    results['CQ10b'] = (assessment, count)

    # ==========================================================================
    # CQ13: What contaminants are present above threshold T?
    # ==========================================================================
    assessment, count = test_query(
        g,
        "13",
        "What contaminants exceed threshold values? (e.g., BOD5 > 10 mg/L)",
        """
        PREFIX sosa: <http://www.w3.org/ns/sosa/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX ex: <http://example.org/waterFRAME/>

        SELECT ?featureLabel ?propertyLabel ?value ?phenomenonTime
        WHERE {
            ?obs a sosa:Observation ;
                 sosa:hasFeatureOfInterest ?feature ;
                 sosa:observedProperty ?property ;
                 sosa:hasSimpleResult ?value ;
                 sosa:phenomenonTime ?phenomenonTime .

            # Filter for BOD5 values > 10 mg/L
            FILTER(?property = ex:BOD5 && xsd:decimal(?value) > 10)

            OPTIONAL { ?feature rdfs:label ?featureLabel }
            OPTIONAL { ?property rdfs:label ?propertyLabel }
        }
        ORDER BY DESC(?value)
        """,
        "Should return greywater BOD5 (180 mg/L) but not effluent BOD5 (8.2 mg/L)"
    )
    results['CQ13'] = (assessment, count)

    # ==========================================================================
    # Sensor Capabilities: What sensors can measure property P?
    # ==========================================================================
    assessment, count = test_query(
        g,
        "Sensor-1",
        "What sensors can observe dissolved oxygen?",
        """
        PREFIX sosa: <http://www.w3.org/ns/sosa/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX ex: <http://example.org/waterFRAME/>

        SELECT ?sensor ?sensorLabel ?platform ?platformLabel
        WHERE {
            ?sensor a sosa:Sensor ;
                    sosa:observes ex:DissolvedOxygen .

            OPTIONAL { ?sensor rdfs:label ?sensorLabel }
            OPTIONAL {
                ?sensor sosa:isHostedBy ?platform .
                ?platform rdfs:label ?platformLabel
            }
        }
        """,
        "Should return MultiParameterProbe1 hosted by MonitoringStation1"
    )
    results['Sensor-1'] = (assessment, count)

    # ==========================================================================
    # Procedure Information: What procedure was used for measurement?
    # ==========================================================================
    assessment, count = test_query(
        g,
        "Procedure-1",
        "What procedures are used for BOD5 measurements?",
        """
        PREFIX sosa: <http://www.w3.org/ns/sosa/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX ex: <http://example.org/waterFRAME/>

        SELECT DISTINCT ?procedure ?procedureLabel ?methodology
        WHERE {
            ?obs a sosa:Observation ;
                 sosa:observedProperty ex:BOD5 ;
                 sosa:usedProcedure ?procedure .

            OPTIONAL { ?procedure rdfs:label ?procedureLabel }
            OPTIONAL { ?procedure ex:methodology ?methodology }
        }
        """,
        "Should return Standard Methods 5210B procedure"
    )
    results['Procedure-1'] = (assessment, count)

    # ==========================================================================
    # Sampling: What samples represent a feature of interest?
    # ==========================================================================
    assessment, count = test_query(
        g,
        "Sample-1",
        "What samples represent River R1?",
        """
        PREFIX sosa: <http://www.w3.org/ns/sosa/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX ex: <http://example.org/waterFRAME/>

        SELECT ?sample ?sampleLabel ?originalFeature ?featureLabel
        WHERE {
            ?sample a sosa:Sample ;
                    sosa:isSampleOf ?originalFeature .

            OPTIONAL { ?sample rdfs:label ?sampleLabel }
            OPTIONAL { ?originalFeature rdfs:label ?featureLabel }
        }
        """,
        "Should return RiverSample1 as sample of RiverR1"
    )
    results['Sample-1'] = (assessment, count)

    # ==========================================================================
    # Temporal Queries: Observations within time range
    # ==========================================================================
    assessment, count = test_query(
        g,
        "Temporal-1",
        "What observations were completed on 2025-01-15?",
        """
        PREFIX sosa: <http://www.w3.org/ns/sosa/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?obs ?propertyLabel ?value ?resultTime
        WHERE {
            ?obs a sosa:Observation ;
                 sosa:observedProperty ?property ;
                 sosa:hasSimpleResult ?value ;
                 sosa:resultTime ?resultTime .

            OPTIONAL { ?property rdfs:label ?propertyLabel }

            FILTER(STRSTARTS(STR(?resultTime), "2025-01-15"))
        }
        ORDER BY ?resultTime
        """,
        "Should return observations completed (result time) on 2025-01-15"
    )
    results['Temporal-1'] = (assessment, count)

    # ==========================================================================
    # Platform and Sensor Relationships
    # ==========================================================================
    assessment, count = test_query(
        g,
        "Platform-1",
        "What sensors are hosted by each platform?",
        """
        PREFIX sosa: <http://www.w3.org/ns/sosa/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?platform ?platformLabel ?sensor ?sensorLabel
        WHERE {
            ?platform a sosa:Platform ;
                      sosa:hosts ?sensor .

            ?sensor a sosa:Sensor .

            OPTIONAL { ?platform rdfs:label ?platformLabel }
            OPTIONAL { ?sensor rdfs:label ?sensorLabel }
        }
        ORDER BY ?platformLabel ?sensorLabel
        """,
        "Should return all sensor-platform relationships"
    )
    results['Platform-1'] = (assessment, count)

    # ==========================================================================
    # Summary
    # ==========================================================================
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    pass_count = sum(1 for assessment, _ in results.values() if assessment == "PASS")
    partial_count = sum(1 for assessment, _ in results.values() if assessment == "PARTIAL")
    fail_count = sum(1 for assessment, _ in results.values() if assessment == "FAIL")

    print(f"Total queries: {len(results)}")
    print(f"PASS: {pass_count}")
    print(f"PARTIAL: {partial_count}")
    print(f"FAIL: {fail_count}")
    print()

    for cq, (assessment, count) in results.items():
        status_symbol = "✓" if assessment == "PASS" else ("◐" if assessment == "PARTIAL" else "✗")
        print(f"  {status_symbol} {cq}: {assessment} ({count} results)")

if __name__ == "__main__":
    run_tests()
