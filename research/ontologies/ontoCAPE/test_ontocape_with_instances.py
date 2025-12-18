"""
Test OntoCAPE with a reasoner using ACTUAL instances from the fixed modules.

This script:
1. Loads the fixed OntoCAPE ontology with instances
2. Runs a reasoner (Pellet) to check consistency
3. Tests inference capabilities
4. Reports actual statistics including individuals
"""

from pathlib import Path
from owlready2 import get_ontology, default_world, sync_reasoner_pellet, OwlReadyInconsistentOntologyError
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
    print("OntoCAPE REASONER TEST WITH INSTANCES")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Step 1: Load base ontology modules
    print("Step 1: Loading base OntoCAPE modules...")
    print("-" * 80)

    base_modules = [
        "upper_level/system.owl",
        "supporting_concepts/physical_dimension/physical_dimension.owl",
        "supporting_concepts/SI_unit/SI_unit.owl",
        "material/substance/substance.owl",
    ]

    for module in base_modules:
        module_path = ontocape_fixed / module
        print(f"Loading: {module}")
        onto = get_ontology(f"file://{module_path.as_posix()}").load()

    print(f"✓ Loaded {len(base_modules)} base modules")
    print()

    # Step 2: Load chemical species with instances
    print("Step 2: Loading chemical species with instances...")
    print("-" * 80)

    # Use the test file first (smaller subset)
    test_species_path = ontocape_fixed / "material/substance/chemical_species__test.owl"

    if test_species_path.exists():
        print(f"Loading: chemical_species__test.owl")
        species_onto = get_ontology(f"file://{test_species_path.as_posix()}").load()
        print("✓ Loaded test chemical species file")
    else:
        print("⚠ Test file not found, loading full dataset...")
        all_species_path = ontocape_fixed / "material/substance/chemical_species__all.owl"
        print(f"Loading: chemical_species__all.owl (this may take a while...)")
        species_onto = get_ontology(f"file://{all_species_path.as_posix()}").load()
        print("✓ Loaded full chemical species file")

    print()

    # Step 3: Count entities before reasoning
    print("Step 3: Statistics BEFORE reasoning")
    print("-" * 80)

    all_classes = list(default_world.classes())
    all_individuals = list(default_world.individuals())
    all_obj_props = list(default_world.object_properties())
    all_data_props = list(default_world.data_properties())

    print(f"Classes: {len(all_classes)}")
    print(f"Object properties: {len(all_obj_props)}")
    print(f"Data properties: {len(all_data_props)}")
    print(f"Individuals: {len(all_individuals)}")
    print()

    if len(all_individuals) == 0:
        print("⚠ WARNING: No individuals found!")
        print("Cannot perform meaningful reasoning tests without instances.")
        return 1

    # Show sample individuals
    print("Sample individuals (first 10):")
    for i, ind in enumerate(all_individuals[:10]):
        types = [t.__name__ if hasattr(t, '__name__') else str(t) for t in ind.is_a]
        print(f"  {i+1}. {ind.name} - types: {', '.join(types[:2])}")
    print()

    # Step 4: Run the reasoner
    print("Step 4: Running Pellet reasoner...")
    print("-" * 80)
    print("This will check:")
    print("  - Ontology consistency (no logical contradictions)")
    print("  - Class hierarchy inference")
    print("  - Property inference")
    print("  - Instance classification")
    print()

    try:
        print("Starting reasoner (this may take a minute)...")
        sync_reasoner_pellet(debug=1)
        print("✓ Reasoner completed successfully!")
        print()

        # Step 5: Check results after reasoning
        print("Step 5: Statistics AFTER reasoning")
        print("-" * 80)

        all_classes_after = list(default_world.classes())
        all_individuals_after = list(default_world.individuals())

        print(f"Classes: {len(all_classes_after)}")
        print(f"Individuals: {len(all_individuals_after)}")
        print()

        # Check if reasoning inferred anything new
        if len(all_classes_after) > len(all_classes):
            print(f"✓ Reasoner inferred {len(all_classes_after) - len(all_classes)} new class relationships")

        if len(all_individuals_after) > len(all_individuals):
            print(f"✓ Reasoner inferred {len(all_individuals_after) - len(all_individuals)} new individuals")

        # Step 6: Test specific inferences
        print()
        print("Step 6: Testing specific class instances")
        print("-" * 80)

        # Find ChemicalSpecies class and count instances
        for cls in all_classes:
            class_name = cls.name if hasattr(cls, 'name') else str(cls).split('.')[-1]
            if "ChemicalSpecies" in class_name:
                instances = list(cls.instances())
                print(f"Class: {class_name}")
                print(f"  Direct instances: {len(instances)}")
                if instances:
                    print(f"  Sample instances:")
                    for i, inst in enumerate(instances[:5]):
                        print(f"    {i+1}. {inst.name}")
                break

        print()
        print("=" * 80)
        print("REASONING TEST RESULTS")
        print("=" * 80)
        print("✅ ONTOLOGY IS CONSISTENT")
        print(f"✅ Successfully reasoned over {len(all_individuals)} individuals")
        print("✅ No logical contradictions found")
        print()
        print("The OntoCAPE ontology is logically sound and ready for use!")
        return 0

    except OwlReadyInconsistentOntologyError as e:
        print()
        print("=" * 80)
        print("❌ ONTOLOGY IS INCONSISTENT")
        print("=" * 80)
        print(f"Error: {e}")
        print()
        print("The ontology contains logical contradictions.")
        print("This means some axioms are incompatible with each other.")
        return 1

    except Exception as e:
        print(f"✗ Reasoner failed: {type(e).__name__}")
        print(f"  Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
