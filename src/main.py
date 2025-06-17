import argparse
import asyncio
import sys
from pathlib import Path

import uvicorn
import yaml
from rich.console import Console
from rich.table import Table

from .counters import counters
from .edge_buffer import cleanup, initialize_buffers
from .emitter import launch_emitters
from .sinks.factory import get_sink
from .user_pool import generate_user_device_pool
from .utils import generate_user_device_pool
from .web.app import app as web_app


def load_config(sink_type="mock"):
    """Load configuration from YAML file."""
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Override sink configuration based on sink_type
    if sink_type == "mock":
        config["sinks"] = {"mock": {"type": "mock"}}
        config["region_sinks"] = {"default": ["mock"]}
    elif sink_type == "kafka":
        config["sinks"] = {"kafka": config["sinks"]["kafka"]}
        config["region_sinks"] = {"default": ["kafka"]}
    elif sink_type == "fastapi":
        config["sinks"] = {"fastapi": config["sinks"]["fastapi"]}
        config["region_sinks"] = {"default": ["fastapi"]}
    return config


def create_metrics_table(console):
    """Create a table for displaying metrics."""
    table = Table(title="DataFlux Metrics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    console.print(table)
    return table


async def update_metrics(console, table, config):
    """Update and display metrics."""
    while True:
        table.clear_rows()
        print("Current counters:", counters)  # Debug print to show current counters
        # Add event counts
        for stream, count in counters.items():
            table.add_row(f"{stream} Events", str(count))

        # Add total events
        total_events = sum(counters.values())
        table.add_row("Total Events", str(total_events))

        # Add event rate (events per second)
        if hasattr(update_metrics, "last_total"):
            rate = total_events - update_metrics.last_total
            table.add_row("Events/sec", str(rate))
        update_metrics.last_total = total_events

        console.clear()
        console.print(table)
        await asyncio.sleep(1)


async def main(worker_id, sink_type="mock", mode="normal"):
    """Main entry point for DataFlux worker."""
    # Load configuration
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Override config with command line arguments
    config["sink_type"] = sink_type
    config["mode"] = mode

    # Initialize sink
    sink = get_sink(sink_type)
    sink.initialize(config)

    # Generate user pool
    user_pool = generate_user_device_pool(config["emitters"], config["regions"])

    # Initialize buffers
    buffers = initialize_buffers(config["regions"], config)

    try:
        # Launch emitters
        await launch_emitters(user_pool, config, buffers)
    finally:
        # Ensure sink is closed
        await sink.close()


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="DataFlux - High-throughput data simulation framework"
    )
    parser.add_argument("command", choices=["run", "help"], help="Command to execute")
    args = parser.parse_args()

    if args.command == "help":
        parser.print_help()
        return

    if args.command == "run":
        try:
            asyncio.run(run_dataflux())
        except (KeyboardInterrupt, asyncio.CancelledError):
            print("\nShutting down gracefully...")
            sys.exit(0)


def start_command():
    """Command to start the DataFlux application."""
    try:
        asyncio.run(run_dataflux())
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\nShutting down gracefully...")
        sys.exit(0)


async def run_dataflux():
    """Run the DataFlux application."""
    console = Console()
    config = load_config()

    # Initialize components
    user_pool = generate_user_device_pool(config["emitters"], config["regions"])
    buffers = initialize_buffers(config["regions"], config)

    # Start the web dashboard
    uvicorn_config = uvicorn.Config(
        web_app, host="0.0.0.0", port=8000, log_level="info"
    )
    server = uvicorn.Server(uvicorn_config)
    dashboard_task = asyncio.create_task(server.serve())

    try:
        await launch_emitters(user_pool, config, buffers)
    except (KeyboardInterrupt, asyncio.CancelledError):
        console.print("\n[yellow]Shutting down gracefully...[/yellow]")
    finally:
        dashboard_task.cancel()
        try:
            await dashboard_task
        except asyncio.CancelledError:
            pass
        await cleanup()


if __name__ == "__main__":
    main()
