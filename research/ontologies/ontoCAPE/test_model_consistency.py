"""
Test consistency of OntoCAPE model modules specifically.

This script isolates the mathematical model portion of OntoCAPE to determine
if it can be used independently for waterFRAME's needs (ASM/ADM model representation).

Tests:
1. Load only model-related modules and their dependencies
2. Create test instances of MathematicalModel, ModelVariable, Parameter
3. Run reasoner to check consistency
4. Report whether model modules are usable
"""

from pathlib import Path
from owlready2 import (
    get_ontology,
    default_world,
    sync_reasoner_pellet,
    OwlReadyInconsistentOntologyError,
)
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
    print("OntoCAPE MODEL MODULES CONSISTENCY TEST")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("GOAL: Determine if model/ modules are consistent for use in waterFRAME")
    print()

    # Load model modules with minimal dependencies
    print("Loading model modules...")
    print("-" * 80)

    model_modules = [
        "model/mathematical_model.owl",
        "model/process_model.owl",
    ]

    loaded_ontos = []

    for module_path in model_modules:
        full_path = ontocape_fixed / module_path
        if not full_path.exists():
            print(f"⚠ Warning: {module_path} not found")
            continue

        print(f"Loading: {module_path}")
        try:
            onto = get_ontology(f"file://{full_path.as_posix()}").load()
            loaded_ontos.append(onto)
            print(f"  ✓ Loaded {module_path}")
        except Exception as e:
            print(f"  ✗ Failed to load {module_path}: {e}")
            return 1

    if not loaded_ontos:
        print("❌ No model modules loaded!")
        return 1

    print(f"✓ Successfully loaded {len(loaded_ontos)} model modules")
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

    # Find model-specific classes
    print("Finding model-related classes...")
    print("-" * 80)

    MathematicalModel_class = None
    ProcessModel_class = None
    ModelVariable_class = None
    Parameter_class = None
    System_class = None

    for cls in all_classes:
        class_name = cls.name if hasattr(cls, "name") else str(cls).split(".")[-1]

        if class_name == "MathematicalModel":
            MathematicalModel_class = cls
            print(f"✓ Found: {class_name}")
        elif class_name == "ProcessModel":
            ProcessModel_class = cls
            print(f"✓ Found: {class_name}")
        elif class_name == "ModelVariable":
            ModelVariable_class = cls
            print(f"✓ Found: {class_name}")
        elif class_name == "Parameter":
            Parameter_class = cls
            print(f"✓ Found: {class_name}")
        elif class_name == "System":
            System_class = cls
            print(f"✓ Found: {class_name} (dependency)")

    print()

    # Create test instances representing an ASM-like model
    print("Creating test instances (simulating ASM1 model)...")
    print("-" * 80)

    created_instances = []

    if not loaded_ontos:
        print("❌ No ontology loaded to create instances in")
        return 1

    # Use first loaded ontology as namespace
    primary_onto = loaded_ontos[0]

    with primary_onto:
        # Create a mathematical model instance
        if MathematicalModel_class:
            asm1_model = MathematicalModel_class("ASM1_Model")
            created_instances.append(asm1_model)
            print(f"✓ Created: ASM1_Model (type: MathematicalModel)")
        else:
            print("⚠ Warning: MathematicalModel class not found")

        # Create a process model instance
        if ProcessModel_class:
            wwtp_model = ProcessModel_class("WWTP_ProcessModel")
            created_instances.append(wwtp_model)
            print(f"✓ Created: WWTP_ProcessModel (type: ProcessModel)")
        else:
            print("⚠ Warning: ProcessModel class not found")

        # Create model variables
        if ModelVariable_class:
            substrate_var = ModelVariable_class("Substrate_S")
            biomass_var = ModelVariable_class("Biomass_X")
            created_instances.append(substrate_var)
            created_instances.append(biomass_var)
            print(f"✓ Created: Substrate_S (type: ModelVariable)")
            print(f"✓ Created: Biomass_X (type: ModelVariable)")
        else:
            print("⚠ Warning: ModelVariable class not found")

        # Create parameters
        if Parameter_class:
            mu_max = Parameter_class("mu_max")
            Y_yield = Parameter_class("Y_yield")
            created_instances.append(mu_max)
            created_instances.append(Y_yield)
            print(f"✓ Created: mu_max (type: Parameter)")
            print(f"✓ Created: Y_yield (type: Parameter)")
        else:
            print("⚠ Warning: Parameter class not found")

        # Create a system (what the model models)
        if System_class:
            bioreactor = System_class("BioreactorSystem")
            created_instances.append(bioreactor)
            print(f"✓ Created: BioreactorSystem (type: System)")
        else:
            print("⚠ Warning: System class not found")

    print(f"\n✓ Created {len(created_instances)} test instances")
    print()

    # Verify instances exist
    all_individuals_before = list(default_world.individuals())
    print(f"Total individuals in world: {len(all_individuals_before)}")
    print()

    if len(all_individuals_before) == 0:
        print("❌ ERROR: Failed to create instances!")
        return 1

    # Run the reasoner
    print("Running Pellet reasoner on MODEL MODULES ONLY...")
    print("-" * 80)
    print("Checking for:")
    print("  - Consistency of model-related axioms")
    print("  - Whether model modules are usable in isolation")
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
        print(
            f"Individuals: {len(all_individuals_after)} (before: {len(all_individuals_before)})"
        )
        print()

        # Check instance types after reasoning
        print("Instance classifications after reasoning:")
        print("-" * 80)
        for ind in created_instances:
            types = [t.name if hasattr(t, "name") else str(t) for t in ind.is_a]
            print(f"{ind.name}:")
            for t in types:
                print(f"  - {t}")

        print()
        print("=" * 80)
        print("✅ MODEL MODULES CONSISTENCY TEST RESULTS")
        print("=" * 80)
        print("✅ MODEL MODULES ARE CONSISTENT")
        print(f"✅ Successfully reasoned over {len(all_individuals_after)} individuals")
        print("✅ No logical contradictions in model modules")
        print()
        print("CONCLUSION:")
        print("The model/ modules (mathematical_model.owl, process_model.owl) are")
        print("logically sound and CAN BE USED for waterFRAME to represent ASM/ADM models.")
        print()
        print("RECOMMENDATION:")
        print("Import only the model/ modules and their minimal dependencies")
        print("(system.owl, supporting_concepts) to avoid the inconsistencies")
        print("present in the full OntoCAPE ontology (likely in material/ or")
        print("chemical_process_system/ modules).")
        return 0

    except OwlReadyInconsistentOntologyError as e:
        print()
        print("=" * 80)
        print("❌ MODEL MODULES ARE INCONSISTENT")
        print("=" * 80)
        print(f"Error: {e}")
        print()
        print("CONCLUSION:")
        print("The model/ modules contain logical contradictions even in isolation.")
        print("OntoCAPE's model representation cannot be used directly for waterFRAME.")
        print()
        print("RECOMMENDATION:")
        print("Extract the modeling patterns manually (classes, properties) without")
        print("importing the ontology, or use alternative model representation approaches.")
        return 1

    except Exception as e:
        print(f"✗ Reasoner failed: {type(e).__name__}")
        print(f"  Error: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
