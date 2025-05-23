import argparse
import asyncio
import multiprocessing
import sys
from pathlib import Path


def start_worker(worker_id, sink_type, mode):
    """Start a DataFlux worker process."""
    # Add src directory to Python path
    src_dir = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_dir))

    # Import main here to avoid circular imports
    from main import main as worker_main

    # Run the worker with asyncio
    asyncio.run(worker_main(worker_id, sink_type, mode))


def run(num_workers=4, sink_type="mock", mode="normal"):
    """Launch DataFlux workers."""
    print(
        f"Launching {num_workers} DataFlux workers with {sink_type} sink in {mode} mode...\n"
    )

    # Create worker processes
    processes = []
    for i in range(num_workers):
        p = multiprocessing.Process(
            target=start_worker, args=(i, sink_type, mode), name=f"DataFlux-Worker-{i}"
        )
        processes.append(p)
        p.start()

    try:
        # Wait for all processes
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\nShutting down workers...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.join()


def main():
    """Parse command line arguments and run DataFlux."""
    parser = argparse.ArgumentParser(description="DataFlux CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run DataFlux workers")
    run_parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=4,
        help="Number of workers to launch (default: 4)",
    )
    run_parser.add_argument(
        "-s",
        "--sink",
        type=str,
        default="mock",
        choices=["mock", "kafka", "fastapi"],
        help="Sink type to use (default: mock)",
    )
    run_parser.add_argument(
        "-m",
        "--mode",
        type=str,
        default="normal",
        choices=["normal", "safe"],
        help="Operation mode (default: normal)",
    )

    args = parser.parse_args()

    if args.command == "run":
        run(args.workers, args.sink, args.mode)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
