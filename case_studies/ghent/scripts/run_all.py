#!/usr/bin/env python3
"""
Run all Ghent Water System components.

This script starts:
1. The orchestrator (FastAPI) on port 8080
2. All model services (DWP-1, WWTP-1, DWP-2, WWTP-2, Lieve River, Industries, Residential)
3. The React frontend on port 3000

Usage:
    python run_all.py              # Run with default settings
    python run_all.py --no-frontend  # Skip the frontend
    python run_all.py --port 3000    # Use custom frontend port
    python run_all.py --kill        # Kill all running components
    python run_all.py --restart     # Kill and restart all components
"""

import argparse
import httpx
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

# Add project root to path
script_path = Path(__file__).resolve()
project_root = script_path.parent.parent  # scripts/ -> ghent/ (project root)

sys.path.insert(0, str(project_root))

# Load environment variables from .env file at startup
from dotenv import load_dotenv

env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"Loaded environment from {env_path}")
else:
    print(f"Note: No .env file found at {env_path}")

# Get environment for subprocesses (includes .env vars)
ENV = os.environ.copy()

# PID file to track running processes
PID_FILE = project_root / ".ghent_water_pids"


def save_pids(processes: list) -> None:
    """Save process PIDs to a file for later management."""
    with open(PID_FILE, "w") as f:
        for name, p in processes:
            f.write(f"{name},{p.pid}\n")


def load_pids() -> dict:
    """Load PIDs from file."""
    pids = {}
    if PID_FILE.exists():
        with open(PID_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    name, pid = line.split(",")
                    pids[name] = int(pid)
    return pids


def wait_for_service(
    url: str, timeout: float = 30.0, service_name: str = "service"
) -> bool:
    """Wait for a service to become available.

    Args:
        url: URL of the service health endpoint.
        timeout: Maximum time to wait in seconds.
        service_name: Name of the service for display purposes.

    Returns:
        True if service is available, False if timeout.
    """
    print(f"  Waiting for {service_name} at {url}...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = httpx.get(url, timeout=2.0)
            if resp.status_code == 200:
                print(f"  ✓ {service_name} is ready!")
                return True
        except httpx.ConnectError:
            pass
        except httpx.TimeoutException:
            pass
        time.sleep(0.5)

    print(f"  ✗ {service_name} failed to start within {timeout}s")
    return False


def kill_all() -> None:
    """Kill all running components using lsof to find processes by port."""
    # Define all ports used by the system
    PORTS = [
        8080,  # orchestrator
        8001,  # dwp1
        8002,  # dwp2
        8003,  # wwtp1
        8004,  # wwtp2
        8005,  # texfin
        8006,  # foodpro
        8007,  # chiptech
        8008,  # pharmagen
        8009,  # brewco
        8010,  # lieve_river
        8011,  # dampoort
        8012,  # muide
        3000,  # frontend
    ]

    print("Killing all processes on configured ports...")
    killed_any = False

    for port in PORTS:
        try:
            # Find processes using this port
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split("\n")
                for pid in pids:
                    if pid:
                        try:
                            pid_int = int(pid)
                            os.kill(pid_int, signal.SIGKILL)
                            print(f"  - Killed PID {pid_int} on port {port}")
                            killed_any = True
                        except (ProcessLookupError, ValueError, PermissionError) as e:
                            print(f"  - Error killing PID {pid} on port {port}: {e}")
            # If no processes found, lsof returns non-zero - that's OK
        except FileNotFoundError:
            print("  - Error: lsof command not found. Please install lsof.")
            return
        except Exception as e:
            print(f"  - Error checking port {port}: {e}")

    if killed_any:
        print("\nWaiting for processes to terminate...")
        time.sleep(1)

    # Clean up PID file
    if PID_FILE.exists():
        PID_FILE.unlink()

    print("All components killed.\n")


def run_orchestrator(port: int = 8080, host: str = "0.0.0.0") -> None:
    """Run the orchestrator service."""
    orchestrator_script = project_root / "scripts" / "run_orchestrator.py"
    cmd = [
        sys.executable,
        str(orchestrator_script),
        "--host",
        host,
        "--port",
        str(port),
    ]
    subprocess.Popen(cmd, cwd=str(project_root), env=ENV)


def run_model(model_name: str, port: int) -> None:
    """Run a model service."""
    cmd = [
        sys.executable,
        "-m",
        "ghent_water.models.runners.model_runner",
        "--model",
        model_name,
        "--port",
        str(port),
    ]
    subprocess.Popen(cmd, cwd=str(project_root), env=ENV)


def run_frontend(port: int = 3000, host: str = "0.0.0.0") -> None:
    """Run the React frontend."""
    frontend_dir = project_root / "frontend-react"
    cmd = ["npm", "run", "dev", "--", "--port", str(port), "--host", host]
    print(f"  Starting React frontend: {' '.join(cmd)}")
    subprocess.Popen(cmd, cwd=str(frontend_dir), env=ENV)


# Model configuration: (model_name, port, enabled_by_default)
MODELS = [
    ("dwp1", 8001, True),
    ("dwp2", 8002, True),
    ("wwtp1", 8003, True),
    ("wwtp2", 8004, True),
    ("texfin", 8005, True),
    ("foodpro", 8006, True),
    ("chiptech", 8007, True),
    ("pharmagen", 8008, True),
    ("brewco", 8009, True),
    ("lieve_river", 8010, True),
    ("dampoort", 8011, True),
    ("muide", 8012, True),
]


def main():
    parser = argparse.ArgumentParser(
        description="Run the Ghent Water System case study",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--orchestrator-port",
        type=int,
        default=8080,
        help="Port for the orchestrator (default: 8080)",
    )

    parser.add_argument(
        "--frontend-port",
        type=int,
        default=3000,
        help="Port for the frontend (default: 3000)",
    )

    parser.add_argument(
        "--no-frontend",
        action="store_true",
        help="Skip starting the frontend",
    )

    parser.add_argument(
        "--models",
        nargs="+",
        default=None,
        help="Specific models to run (default: all models)",
    )

    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )

    parser.add_argument(
        "--kill",
        action="store_true",
        help="Kill all running components",
    )

    parser.add_argument(
        "--restart",
        action="store_true",
        help="Kill all running components and restart them",
    )

    args = parser.parse_args()

    # Handle --kill first (can be combined with other options)
    if args.kill:
        kill_all()
        if not args.restart:
            return

    # Handle --restart
    if args.restart:
        kill_all()
        # Small delay to allow processes to fully terminate
        time.sleep(1)

    print("=" * 60)
    print("Ghent Water System - Starting All Components")
    print("=" * 60)
    print()

    # Determine which models to run
    if args.models is not None:
        models_to_run = []
        for model in MODELS:
            if model[0] in args.models:
                models_to_run.append(model)
    else:
        models_to_run = [m for m in MODELS if m[2]]

    # Start processes
    processes = []

    # 1. Start orchestrator
    print(f"[1/3] Starting orchestrator on port {args.orchestrator_port}...")
    p = subprocess.Popen(
        [
            sys.executable,
            str(project_root / "scripts" / "run_orchestrator.py"),
            "--host",
            args.host,
            "--port",
            str(args.orchestrator_port),
        ],
        cwd=str(project_root),
        env=ENV,
    )
    processes.append(("orchestrator", p))

    # Wait for orchestrator to be ready
    orchestrator_url = f"http://localhost:{args.orchestrator_port}/health"
    if not wait_for_service(
        orchestrator_url, timeout=30.0, service_name="orchestrator"
    ):
        print("ERROR: Orchestrator failed to start. Exiting.")
        return

    # 2. Start models
    print(f"[2/3] Starting {len(models_to_run)} model services...")
    for model_name, port, _ in models_to_run:
        print(f"  - Starting {model_name} on port {port}...")
        cmd = [
            sys.executable,
            "-m",
            "ghent_water.models.runners.model_runner",
            "--model",
            model_name,
            "--port",
            str(port),
        ]
        p = subprocess.Popen(cmd, cwd=str(project_root), env=ENV)
        processes.append((model_name, p))

        # Wait for model to be ready
        model_url = f"http://localhost:{port}/health"
        wait_for_service(model_url, timeout=10.0, service_name=model_name)

    # 3. Start frontend (if not disabled)
    if not args.no_frontend:
        print(f"[3/3] Starting React frontend on port {args.frontend_port}...")
        frontend_dir = project_root / "frontend-react"
        cmd = [
            "npm",
            "run",
            "dev",
            "--",
            "--port",
            str(args.frontend_port),
            "--host",
            args.host,
        ]
        p = subprocess.Popen(cmd, cwd=str(frontend_dir), env=ENV)
        processes.append(("frontend", p))

        # Wait for frontend to be ready
        frontend_url = f"http://localhost:{args.frontend_port}"
        wait_for_service(frontend_url, timeout=15.0, service_name="React frontend")
    else:
        print("[3/3] Frontend disabled (--no-frontend)")

    # Save PIDs for later management
    save_pids(processes)

    print()
    print("=" * 60)
    print("All components started successfully!")
    print("=" * 60)
    print()
    print("Access points:")
    print(f"  - Orchestrator API: http://localhost:{args.orchestrator_port}")
    print(f"  - Frontend:         http://localhost:{args.frontend_port}")
    print(f"  - API Docs:         http://localhost:{args.orchestrator_port}/docs")
    print()
    print("Available models:")
    for model_name, port, _ in models_to_run:
        print(f"  - {model_name}: http://localhost:{port}")
    print()
    print("Press Ctrl+C to stop all services or run: python run_all.py --kill")
    print()
    print(f"Frontend: http://localhost:{args.frontend_port}")
    print()

    # Wait for processes
    try:
        for name, p in processes:
            p.wait()
    except KeyboardInterrupt:
        print("\nShutting down all services...")
        for name, p in processes:
            p.terminate()
        for name, p in processes:
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
        print("All services stopped.")
    finally:
        # Clean up PID file on exit
        if PID_FILE.exists():
            PID_FILE.unlink()


if __name__ == "__main__":
    main()
