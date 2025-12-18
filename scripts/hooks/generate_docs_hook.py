#!/usr/bin/env python3
"""
MkDocs Hook for Ontology Documentation Generation

This hook integrates the ontology documentation generation
into the MkDocs build process, ensuring that entity documentation
is always up-to-date when building the site.
"""

import subprocess
import sys
from pathlib import Path

# Add the parent directories to the path so we can import our modules
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
scripts_dir = project_root / "scripts"
src_dir = project_root / "src"

sys.path.insert(0, str(scripts_dir))
sys.path.insert(0, str(src_dir))

try:
    from generate_docs import OntologyDocGenerator
except ImportError as e:
    print(f"Warning: Could not import generate_docs: {e}")
    OntologyDocGenerator = None


def export_marimo_notebook(config):
    """
    Export marimo notebook to HTML for inclusion in docs.

    The notebook is exported to a temporary location in docs/notebook,
    which MkDocs will copy to the site directory during build.

    Args:
        config: MkDocs configuration object

    Returns:
        Path to exported notebook or None if failed
    """
    try:
        print("Exporting marimo notebook...")
        notebook_path = project_root / "notebooks" / "explore_ontology.py"
        # Export to docs/notebook so MkDocs can copy it to site/notebook
        output_dir = project_root / "docs" / "notebook"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Run marimo export command with --force to avoid prompts
        cmd = [
            "uv",
            "run",
            "marimo",
            "export",
            "html-wasm",
            str(notebook_path),
            "-o",
            str(output_dir),
            "--force",
        ]

        # Use stdin=subprocess.DEVNULL to prevent hanging on input
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            stdin=subprocess.DEVNULL,
            timeout=60,
        )

        print(f"Successfully exported marimo notebook to {output_dir}")
        print("MkDocs will copy it to site/notebook/ during build")
        return output_dir / "index.html"
    except subprocess.CalledProcessError as e:
        print(f"Error exporting marimo notebook: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return None
    except Exception as e:
        print(f"Error exporting marimo notebook: {e}")
        import traceback

        traceback.print_exc()
        return None


def on_pre_build(config, **kwargs):
    """
    MkDocs hook that runs before the build starts.
    Generates ontology documentation and exports marimo notebook.

    Args:
        config: MkDocs configuration object
        **kwargs: Additional keyword arguments from MkDocs
    """
    # Export marimo notebook
    notebook_export = export_marimo_notebook(config)
    if notebook_export:
        print(f"Exported marimo notebook: {notebook_export}")
    else:
        print("Warning: Failed to export marimo notebook")

    # Generate ontology documentation
    if OntologyDocGenerator is None:
        print("Warning: Ontology documentation generator not available")
        return

    try:
        print("Generating ontology documentation...")
        generator = OntologyDocGenerator()

        # Generate index page
        generator.generate_index()

        # Generate modular documentation
        module_files = generator.generate_modular_docs()

        if module_files:
            print(f"Generated {len(module_files)} module documentation pages")
        else:
            print("Warning: No module documentation generated")

        return module_files
    except Exception as e:
        print(f"Error generating ontology documentation: {e}")
        import traceback

        traceback.print_exc()
        return None
