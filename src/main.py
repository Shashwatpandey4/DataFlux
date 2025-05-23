import argparse
import asyncio
from pathlib import Path

import yaml

from src.counters import start_counter_logger
from src.edge_buffer import initialize_buffers
from src.emitter import launch_emitters
from src.sinks.factory import get_sink
from src.utils import generate_user_device_pool


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

    # Start counter logger (only for worker 0)
    counter_task = None
    if worker_id == 0:
        counter_task = asyncio.create_task(start_counter_logger())

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
        # Cancel counter logger if it exists
        if counter_task:
            counter_task.cancel()
            try:
                await counter_task
            except asyncio.CancelledError:
                pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("worker_id", type=int, nargs="?", default=0)
    parser.add_argument(
        "--sink", type=str, default="mock", choices=["mock", "kafka", "fastapi"]
    )
    parser.add_argument(
        "--mode", type=str, default="normal", choices=["normal", "safe"]
    )
    args = parser.parse_args()

    asyncio.run(main(args.worker_id, args.sink, args.mode))
