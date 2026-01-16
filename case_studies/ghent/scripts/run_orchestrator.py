#!/usr/bin/env python3
"""Run the FastAPI orchestrator server."""
import argparse
import uvicorn
import sys
from pathlib import Path


def main():
    """Main entry point for running the orchestrator."""
    parser = argparse.ArgumentParser(
        description="Run the ontEAUlogy FastAPI orchestrator"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to bind to (default: 8080)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of workers (default: 1)"
    )
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="Log level (default: info)"
    )
    
    args = parser.parse_args()
    
    # Ensure we're running from the project root
    script_dir = Path(__file__).parent.parent
    if script_dir not in sys.path:
        sys.path.insert(0, str(script_dir))
    
    # Run the server
    uvicorn.run(
        "ghent_water.orchestrator.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers if not args.reload else 1,
        log_level=args.log_level
    )


if __name__ == "__main__":
    main()
