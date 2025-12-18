"""
Test that OntoCAPE modules load correctly with their imports.

This script verifies that:
1. Individual modules can be loaded
2. Imports are resolved correctly
3. The ontology structure is accessible
"""

from pathlib import Path
from owlready2 import get_ontology, default_world
import sys

def test_module_loading(owl_path: Path) -> tuple[bool, str, dict]:
    """
    Test loading a single OWL module.

    Args:
        owl_path: Path to the OWL file

    Returns:
        Tuple of (success, message, stats)
    """
    try:
        # Clear the world for a clean test
        default_world.ontologies.clear()

        # Load the ontology
        onto = get_ontology(f"file://{owl_path.as_posix()}").load()

        # Gather statistics
        stats = {
            "classes": len(list(onto.classes())),
            "object_properties": len(list(onto.object_properties())),
            "data_properties": len(list(onto.data_properties())),
            "individuals": len(list(onto.individuals())),
            "imports": len(onto.imported_ontologies),
        }

        return True, "✓ Loaded successfully", stats

    except FileNotFoundError as e:
        return False, f"✗ Import not found: {e}", {}
    except Exception as e:
        return False, f"✗ Error: {type(e).__name__}: {str(e)[:100]}", {}


def main():
    # Get the fixed OntoCAPE directory
    script_dir = Path(__file__).parent
    ontocape_dir = script_dir / "OntoCAPE_fixed"

    if not ontocape_dir.exists():
        print(f"❌ Error: OntoCAPE_fixed directory not found at {ontocape_dir}")
        print("Run fix_imports.py first!")
        return 1

    print("=" * 80)
    print("TESTING OntoCAPE MODULE LOADING")
    print("=" * 80)
    print(f"\nOntoCAPE directory: {ontocape_dir}")
    print()

    # Test key modules in dependency order
    test_modules = [
        # Upper level (foundational)
        "upper_level/system.owl",
        "upper_level/coordinate_system.owl",
        "upper_level/network_system.owl",
        "upper_level/tensor_quantity.owl",

        # Supporting concepts
        "supporting_concepts/physical_dimension/physical_dimension.owl",
        "supporting_concepts/SI_unit/SI_unit.owl",
        "supporting_concepts/SI_unit/derived_SI_units.owl",
        "supporting_concepts/space_and_time/space_and_time.owl",
        "supporting_concepts/geometry/geometry.owl",
        "supporting_concepts/mathematical_relation/mathematical_relation.owl",

        # Material
        "material/material.owl",
        "material/substance/substance.owl",
        "material/substance/molecular_structure.owl",
        "material/substance/chemical_species.owl",

        # Chemical process system
        "chemical_process_system/chemical_process_system.owl",
        "chemical_process_system/CPS_function/process.owl",
        "chemical_process_system/CPS_realization/plant.owl",
        "chemical_process_system/process_units/chemical_reactor.owl",

        # Models
        "model/mathematical_model.owl",
        "model/process_model.owl",

        # Main ontology
        "OntoCAPE.owl",
    ]

    results = []
    total_stats = {
        "classes": 0,
        "object_properties": 0,
        "data_properties": 0,
        "individuals": 0,
        "imports": 0,
    }

    print("Testing module loading:")
    print("-" * 80)

    for module_path in test_modules:
        full_path = ontocape_dir / module_path
        if not full_path.exists():
            results.append((module_path, False, "File not found", {}))
            print(f"⚠ SKIP: {module_path} (file not found)")
            continue

        success, message, stats = test_module_loading(full_path)
        results.append((module_path, success, message, stats))

        # Update totals
        if success:
            for key in total_stats:
                total_stats[key] = max(total_stats[key], stats.get(key, 0))

        # Print result
        status = "✓" if success else "✗"
        print(f"{status} {module_path}")
        if success and stats:
            print(f"  └─ {stats['classes']} classes, {stats['object_properties']} obj props, "
                  f"{stats['data_properties']} data props, {stats['individuals']} individuals, "
                  f"{stats['imports']} imports")
        if not success:
            print(f"  └─ {message}")

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    successful = sum(1 for _, success, _, _ in results if success)
    failed = len(results) - successful

    print(f"✓ Successfully loaded: {successful}/{len(results)} modules")
    print(f"✗ Failed: {failed}/{len(results)} modules")
    print()

    if successful > 0:
        print("Maximum counts across all modules:")
        print(f"  Classes: {total_stats['classes']}")
        print(f"  Object properties: {total_stats['object_properties']}")
        print(f"  Data properties: {total_stats['data_properties']}")
        print(f"  Individuals: {total_stats['individuals']}")
        print(f"  Imports: {total_stats['imports']}")

    if failed > 0:
        print()
        print("Failed modules:")
        for module_path, success, message, _ in results:
            if not success:
                print(f"  ✗ {module_path}: {message}")
        return 1

    print()
    print("✅ ALL MODULES LOADED SUCCESSFULLY")
    print("The import structure is working correctly!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
