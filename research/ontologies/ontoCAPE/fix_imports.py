"""
Fix XML entity declarations in OntoCAPE OWL files to use proper file paths.

This script:
1. Copies the OntoCAPE directory to OntoCAPE_fixed
2. Replaces Windows-specific file:///C:/OntoCAPE/ references with proper file:// URIs
"""

from pathlib import Path
import shutil
import re


def fix_owl_file(file_path: Path, root_dir: Path) -> bool:
    """
    Fix XML entity declaration in a single OWL file.

    Args:
        file_path: Path to the OWL file to fix
        root_dir: Root directory of the fixed OntoCAPE ontology (OntoCAPE_fixed)

    Returns:
        True if file was modified, False otherwise
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Try with latin-1 encoding as fallback
        content = file_path.read_text(encoding="latin-1")

    original_content = content

    # Pattern 1: Replace <!ENTITY root "file:/C:/OntoCAPE/">
    # We'll use the absolute path to the OntoCAPE_fixed directory
    old_pattern = r'<!ENTITY root "file:/C:/OntoCAPE/">'
    new_value = f'<!ENTITY root "file://{root_dir.as_posix()}/">'
    content = re.sub(old_pattern, new_value, content)

    # Pattern 2: Sometimes there are triple slashes
    old_pattern2 = r'<!ENTITY root "file:///C:/OntoCAPE/">'
    content = re.sub(old_pattern2, new_value, content)

    # Pattern 3: Remove the extra "OntoCAPE/" prefix from entity references
    # Replace &root;OntoCAPE/... with &root;...
    entity_pattern = r'(&root;)OntoCAPE/([^"]+)'
    content = re.sub(entity_pattern, r"\1\2", content)

    # Pattern 4: Replace all hardcoded Windows file paths with absolute paths
    # Replace file:/C:/OntoCAPE/OntoCAPE/... with absolute paths
    windows_pattern = r'file:/C:/OntoCAPE/OntoCAPE/([^"]+)'
    new_abs_path = f"file://{root_dir.as_posix()}/\\1"
    content = re.sub(windows_pattern, new_abs_path, content)

    # Pattern 5: Also handle triple slash Windows paths
    windows_pattern2 = r'file:///C:/OntoCAPE/OntoCAPE/([^"]+)'
    content = re.sub(windows_pattern2, new_abs_path, content)

    # Check if we made any changes
    if content != original_content:
        file_path.write_text(content, encoding="utf-8")
        return True

    return False


def main():
    # Get the directories
    script_dir = Path(__file__).parent
    source_dir = script_dir / "OntoCAPE"
    target_dir = script_dir / "OntoCAPE_fixed"

    if not source_dir.exists():
        print(f"❌ Error: Source directory not found at {source_dir}")
        return

    print("=" * 80)
    print("FIXING OntoCAPE IMPORT PATHS")
    print("=" * 80)

    # Step 1: Copy directory
    if target_dir.exists():
        print(f"\n⚠ Target directory already exists: {target_dir}")
        print("Removing existing directory...")
        shutil.rmtree(target_dir)

    print(f"\nCopying OntoCAPE to OntoCAPE_fixed...")
    shutil.copytree(source_dir, target_dir)
    print(f"✓ Copied to: {target_dir}")

    # Step 2: Fix all OWL files in the copied directory
    print(f"\nNew root entity will be: file://{target_dir.as_posix()}/")
    print()

    # Find all OWL files in the target directory
    owl_files = list(target_dir.rglob("*.owl"))
    print(f"Found {len(owl_files)} OWL files to fix")
    print()

    # Fix each file
    fixed_count = 0
    unchanged_count = 0

    for owl_file in owl_files:
        relative_path = owl_file.relative_to(target_dir)
        if fix_owl_file(owl_file, target_dir):
            print(f"✓ Fixed: {relative_path}")
            fixed_count += 1
        else:
            unchanged_count += 1

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✓ Fixed: {fixed_count} files")
    print(f"- Unchanged: {unchanged_count} files")
    print(f"✓ Total: {len(owl_files)} files processed")
    print()
    print(f"Fixed ontology available at: {target_dir}")
    print("All import paths have been updated to use absolute file:// URIs")
    print("The ontology should now be loadable with owlready2 or rdflib")


if __name__ == "__main__":
    main()
