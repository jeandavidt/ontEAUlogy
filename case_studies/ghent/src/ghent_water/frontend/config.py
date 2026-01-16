"""Frontend configuration settings."""

import os
from typing import Optional


class Config:
    """Configuration class for the Streamlit frontend."""

    # API settings
    ORCHESTRATOR_URL: str = os.getenv("ORCHESTRATOR_URL", "http://localhost:8000")
    API_TIMEOUT: int = 30  # seconds
    
    # Map settings
    MAP_CENTER_LAT: float = 51.055
    MAP_CENTER_LON: float = 3.743
    MAP_ZOOM: int = 14
    MAP_HEIGHT: int = 500
    
    # UI settings
    PAGE_TITLE: str = "Ghent Water System Explorer"
    PAGE_ICON: str = "💧"
    
    # Session state keys
    KEY_SELECTED_ENTITY: str = "selected_entity"
    KEY_QUERY_RESULTS: str = "query_results"
    KEY_LAST_QUERY_TYPE: str = "last_query_type"
    KEY_JOBS: str = "jobs"


# Global config instance
config = Config()


def get_orchestrator_url() -> str:
    """Get the orchestrator base URL.
    
    Returns:
        The configured orchestrator URL.
    """
    return Config.ORCHESTRATOR_URL


def set_orchestrator_url(url: str) -> None:
    """Set the orchestrator base URL.
    
    Args:
        url: The new orchestrator URL.
    """
    Config.ORCHESTRATOR_URL = url
