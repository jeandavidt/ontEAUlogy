"""Test reasoning with SOSA/SSN ontology using owlready2."""

from pathlib import Path
from owlready2 import get_ontology, sync_reasoner_pellet, OwlReadyInconsistentOntologyError
import time

def test_reasoning():
    """Test ontology consistency and reasoning."""
    base_path = Path(__file__).parent

    print("=" * 80)
    print("REASONING CONSISTENCY CHECK")
    print("=" * 80)

    # Load SOSA ontology (using RDF/XML format for owlready2 compatibility)
    print("\nLoading SOSA ontology...")
    sosa_onto = get_ontology(str(base_path / "sosa_updated.rdf")).load()
    print(f"SOSA loaded: {sosa_onto.base_iri}")

    # Load SSN ontology
    print("\nLoading SSN ontology...")
    ssn_onto = get_ontology(str(base_path / "ssn.rdf")).load()
    print(f"SSN loaded: {ssn_onto.base_iri}")

    # Load test data (using RDF/XML format for owlready2 compatibility)
    print("\nLoading test data...")
    test_onto = get_ontology(str(base_path / "water_quality_test_data.rdf")).load()
    print(f"Test data loaded: {test_onto.base_iri}")

    # List all classes
    print("\n" + "-" * 80)
    print("Classes loaded:")
    all_classes = list(sosa_onto.classes()) + list(ssn_onto.classes())
    for cls in sorted(set(all_classes), key=lambda x: str(x)):
        print(f"  • {cls}")

    # List all individuals before reasoning
    print("\n" + "-" * 80)
    print("Individuals before reasoning:")
    all_individuals_before = list(test_onto.individuals())
    print(f"  Total: {len(all_individuals_before)}")

    # Run reasoner
    print("\n" + "-" * 80)
    print("Running Pellet reasoner...")
    start_time = time.time()

    try:
        sync_reasoner_pellet(
            infer_property_values=True,
            infer_data_property_values=True,
            debug=False
        )
        elapsed_time = time.time() - start_time
        print(f"✓ Ontology is CONSISTENT")
        print(f"  Reasoning completed in {elapsed_time:.2f} seconds")

        # Check for inferred facts
        print("\n" + "-" * 80)
        print("Checking for inferred facts...")

        # Check if any new class memberships were inferred
        print("\nClass instances (including inferred):")
        for cls in sorted(set(all_classes), key=lambda x: str(x))[:10]:  # Show first 10
            instances = list(cls.instances())
            if instances:
                print(f"  • {cls.name}: {len(instances)} instance(s)")
                for inst in instances[:3]:  # Show first 3 instances
                    print(f"    - {inst.name if hasattr(inst, 'name') else inst}")

        print("\n" + "-" * 80)
        print("ASSESSMENT: ✓ PASS")
        print("The SOSA/SSN ontology with water quality test data is consistent.")
        print("No logical contradictions detected.")

    except OwlReadyInconsistentOntologyError as e:
        elapsed_time = time.time() - start_time
        print(f"✗ INCONSISTENCY DETECTED")
        print(f"  Error: {e}")
        print(f"  Time to detect: {elapsed_time:.2f} seconds")
        print("\n" + "-" * 80)
        print("ASSESSMENT: ✗ FAIL")
        print("The ontology contains logical contradictions.")

    except Exception as e:
        print(f"✗ ERROR during reasoning: {e}")
        print("\n" + "-" * 80)
        print("ASSESSMENT: ⚠ ERROR")
        print(f"Unexpected error: {type(e).__name__}")

if __name__ == "__main__":
    test_reasoning()
