"""CLI entry point for household orchestrator.

Usage:
    python -m household_water.runners.orchestrator_runner [--port 8080]
"""

import argparse
import uvicorn


def main():
    parser = argparse.ArgumentParser(description="Run household orchestrator")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    args = parser.parse_args()

    uvicorn.run(
        "household_water.orchestrator:app",
        host=args.host,
        port=args.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
