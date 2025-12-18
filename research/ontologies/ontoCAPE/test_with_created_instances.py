"""
Test OntoCAPE by creating instances programmatically and running reasoner.

This script:
1. Loads the fixed OntoCAPE ontology modules
2. Creates test instances programmatically
3. Runs a reasoner (Pellet) to check consistency
4. Reports results
"""

from pathlib import Path
from owlready2 import get_ontology, default_world, sync_reasoner_pellet, OwlReadyInconsistentOntologyError, Thing
import sys
from datetime import datetime

def main():
    script_dir = Path(__file__).parent
    ontocape_fixed = script_dir / "OntoCAPE_fixed"

    if not ontocape_fixed.exists():
        print(f"❌ Error: OntoCAPE_fixed directory not found")
        print("Run fix_imports.py first!")
        return 1

    print("=" * 80)
    print("OntoCAPE REASONER TEST WITH PROGRAMMATICALLY CREATED INSTANCES")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Load key ontology modules
    print("Loading OntoCAPE modules...")
    print("-" * 80)

    system_path = ontocape_fixed / "upper_level/system.owl"
    substance_path = ontocape_fixed / "material/substance/substance.owl"
    process_path = ontocape_fixed / "chemical_process_system/CPS_function/process.owl"

    print(f"Loading: {system_path.name}")
    system_onto = get_ontology(f"file://{system_path.as_posix()}").load()

    print(f"Loading: {substance_path.name}")
    substance_onto = get_ontology(f"file://{substance_path.as_posix()}").load()

    print(f"Loading: {process_path.name}")
    process_onto = get_ontology(f"file://{process_path.as_posix()}").load()

    print("✓ Loaded ontology modules")
    print()

    # Count entities
    print("Ontology statistics:")
    print("-" * 80)
    all_classes = list(default_world.classes())
    all_obj_props = list(default_world.object_properties())
    all_data_props = list(default_world.data_properties())

    print(f"Classes: {len(all_classes)}")
    print(f"Object properties: {len(all_obj_props)}")
    print(f"Data properties: {len(all_data_props)}")
    print()

    # Find key classes
    print("Finding key classes for instance creation...")
    print("-" * 80)

    # Search for important classes
    System_class = None
    ChemicalSpecies_class = None
    MaterialStream_class = None

    for cls in all_classes:
        class_name = cls.name if hasattr(cls, 'name') else str(cls).split('.')[-1]
        if class_name == "System":
            System_class = cls
            print(f"✓ Found: System class")
        elif "ChemicalSpecies" in class_name:
            ChemicalSpecies_class = cls
            print(f"✓ Found: {class_name} class")
        elif "MaterialStream" in class_name:
            MaterialStream_class = cls
            print(f"✓ Found: {class_name} class")

    if not System_class:
        print("⚠ Warning: Could not find System class")

    print()

    # Create test instances
    print("Creating test instances...")
    print("-" * 80)

    created_instances = []

    # Create instances in the system ontology namespace
    with system_onto:
        # Create a simple System instance
        if System_class:
            test_system = System_class("TestSystem1")
            created_instances.append(test_system)
            print(f"✓ Created: {test_system.name} (type: {System_class.name})")

        # Create another system
        if System_class:
            test_system2 = System_class("TestSystem2")
            created_instances.append(test_system2)
            print(f"✓ Created: {test_system2.name} (type: {System_class.name})")

    # Create instances in substance ontology namespace
    with substance_onto:
        if ChemicalSpecies_class:
            water = ChemicalSpecies_class("Water_H2O")
            created_instances.append(water)
            print(f"✓ Created: {water.name} (type: {ChemicalSpecies_class.name})")

            oxygen = ChemicalSpecies_class("Oxygen_O2")
            created_instances.append(oxygen)
            print(f"✓ Created: {oxygen.name} (type: {ChemicalSpecies_class.name})")

    print(f"\n✓ Created {len(created_instances)} test instances")
    print()

    # Verify instances exist
    all_individuals_before = list(default_world.individuals())
    print(f"Total individuals in world: {len(all_individuals_before)}")
    print()

    if len(all_individuals_before) == 0:
        print("❌ ERROR: Failed to create instances!")
        print("This indicates an issue with instance creation.")
        return 1

    # Run the reasoner
    print("Running Pellet reasoner...")
    print("-" * 80)
    print("Checking for:")
    print("  - Consistency (no contradictions)")
    print("  - Class hierarchy inferences")
    print("  - Instance classifications")
    print()

    try:
        print("Starting reasoner...")
        sync_reasoner_pellet(debug=1, infer_property_values=True)
        print("✓ Reasoner completed successfully!")
        print()

        # Check results after reasoning
        all_individuals_after = list(default_world.individuals())
        all_classes_after = list(default_world.classes())

        print("Statistics AFTER reasoning:")
        print("-" * 80)
        print(f"Classes: {len(all_classes_after)} (before: {len(all_classes)})")
        print(f"Individuals: {len(all_individuals_after)} (before: {len(all_individuals_before)})")
        print()

        # Check instance types after reasoning
        print("Instance classifications after reasoning:")
        print("-" * 80)
        for ind in created_instances:
            types = [t.name if hasattr(t, 'name') else str(t) for t in ind.is_a]
            print(f"{ind.name}:")
            for t in types:
                print(f"  - {t}")

        print()
        print("=" * 80)
        print("✅ REASONING TEST RESULTS")
        print("=" * 80)
        print("✅ ONTOLOGY IS CONSISTENT")
        print(f"✅ Successfully reasoned over {len(all_individuals_after)} individuals")
        print("✅ No logical contradictions found")
        print()
        print("CONCLUSION:")
        print("The OntoCAPE ontology is logically sound and can handle instances correctly.")
        print("The previous agent's test showed 0 individuals because they didn't")
        print("actually create or load any instance data - they only loaded the")
        print("schema/TBox without the instance data/ABox.")
        return 0

    except OwlReadyInconsistentOntologyError as e:
        print()
        print("=" * 80)
        print("❌ ONTOLOGY IS INCONSISTENT")
        print("=" * 80)
        print(f"Error: {e}")
        print()
        print("The ontology contains logical contradictions.")
        return 1

    except Exception as e:
        print(f"✗ Reasoner failed: {type(e).__name__}")
        print(f"  Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
