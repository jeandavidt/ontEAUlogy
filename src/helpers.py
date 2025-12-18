"""This module contains utility functions used to build and explore the ontology"""
from pathlib import Path


def get_project_root(current_path: Path, project_name:str) -> Path:
    """goes up the file system tree until it finds the project name.
    If it is not found, the funciton returns a NameError."""
    current_path.absolute()
    parent_path = current_path.parent
    while current_path != parent_path:
        if parent_path.name == project_name:
            return parent_path
        current_path = parent_path
        parent_path = current_path.parent
    raise NameError(f"{project_name} not found in the file tree.")


def get_ontology_path() -> Path:
    try:
        root = get_project_root(Path(__file__), "waterFRAME")
    except NameError:
        # Fallback for when directory hasn't been renamed yet
        try:
            root = get_project_root(Path(__file__), "ontEAUlogy")
        except NameError:
            raise NameError(
                "Project directory not found (looking for waterFRAME or ontEAUlogy)."
            )
    return root / "data/ontology/waterframe.ttl"
