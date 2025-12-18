"""
Test OntoCAPE consistency by architectural layers.

Following OntoCAPE's modular architecture:
- Layer 1: Meta-model (foundational concepts)
- Layer 2: Upper level (system, network, coordinate system)
- Layer 3: Supporting concepts (physical dimensions, SI units, space/time, geometry)
- Layer 4: Domain level (material, chemical process system)
- Layer 5: Application level (process models, specific applications)

This tests each layer independently and cumulatively to identify where inconsistencies arise.
"""

from pathlib import Path
from owlready2 import get_ontology, default_world, sync_reasoner_pellet, OwlReadyInconsistentOntologyError
import sys
from datetime import datetime

def test_layer(layer_name: str, modules: list, ontocape_fixed: Path, create_instances: bool = True):
    """
    Test a specific architectural layer for consistency.

    Args:
        layer_name: Name of the layer being tested
        modules: List of module paths to load
        ontocape_fixed: Path to OntoCAPE_fixed directory
        create_instances: Whether to create test instances

    Returns:
        Tuple of (consistent: bool, error_msg: str, stats: dict)
    """
    print(f"\n{'='*80}")
    print(f"TESTING LAYER: {layer_name}")
    print(f"{'='*80}")

    # Note: We can't clear the world, so each test is cumulative
    # For true isolation, would need to run each test in a separate process

    # Load modules
    print(f"\nLoading {len(modules)} modules:")
    loaded_ontos = []
    for module_path in modules:
        full_path = ontocape_fixed / module_path
        if not full_path.exists():
            print(f"  ⚠ SKIP: {module_path} (not found)")
            continue
        print(f"  Loading: {module_path}")
        onto = get_ontology(f"file://{full_path.as_posix()}").load()
        loaded_ontos.append((module_path, onto))

    # Gather statistics
    all_classes = list(default_world.classes())
    all_obj_props = list(default_world.object_properties())
    all_data_props = list(default_world.data_properties())

    stats = {
        "modules_loaded": len(loaded_ontos),
        "classes": len(all_classes),
        "object_properties": len(all_obj_props),
        "data_properties": len(all_data_props),
        "individuals": 0
    }

    print(f"\nStatistics:")
    print(f"  Modules loaded: {stats['modules_loaded']}")
    print(f"  Classes: {stats['classes']}")
    print(f"  Object properties: {stats['object_properties']}")
    print(f"  Data properties: {stats['data_properties']}")

    # Create test instances if requested
    created_instances = []
    if create_instances and loaded_ontos:
        print(f"\nCreating test instances...")

        # Find key classes to instantiate
        System_class = None
        ChemicalSpecies_class = None

        for cls in all_classes:
            class_name = cls.name if hasattr(cls, 'name') else str(cls).split('.')[-1]
            if class_name == "System" and not System_class:
                System_class = cls
            elif "ChemicalSpecies" in class_name and not ChemicalSpecies_class:
                ChemicalSpecies_class = cls

        # Create instances
        _, first_onto = loaded_ontos[0]
        with first_onto:
            if System_class:
                inst = System_class(f"TestSystem_{layer_name.replace(' ', '_')}")
                created_instances.append(inst)
                print(f"  ✓ Created: {inst.name}")

            if ChemicalSpecies_class:
                inst = ChemicalSpecies_class(f"TestSpecies_{layer_name.replace(' ', '_')}")
                created_instances.append(inst)
                print(f"  ✓ Created: {inst.name}")

        stats["individuals"] = len(list(default_world.individuals()))
        print(f"  Total individuals: {stats['individuals']}")

    # Run reasoner
    print(f"\nRunning Pellet reasoner...")
    try:
        sync_reasoner_pellet(debug=0)  # debug=0 to reduce output
        print(f"✅ CONSISTENT - No logical contradictions")
        return True, None, stats

    except OwlReadyInconsistentOntologyError as e:
        error_msg = str(e)
        print(f"❌ INCONSISTENT - Logical contradictions found")
        # Extract key error info
        if "Invalid list structure" in error_msg:
            print(f"  Issue: Malformed RDF lists")
        if "transitivity" in error_msg:
            print(f"  Issue: Transitivity axiom conflicts")
        if "cardinality" in error_msg:
            print(f"  Issue: Cardinality restriction conflicts")
        return False, error_msg, stats

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)[:200]}"
        print(f"⚠ ERROR - {error_msg}")
        return False, error_msg, stats


def main():
    script_dir = Path(__file__).parent
    ontocape_fixed = script_dir / "OntoCAPE_fixed"

    if not ontocape_fixed.exists():
        print(f"❌ Error: OntoCAPE_fixed directory not found")
        return 1

    print("="*80)
    print("OntoCAPE MODULAR CONSISTENCY TESTING")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nStrategy: Test each architectural layer independently")
    print("to identify where inconsistencies originate.")

    # Define architectural layers
    layers = [
        ("Layer 1: Meta-model", [
            "meta_model/meta_model.owl",
        ]),

        ("Layer 2: Upper Level", [
            "upper_level/system.owl",
            "upper_level/network_system.owl",
            "upper_level/coordinate_system.owl",
        ]),

        ("Layer 3: Supporting Concepts - Mathematical", [
            "supporting_concepts/mathematical_relation/mathematical_relation.owl",
        ]),

        ("Layer 3: Supporting Concepts - Physical", [
            "supporting_concepts/physical_dimension/physical_dimension.owl",
            "supporting_concepts/SI_unit/SI_unit.owl",
            "supporting_concepts/SI_unit/derived_SI_units.owl",
        ]),

        ("Layer 3: Supporting Concepts - Spatial/Temporal", [
            "supporting_concepts/space_and_time/space_and_time.owl",
            "supporting_concepts/geometry/geometry.owl",
        ]),

        ("Layer 4: Material Domain", [
            "material/substance/substance.owl",
            "material/substance/molecular_structure.owl",
        ]),

        ("Layer 4: Material + Phase System", [
            "material/substance/substance.owl",
            "material/phase_system/phase_system.owl",
            "material/material.owl",
        ]),

        ("Layer 4: Chemical Process System - Function", [
            "chemical_process_system/CPS_function/process.owl",
        ]),

        ("Layer 4: Chemical Process System - Realization", [
            "chemical_process_system/CPS_realization/plant.owl",
            "chemical_process_system/CPS_realization/plant_equipment/apparatus.owl",
        ]),

        ("Layer 5: Models", [
            "model/mathematical_model.owl",
            "model/process_model.owl",
        ]),

        ("Full Stack: Upper + Supporting + Material", [
            "upper_level/system.owl",
            "supporting_concepts/physical_dimension/physical_dimension.owl",
            "supporting_concepts/SI_unit/SI_unit.owl",
            "material/substance/substance.owl",
        ]),

        ("Full Stack: + Process System", [
            "upper_level/system.owl",
            "supporting_concepts/physical_dimension/physical_dimension.owl",
            "supporting_concepts/SI_unit/SI_unit.owl",
            "material/substance/substance.owl",
            "chemical_process_system/CPS_function/process.owl",
        ]),
    ]

    # Run tests
    results = []
    for layer_name, modules in layers:
        consistent, error, stats = test_layer(layer_name, modules, ontocape_fixed, create_instances=True)
        results.append((layer_name, consistent, error, stats))

        # Stop if we find an inconsistency (to avoid redundant tests)
        # Comment this out if you want to test all layers regardless
        # if not consistent:
        #     print(f"\n⚠ Stopping tests - found inconsistency in: {layer_name}")
        #     break

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY - CONSISTENCY BY LAYER")
    print(f"{'='*80}\n")

    consistent_count = sum(1 for _, c, _, _ in results if c)
    inconsistent_count = len(results) - consistent_count

    for layer_name, consistent, error, stats in results:
        status = "✅ CONSISTENT" if consistent else "❌ INCONSISTENT"
        print(f"{status} - {layer_name}")
        print(f"  Modules: {stats['modules_loaded']}, Classes: {stats['classes']}, "
              f"Individuals: {stats['individuals']}")
        if not consistent and error:
            # Show brief error
            if "Invalid list" in error:
                print(f"  Error: Invalid RDF list structure")
            if "transitivity" in error:
                print(f"  Error: Transitivity axiom conflict")
            print()

    print(f"\n{'='*80}")
    print(f"✅ Consistent layers: {consistent_count}/{len(results)}")
    print(f"❌ Inconsistent layers: {inconsistent_count}/{len(results)}")
    print(f"{'='*80}\n")

    if inconsistent_count > 0:
        print("FINDINGS:")
        print("The ontology has consistency issues that arise in specific modules.")
        print("Review the results above to identify problematic modules.")
        return 1
    else:
        print("✅ All tested layers are consistent!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
