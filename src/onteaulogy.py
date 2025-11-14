"""This module contains utility functions used to build and explore the ontology"""
from pathlib import Path


def get_project_root(current_path: Path, project_name:str = "ontEAUlogy") -> Path:
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
        root = get_project_root(Path(__file__))
    except NameError:
        raise NameError("The default project name is different from the actual project name.")
    return root / "data/ontology/onteaulogy.ttl"
