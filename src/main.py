import asyncio
import signal
import sys

import yaml

from src.counters import start_counter_logger
from src.edge_buffer import cleanup, initialize_buffers
from src.emitter import launch_emitters
from src.user_pool import generate_user_device_pool


def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)


async def main(worker_id=0):
    config = load_config()
    user_pool = generate_user_device_pool(config["emitters"], config["regions"])
    buffers = initialize_buffers(config["regions"], config)
    print(f"[Worker {worker_id}] Starting with {len(user_pool)} users...")

    # Register cleanup handler
    def signal_handler(sig, frame):
        print(f"\n[Worker {worker_id}] Shutting down...")
        cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await asyncio.gather(
            launch_emitters(user_pool, config, buffers),
            start_counter_logger(interval=1),
        )
    finally:
        cleanup()


if __name__ == "__main__":
    worker_id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    asyncio.run(main(worker_id))
