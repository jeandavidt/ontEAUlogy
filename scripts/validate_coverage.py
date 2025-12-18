#!/usr/bin/env python3
"""
Simple ontology validation script for waterFRAME
Checks ontology loading, consistency, and competency question answering
"""

import sys
import os
from pathlib import Path
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, OWL

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))


def load_ontology():
    """Load the ontology modules and instances"""
    g = Graph()

    # Define base paths
    base_dir = Path(__file__).parent.parent
    ontology_dir = base_dir / "data" / "ontology"
    instances_dir = base_dir / "data" / "ontology" / "instances"
    sparql_dir = base_dir / "data" / "competency_questions" / "sparql"

    # Load main ontology (this imports all modules)
    main_ontology_file = ontology_dir / "waterframe.ttl"
    if main_ontology_file.exists():
        g.parse(str(main_ontology_file), format="turtle")
        print(f"✓ Loaded main ontology: {len(g)} triples")

        # Load core modules explicitly (RDFLib doesn't auto-download imports)
        modules_dir = ontology_dir / "modules" / "core"
        core_modules = ["material_entities.ttl", "properties.ttl"]

        for module_file in core_modules:
            module_path = modules_dir / module_file
            if module_path.exists():
                g.parse(str(module_path), format="turtle")
                print(f"✓ Loaded {module_file}: {len(g)} total triples")
            else:
                print(f"✗ {module_file} not found")
                return None, None, None
    else:
        print("✗ Main ontology file not found")
        return None, None, None

    # Load instances
    instances_file = instances_dir / "household_case1.ttl"
    if instances_file.exists():
        g.parse(str(instances_file), format="turtle")
        print(f"✓ Loaded instances: {len(g)} total triples")
    else:
        print("✗ Instance file not found")
        return None, None, None

    return g, sparql_dir, base_dir


def check_consistency(g):
    """Basic consistency checks"""
    print("\n--- Consistency Checks ---")

    # Check for duplicate type assertions
    duplicate_types = 0
    type_check = {}
    for s, o in g.subject_objects(RDF.type):
        if (s, o) in type_check:
            duplicate_types += 1
        else:
            type_check[(s, o)] = 1

    if duplicate_types > 0:
        print(f"⚠ Found {duplicate_types} duplicate type assertions")
    else:
        print("✓ No duplicate type assertions")

    # Check for circular subclass relationships (basic check)
    subclass_cycles = 0
    for s, o in g.subject_objects(RDFS.subClassOf):
        if g.value(o, RDFS.subClassOf) == s:
            subclass_cycles += 1

    if subclass_cycles > 0:
        print(f"✗ Found {subclass_cycles} circular subclass relationships")
        return False
    else:
        print("✓ No circular subclass relationships detected")

    return True


def test_cq1(g, sparql_dir):
    """Test CQ1 query"""
    print("\n--- CQ1 Test: All Nodes in System ---")

    cq1_file = sparql_dir / "cq01_all_nodes.rq"
    if not cq1_file.exists():
        print("✗ CQ1 query file not found")
        return False

    try:
        with open(cq1_file, "r") as f:
            query = f.read()

        results = g.query(query)
        result_count = len(results)

        print(f"✓ CQ1 executed successfully")
        print(f"✓ Found {result_count} nodes in the system")

        if result_count > 0:
            print("Node types found:")
            type_counts = {}
            for row in results:
                node_type = str(row[1]).split("#")[-1]
                type_counts[node_type] = type_counts.get(node_type, 0) + 1

            for node_type, count in sorted(type_counts.items()):
                print(f"  {node_type}: {count}")

        return True

    except Exception as e:
        print(f"✗ CQ1 query failed: {e}")
        return False


def test_flow_cqs(g, sparql_dir):
    """Test flow-related competency questions"""
    print("\n--- Flow CQ Tests ---")

    flow_cqs = [
        "cq03_input_sources.rq",
        "cq04_downstream_nodes.rq",
        "cq05_flow_path.rq",
    ]
    results = {}

    for cq_file in flow_cqs:
        cq_path = sparql_dir / cq_file
        cq_name = cq_file.replace(".rq", "").upper()

        if cq_path.exists():
            try:
                with open(cq_path, "r") as f:
                    query = f.read()

                result_count = len(g.query(query))
                results[cq_name] = result_count
                print(f"✓ {cq_name}: {result_count} results")
            except Exception as e:
                results[cq_name] = f"ERROR: {e}"
                print(f"✗ {cq_name}: {e}")
        else:
            results[cq_name] = "FILE_NOT_FOUND"
            print(f"✗ {cq_name}: Query file not found")

    return results


def main():
    print("=== waterFRAME Validation Report ===")

    # Load ontology
    g, sparql_dir, base_dir = load_ontology()
    if g is None:
        print("✗ Failed to load ontology")
        return 1

    # Check consistency
    is_consistent = check_consistency(g)
    if not is_consistent:
        print("✗ Ontology consistency checks failed")
        return 1

    # Test CQ1
    cq1_success = test_cq1(g, sparql_dir)

    # Test flow CQs
    flow_results = test_flow_cqs(g, sparql_dir)

    # Summary
    print("\n--- Validation Summary ---")
    print(f"✓ Total triples loaded: {len(g)}")
    print(f"✓ CQ1 (All nodes): {'PASS' if cq1_success else 'FAIL'}")

    for cq_name, result in flow_results.items():
        if isinstance(result, int):
            print(f"✓ {cq_name}: PASS ({result} results)")
        else:
            print(f"✗ {cq_name}: FAIL ({result})")

    flow_cqs_work = all(isinstance(r, int) for r in flow_results.values())

    if is_consistent and cq1_success and flow_cqs_work:
        print("✓ All validation checks passed")
        print("✓ Material entities + Properties modules working")
        return 0
    else:
        print("✗ Some validation checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
