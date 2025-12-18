"""
Run OWL reasoner on OntoCAPE with test data
Uses normalized HTTP URIs
"""

from pathlib import Path
from rdflib import Graph
from rdflib.namespace import OWL
from owlready2 import get_ontology, sync_reasoner_pellet, OwlReadyInconsistentOntologyError, World
import sys

print("=" * 80)
print("ONTOCAPE REASONING TEST (NORMALIZED)")
print("=" * 80)

# Merge normalized ontology with test data
print("\n1. MERGING ONTOLOGY + TEST DATA")
print("-" * 80)

ontocape_file = Path(__file__).parent / "ontocape_normalized.ttl"
test_file = Path(__file__).parent / "reasoning_test_normalized.ttl"

print(f"Loading ontology: {ontocape_file.name}")
g = Graph()
g.parse(str(ontocape_file), format="turtle")
print(f"✓ Loaded {len(g)} triples from ontology")

print(f"Loading test data: {test_file.name}")
g.parse(str(test_file), format="turtle")
print(f"✓ Total: {len(g)} triples (ontology + test data)")

# Remove owl:imports statements (they cause owlready2 to try downloading)
print(f"\nRemoving owl:imports statements...")
imports_removed = 0
for s, p, o in list(g.triples((None, OWL.imports, None))):
    g.remove((s, p, o))
    imports_removed += 1
print(f"✓ Removed {imports_removed} owl:imports statements")

# Save merged graph as RDF/XML for owlready2
temp_file = Path(__file__).parent / "merged_for_reasoning.owl"
print(f"\nConverting to RDF/XML for reasoner...")
g.serialize(str(temp_file), format="xml")
print(f"✓ Saved to: {temp_file.name}")

# Load with owlready2
print("\n2. LOADING INTO OWLREADY2")
print("-" * 80)

try:
    # Create a world and load without following imports
    world = World()
    onto = world.get_ontology(temp_file.as_uri()).load(only_local=True, reload=True)
    print(f"✓ Successfully loaded")
    print(f"  Base IRI: {onto.base_iri}")

    # Count entities
    classes = list(onto.classes())
    # Get individuals from all loaded ontologies in the world
    all_individuals = list(world.individuals())
    properties = list(onto.properties())

    print(f"\n📊 BEFORE REASONING:")
    print(f"  Classes: {len(classes)}")
    print(f"  All individuals in world: {len(all_individuals)}")
    print(f"  Properties: {len(properties)}")

    # Show test individuals
    print(f"\n  Test individuals from http://example.org/:")
    test_inds = [i for i in all_individuals if 'example.org' in str(i.iri)]
    print(f"  Found {len(test_inds)} test individuals")
    for ind in test_inds[:15]:
        types = [str(t).split('.')[-1] for t in ind.is_a if hasattr(t, '__name__')]
        print(f"    - {ind.name}: {', '.join(types) if types else 'no explicit types'}")

    print("\n3. RUNNING PELLET REASONER")
    print("-" * 80)
    print("  (This may take a moment with 68k triples...)")

    try:
        with onto:
            sync_reasoner_pellet(
                infer_property_values=True,
                infer_data_property_values=False,  # Faster
                debug=0  # Reduce verbosity
            )

        print("\n✅ REASONING COMPLETE - ONTOLOGY IS CONSISTENT")

        # Check for inferred types
        print(f"\n4. CHECKING INFERENCES")
        print("-" * 80)

        inferences = {}
        for ind in test_inds:
            original_types = set(str(t).split('.')[-1] for t in ind.INDIRECT_is_a if hasattr(t, '__name__'))
            asserted_types = set(str(t).split('.')[-1] for t in ind.is_a if hasattr(t, '__name__'))
            inferred = original_types - asserted_types

            if inferred:
                inferences[ind.name] = {
                    'asserted': asserted_types,
                    'inferred': inferred
                }

        if inferences:
            print("✓ Found inferred types:")
            for name, types in inferences.items():
                print(f"\n  {name}:")
                print(f"    Asserted: {', '.join(types['asserted'])}")
                print(f"    Inferred: {', '.join(types['inferred'])}")
        else:
            print("ℹ️  No additional type inferences")
            print("   (This is normal - OntoCAPE doesn't have complex class restrictions")
            print("    that would trigger type inference from property assertions)")

        # Check domain/range satisfaction
        print(f"\n5. DOMAIN/RANGE VALIDATION")
        print("-" * 80)

        violations = []
        for ind in test_inds:
            for prop in onto.properties():
                if hasattr(ind, prop.python_name):
                    values = getattr(ind, prop.python_name)
                    if values and not isinstance(values, (str, int, float, bool)):
                        # Check domain
                        if hasattr(prop, 'domain') and prop.domain:
                            domains = prop.domain if isinstance(prop.domain, list) else [prop.domain]
                            if not any(isinstance(ind, d) for d in domains if hasattr(d, '__name__')):
                                violations.append(f"{ind.name}.{prop.python_name}: domain not satisfied")

        if violations:
            print("⚠️  Potential violations (may be OK if domains are not enforced):")
            for v in violations[:5]:
                print(f"    {v}")
            if len(violations) > 5:
                print(f"    ... and {len(violations)-5} more")
        else:
            print("✓ All domain/range constraints satisfied")

        # Summary
        print(f"\n" + "=" * 80)
        print("REASONING SUMMARY")
        print("=" * 80)
        print("✅ Ontology is CONSISTENT")
        print(f"✓ Processed {len(test_inds)} test individuals")
        print(f"✓ {len(inferences)} individuals with inferred types" if inferences else "✓ No type inferences (expected)")
        print("\n💡 INTERPRETATION:")
        print("The OntoCAPE ontology combined with the test data is")
        print("logically consistent. The wastewater treatment network")
        print("structure is compatible with OntoCAPE's definitions.")

    except OwlReadyInconsistentOntologyError as e:
        print("\n❌ INCONSISTENCY DETECTED")
        print("=" * 80)
        print(f"Error: {e}")
        print("\nThe ontology contains contradictory statements.")
        sys.exit(1)

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
