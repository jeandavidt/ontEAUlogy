#!/usr/bin/env python3
"""
MkDocs Hook for Ontology Documentation Generation

This hook integrates the ontology documentation generation
into the MkDocs build process, ensuring that entity documentation
is always up-to-date when building the site.
"""

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

def on_pre_build(config, **kwargs):
    """
    MkDocs hook that runs before the build starts.
    Generates ontology documentation.

    Args:
        config: MkDocs configuration object
        **kwargs: Additional keyword arguments from MkDocs
    """
    if OntologyDocGenerator is None:
        print("Warning: Ontology documentation generator not available")
        return

    try:
        print("Generating ontology documentation...")
        generator = OntologyDocGenerator()

        # Generate index page
        generator.generate_index()

        # Generate entities documentation
        entities_file = generator.generate_all_docs()

        if entities_file:
            print(f"Generated entity documentation file: {entities_file}")
        else:
            print("Warning: Failed to generate entity documentation")

        return entities_file
    except Exception as e:
        print(f"Error generating ontology documentation: {e}")
        import traceback
        traceback.print_exc()
        return None
