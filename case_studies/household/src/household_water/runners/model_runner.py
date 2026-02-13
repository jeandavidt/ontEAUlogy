"""CLI entry point for household model services.

Usage:
    python -m household_water.runners.model_runner --model mbr [--port 8101]
    python -m household_water.runners.model_runner --model ro [--port 8102]
    python -m household_water.runners.model_runner --model infiltration [--port 8103]
"""

import argparse
import uvicorn


def main():
    parser = argparse.ArgumentParser(description="Run a household water model service")
    parser.add_argument(
        "--model",
        required=True,
        choices=["mbr", "ro", "infiltration"],
        help="Which model to run",
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=None, help="Port override (defaults to model default)")
    args = parser.parse_args()

    model_app_map = {
        "mbr": ("household_water.models.mbr:app", 8101),
        "ro": ("household_water.models.ro:app", 8102),
        "infiltration": ("household_water.models.infiltration:app", 8103),
    }

    app_import, default_port = model_app_map[args.model]
    port = args.port or default_port

    uvicorn.run(app_import, host=args.host, port=port, log_level="info")


if __name__ == "__main__":
    main()
