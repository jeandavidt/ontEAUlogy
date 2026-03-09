"""Household orchestrator - Uses ontEAUlogy_core for orchestration.

This module creates a FastAPI orchestrator for the household case study
using the reusable ontEAUlogy_core components.
"""

import logging
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_household_orchestrator(config_path: Optional[Path] = None):
    """Create the household case study orchestrator.
    
    Args:
        config_path: Optional path to YAML configuration file.
                    If None, uses default config from household/config/
    
    Returns:
        Configured FastAPI application
    """
    from ontEAUlogy_core.main import create_app
    
    if config_path is None:
        # Use default household config
        config_path = Path(__file__).parent.parent.parent.parent / "config" / "orchestrator.yaml"
    
    return create_app(config_path)


# Default app instance (used by uvicorn)
default_config_path = Path(__file__).parent.parent.parent.parent / "config" / "orchestrator.yaml"
app = create_household_orchestrator(default_config_path)


def run():
    """Run the orchestrator (entry point for CLI)."""
    import uvicorn
    import sys
    
    # Check for config path argument
    config_path: Optional[Path] = None
    if len(sys.argv) > 1:
        config_path = Path(sys.argv[1])
    
    # Create app with config
    application = create_household_orchestrator(config_path)
    
    # Run server
    uvicorn.run(application, host="0.0.0.0", port=8080, log_level="info")


if __name__ == "__main__":
    run()
