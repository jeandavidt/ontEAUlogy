"""Test QUDT unit conversions using SPARQL and QUDT's conversion graph.

This demonstrates approach #3: Using QUDT's built-in conversionMultiplier
properties to perform unit conversions directly in the ontology/SPARQL layer.
"""

from pathlib import Path
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS
from decimal import Decimal

# Define namespaces
SOSA = Namespace("http://www.w3.org/ns/sosa/")
QUDT = Namespace("http://qudt.org/schema/qudt/")
UNIT = Namespace("http://qudt.org/vocab/unit/")
QK = Namespace("http://qudt.org/vocab/quantitykind/")
EX = Namespace("http://example.org/waterFRAME/")

def load_data_with_qudt():
    """Load test data AND QUDT units vocabulary."""
    base_path = Path(__file__).parent

    g = Graph()
    g.bind("sosa", SOSA)
    g.bind("qudt", QUDT)
    g.bind("unit", UNIT)
    g.bind("qk", QK)
    g.bind("ex", EX)

    print("Loading QUDT units vocabulary...")
    g.parse(base_path / "qudt-units.ttl", format="turtle")
    print(f"  QUDT: {len(g)} triples")

    print("Loading test data...")
    g.parse(base_path / "test_data_flow_balance.ttl", format="turtle")
    print(f"  Total: {len(g)} triples\n")

    return g

def test_cq_qudt_1_sparql(g: Graph):
    """
    CQ-QUDT-1: Sum flows in different units using SPARQL conversion.

    Strategy:
    1. Get all flow values with their units
    2. Use QUDT conversionMultiplier to convert to coherent SI unit (m³/s)
    3. Convert m³/s to m³/day in SPARQL
    4. Sum the results
    """
    print("=" * 80)
    print("CQ-QUDT-1: Sum flows using QUDT conversion graph in SPARQL")
    print("-" * 80)

    query = """
        PREFIX sosa: <http://www.w3.org/ns/sosa/>
        PREFIX qudt: <http://qudt.org/schema/qudt/>
        PREFIX unit: <http://qudt.org/vocab/unit/>
        PREFIX ex: <http://example.org/waterFRAME/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?source ?sourceLabel ?value ?unit_label ?mult ?value_m3_s ?value_m3_day
        WHERE {
            # Get flow observations for Junction1 sources
            ex:Junction1 ex:receivesFlowFrom ?source .

            ?obs a sosa:Observation ;
                 sosa:hasFeatureOfInterest ?source ;
                 sosa:hasResult ?result .

            ?result qudt:numericValue ?value ;
                    qudt:unit ?unit .

            # Get QUDT's conversion multiplier (converts TO coherent SI unit: m³/s)
            ?unit qudt:conversionMultiplier ?mult .

            # Optional labels
            OPTIONAL { ?source rdfs:label ?sourceLabel }
            OPTIONAL { ?unit rdfs:label ?unit_label }

            # Calculate values
            # Step 1: Convert to m³/s using QUDT multiplier
            BIND(?value * ?mult AS ?value_m3_s)

            # Step 2: Convert m³/s to m³/day (multiply by 86,400 s/day)
            BIND(?value_m3_s * 86400.0 AS ?value_m3_day)
        }
    """

    results = list(g.query(query))
    print(f"Found {len(results)} flow measurements:\n")

    total_m3_day = Decimal('0')

    for source, sourceLabel, value, unit_label, mult, value_m3_s, value_m3_day in results:
        unit_str = str(unit_label) if unit_label else "unknown unit"
        value_m3_day_dec = Decimal(str(value_m3_day))
        total_m3_day += value_m3_day_dec

        print(f"  {sourceLabel}:")
        print(f"    Input: {value} {unit_str}")
        print(f"    QUDT multiplier: {mult}")
        print(f"    → {float(value_m3_s):.6f} m³/s (coherent SI)")
        print(f"    → {value_m3_day_dec:.2f} m³/day")

    print(f"\n✓ TOTAL FLOW (via QUDT conversions): {total_m3_day:.2f} m³/day")
    print(f"  Expected: ~24,318 m³/day\n")

    return total_m3_day

def test_cq_qudt_2_sparql(g: Graph):
    """
    CQ-QUDT-2/3: Mass loading using QUDT conversions in SPARQL.

    Strategy:
    1. Convert flow to m³/s using QUDT
    2. Convert concentration to kg/m³ using QUDT
    3. Calculate mass loading: (m³/s) × (kg/m³) = kg/s
    4. Convert to kg/day
    """
    print("=" * 80)
    print("CQ-QUDT-2/3: Mass loading via QUDT SPARQL conversions")
    print("-" * 80)

    query = """
        PREFIX sosa: <http://www.w3.org/ns/sosa/>
        PREFIX qudt: <http://qudt.org/schema/qudt/>
        PREFIX ex: <http://example.org/waterFRAME/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?stream ?streamLabel
               ?flow_value ?flow_mult ?flow_m3_s
               ?conc_value ?conc_mult ?conc_kg_m3
               ?loading_kg_s ?loading_kg_day
        WHERE {
            ?stream a ex:WastewaterStream .
            OPTIONAL { ?stream rdfs:label ?streamLabel }

            # Flow observation
            ?flow_obs sosa:hasFeatureOfInterest ?stream ;
                      sosa:observedProperty ex:FlowRate ;
                      sosa:hasResult ?flow_result .
            ?flow_result qudt:numericValue ?flow_value ;
                        qudt:unit ?flow_unit .
            ?flow_unit qudt:conversionMultiplier ?flow_mult .

            # BOD concentration observation
            ?conc_obs sosa:hasFeatureOfInterest ?stream ;
                      sosa:observedProperty ex:BOD_Concentration ;
                      sosa:hasResult ?conc_result .
            ?conc_result qudt:numericValue ?conc_value ;
                        qudt:unit ?conc_unit .
            ?conc_unit qudt:conversionMultiplier ?conc_mult .

            # Calculations
            # Flow: convert to m³/s (coherent SI for VolumeFlowRate)
            BIND(?flow_value * ?flow_mult AS ?flow_m3_s)

            # Concentration: mg/L → kg/m³
            # QUDT converts mg/L to kg/m³ using multiplier
            # mg/L coherent SI is kg/m³ (same dimensionally)
            BIND(?conc_value * ?conc_mult AS ?conc_kg_m3)

            # Mass loading: m³/s × kg/m³ = kg/s
            BIND(?flow_m3_s * ?conc_kg_m3 AS ?loading_kg_s)

            # Convert to kg/day
            BIND(?loading_kg_s * 86400.0 AS ?loading_kg_day)
        }
    """

    results = list(g.query(query))
    print(f"\nFound {len(results)} streams:\n")

    total_loading = Decimal('0')

    for row in results:
        (stream, streamLabel, flow_value, flow_mult, flow_m3_s,
         conc_value, conc_mult, conc_kg_m3, loading_kg_s, loading_kg_day) = row

        loading_dec = Decimal(str(loading_kg_day))
        total_loading += loading_dec

        print(f"  {streamLabel}:")
        print(f"    Flow: {flow_value} (×{flow_mult}) = {float(flow_m3_s):.6f} m³/s")
        print(f"    BOD:  {conc_value} (×{conc_mult}) = {float(conc_kg_m3):.6f} kg/m³")
        print(f"    ✓ Loading: {loading_dec:.2f} kg/day")

    print(f"\n✓ TOTAL BOD LOADING (via QUDT): {total_loading:.2f} kg/day")
    print(f"  Expected: ~1,988.7 kg/day\n")

    return total_loading

def test_cq_qudt_4_sparql(g: Graph):
    """
    CQ-QUDT-4: Dimensional compatibility check using quantityKind.

    Uses QUDT's hasQuantityKind to verify dimensional compatibility.
    """
    print("=" * 80)
    print("CQ-QUDT-4: Dimensional compatibility via quantityKind")
    print("-" * 80)

    # Query 1: Find all quantity kinds in our data
    query1 = """
        PREFIX qudt: <http://qudt.org/schema/qudt/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?qk ?qk_label (COUNT(?result) AS ?count)
        WHERE {
            ?result a qudt:QuantityValue ;
                    qudt:unit ?unit .
            ?unit qudt:hasQuantityKind ?qk .
            OPTIONAL { ?qk rdfs:label ?qk_label }
        }
        GROUP BY ?qk ?qk_label
        ORDER BY DESC(?count)
    """

    results1 = list(g.query(query1))
    print("\n Quantity kinds in test data:")
    for qk, qk_label, count in results1:
        qk_name = str(qk_label) if qk_label else str(qk).split('/')[-1]
        print(f"  • {qk_name}: {count} measurements")

    # Query 2: Check if two specific measurements are compatible
    query2 = """
        PREFIX qudt: <http://qudt.org/schema/qudt/>
        PREFIX ex: <http://example.org/waterFRAME/>

        SELECT ?obs1_qk ?obs2_qk ?compatible
        WHERE {
            # Flow observation
            ex:obs_SourceA_Flow_2025_01_15 sosa:hasResult ?result1 .
            ?result1 qudt:unit ?unit1 .
            ?unit1 qudt:hasQuantityKind ?obs1_qk .

            # Another flow observation
            ex:obs_SourceB_Flow_2025_01_15 sosa:hasResult ?result2 .
            ?result2 qudt:unit ?unit2 .
            ?unit2 qudt:hasQuantityKind ?obs2_qk .

            # Check compatibility
            BIND(IF(?obs1_qk = ?obs2_qk, "COMPATIBLE", "INCOMPATIBLE") AS ?compatible)
        }
    """

    results2 = list(g.query(query2))
    if results2:
        obs1_qk, obs2_qk, compatible = results2[0]
        print(f"\n✓ Compatibility check:")
        print(f"  Source A (m³/day): {obs1_qk.split('/')[-1]}")
        print(f"  Source B (L/s):    {obs2_qk.split('/')[-1]}")
        print(f"  Result: {compatible} - Can be summed!")

    print("\n  Invalid operation (would require check in application):")
    print(f"  Temperature + FlowRate → INCOMPATIBLE quantity kinds\n")

def test_cq_qudt_5_sparql(g: Graph):
    """
    CQ-QUDT-5: Junction mass balance using QUDT conversions.
    """
    print("=" * 80)
    print("CQ-QUDT-5: Mass balance at Junction2 via QUDT")
    print("-" * 80)

    query = """
        PREFIX sosa: <http://www.w3.org/ns/sosa/>
        PREFIX qudt: <http://qudt.org/schema/qudt/>
        PREFIX ex: <http://example.org/waterFRAME/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?pipe ?pipeLabel
               ?flow_m3_day ?conc_mg_l ?loading_kg_day
        WHERE {
            ex:Junction2 ex:receivesFlowFrom ?pipe .
            OPTIONAL { ?pipe rdfs:label ?pipeLabel }

            # Flow
            ?flow_obs sosa:hasFeatureOfInterest ?pipe ;
                      sosa:observedProperty ex:FlowRate ;
                      sosa:hasResult ?flow_result .
            ?flow_result qudt:numericValue ?flow_value ;
                        qudt:unit ?flow_unit .
            ?flow_unit qudt:conversionMultiplier ?flow_mult .

            # TN concentration
            ?tn_obs sosa:hasFeatureOfInterest ?pipe ;
                    sosa:observedProperty ex:TotalNitrogen ;
                    sosa:hasResult ?tn_result .
            ?tn_result qudt:numericValue ?tn_value ;
                      qudt:unit ?tn_unit .
            ?tn_unit qudt:conversionMultiplier ?tn_mult .

            # Convert flow to m³/day
            BIND((?flow_value * ?flow_mult * 86400.0) AS ?flow_m3_day)

            # Convert concentration to mg/L
            # Note: QUDT converts to kg/m³, need to convert back to mg/L
            # kg/m³ × 1000 = mg/L
            BIND((?tn_value * ?tn_mult * 1000.0) AS ?conc_mg_l)

            # Mass loading: m³/day × mg/L = kg/day
            # m³ × mg/L = 1000 L × mg/L = 1000 mg = 0.001 kg
            BIND(?flow_m3_day * ?conc_mg_l * 0.001 AS ?loading_kg_day)
        }
    """

    results = list(g.query(query))
    print("\nInflows to Junction2:")

    total_flow = Decimal('0')
    total_loading = Decimal('0')

    for pipe, pipeLabel, flow_m3_day, conc_mg_l, loading_kg_day in results:
        flow_dec = Decimal(str(flow_m3_day))
        loading_dec = Decimal(str(loading_kg_day))

        total_flow += flow_dec
        total_loading += loading_dec

        print(f"\n  {pipeLabel}:")
        print(f"    Flow: {flow_dec:.2f} m³/day")
        print(f"    TN:   {float(conc_mg_l):.2f} mg/L")
        print(f"    TN loading: {loading_dec:.2f} kg/day")

    avg_conc = (total_loading / total_flow * Decimal('1000')) if total_flow > 0 else Decimal('0')

    print(f"\n✓ JUNCTION BALANCE (via QUDT):")
    print(f"  Total flow: {total_flow:.2f} m³/day")
    print(f"  Total TN loading: {total_loading:.2f} kg/day")
    print(f"  Average concentration: {avg_conc:.2f} mg/L")
    print(f"\n  Expected: 14,480 m³/day, 1,977.6 kg/day, 136.6 mg/L\n")

if __name__ == "__main__":
    print("=" * 80)
    print("QUDT SPARQL-BASED UNIT CONVERSIONS")
    print("Using QUDT's conversionMultiplier properties in SPARQL queries")
    print("=" * 80)
    print()

    g = load_data_with_qudt()

    test_cq_qudt_1_sparql(g)
    test_cq_qudt_2_sparql(g)
    test_cq_qudt_4_sparql(g)
    test_cq_qudt_5_sparql(g)

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("✓ All conversions performed using QUDT's conversionMultiplier")
    print("✓ SPARQL queries leverage ontology's built-in conversion data")
    print("✓ Dimensional compatibility validated via hasQuantityKind")
    print("✓ Mass balances calculated with QUDT-based unit normalization")
    print("\nAdvantages:")
    print("  • Ontology provides conversion logic, not application code")
    print("  • SPARQL queries are portable across triplestores")
    print("  • Conversion factors maintained by QUDT (authoritative source)")
    print("  • Dimensional analysis built into the semantic model")
    print("\nLimitations:")
    print("  • Need to load QUDT units vocabulary (~42k triples)")
    print("  • Some conversions require intermediate steps (SI unit)")
    print("  • Complex queries for multi-hop conversions")
