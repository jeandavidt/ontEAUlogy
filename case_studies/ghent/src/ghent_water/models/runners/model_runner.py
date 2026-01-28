#!/usr/bin/env python3
"""Model Runner - CLI to run individual water system models.

Usage:
    python -m ghent_water.models.runners.model_runner --model dwp1 --port 8001
    python -m ghent_water.models.runners.model_runner --model wwtp1 --port 8003 --reload

Supported models:
    - dwp1, dwp2: Drinking Water Plants
    - wwtp1, wwtp2: Wastewater Treatment Plants
    - texfin, foodpro, chiptech, pharmagen, brewco: Industries
    - dampoort, muide: Residential Districts
    - lieve_river: River segment
"""

import argparse
import asyncio
import sys
import uvicorn
from typing import Optional

# Import stub models
from ..stubs.dwp import create_dwp_model
from ..stubs.wwtp import create_wwtp_model
from ..stubs.industry import create_industry_model
from ..stubs.residential import create_residential_model
from ..stubs.river import create_river_model


# Model registry mapping
MODEL_REGISTRY = {
    # Drinking Water Plants
    "dwp1": ("DWP1", 8001, create_dwp_model),
    "dwp2": ("DWP2", 8002, create_dwp_model),
    # Wastewater Treatment Plants
    "wwtp1": ("WWTP1", 8003, create_wwtp_model),
    "wwtp2": ("WWTP2", 8004, create_wwtp_model),
    # Industries
    "texfin": ("Texfin", 8005, create_industry_model),
    "foodpro": ("FoodPro", 8006, create_industry_model),
    "chiptech": ("ChipTech", 8007, create_industry_model),
    "pharmagen": ("PharmaGen", 8008, create_industry_model),
    "brewco": ("BrewCo", 8009, create_industry_model),
    # Residential Districts
    "dampoort": ("Dampoort", 8011, create_residential_model),
    "muide": ("Muide", 8012, create_residential_model),
    # River
    "lieve_river": ("Lieve River", 8010, create_river_model),
}


def create_model(model_name: str, port: Optional[int] = None):
    """Create a model instance by name.

    Args:
        model_name: Name of the model (e.g., 'dwp1', 'wwtp1')
        port: Optional custom port override

    Returns:
        Configured model instance

    Raises:
        ValueError: If model name is not recognized
    """
    if model_name.lower() not in MODEL_REGISTRY:
        valid_models = list(MODEL_REGISTRY.keys())
        raise ValueError(
            f"Unknown model: {model_name}\n"
            f"Valid models: {', '.join(valid_models)}"
        )

    display_name, default_port, factory = MODEL_REGISTRY[model_name.lower()]
    actual_port = port or default_port

    # Use the registry key as the entity_id (the programmatic identifier)
    # The display_name from the registry is for human-readable output only
    return factory(entity_id=model_name.lower(), port=actual_port)


def run_model(model_name: str, port: Optional[int] = None, run_server: bool = True):
    """Run a model.

    Args:
        model_name: Name of the model to run
        port: Optional port override
        run_server: Whether to run as HTTP server (default: True)

    Returns:
        Model instance
    """
    model = create_model(model_name, port)

    if run_server:
        print(f"Starting {model.entity_name} on port {model.port}")
        print(f"  - Health: http://localhost:{model.port}/health")
        print(f"  - Describe: http://localhost:{model.port}/describe")
        print(f"  - Simulate: POST http://localhost:{model.port}/simulate")

        uvicorn.run(model.app, host="0.0.0.0", port=model.port, log_level="info")
    else:
        # Just return the model for programmatic use
        return model

    return model


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Run a water system model stub",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--model", "-m",
        type=str,
        required=True,
        help="Model to run (e.g., dwp1, wwtp1, texfin, dampoort, lieve_river)",
    )

    parser.add_argument(
        "--port", "-p",
        type=int,
        default=None,
        help="Port to run the model on (default: model's default port)",
    )

    parser.add_argument(
        "--no-server",
        action="store_true",
        help="Don't run as HTTP server (just create and return model)",
    )

    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )

    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on code changes",
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of workers (default: 1)",
    )

    args = parser.parse_args()

    try:
        model = create_model(args.model, args.port)

        if args.no_server:
            print(f"Model created: {model.entity_name} (ID: {model.entity_id})")
            print(f"  - Describe: {model.api_endpoint}/describe")
            print(f"  - Simulate: POST {model.api_endpoint}/simulate")
            return model

        print(f"Starting {model.entity_name} on port {model.port}")
        print(f"  - Health: http://localhost:{model.port}/health")
        print(f"  - Describe: http://localhost:{model.port}/describe")
        print(f"  - Simulate: POST http://localhost:{model.port}/simulate")

        uvicorn.run(
            model.app,
            host=args.host,
            port=model.port,
            reload=args.reload,
            workers=args.workers,
            log_level="info",
        )

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
