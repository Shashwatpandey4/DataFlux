import asyncio
import sys

import yaml

from counters import start_counter_logger
from edge_buffer import initialize_buffers
from emitter import launch_emitters
from user_pool import generate_user_device_pool


def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)


async def main(worker_id=0):
    config = load_config()
    user_pool = generate_user_device_pool(config["emitters"], config["regions"])
    buffers = initialize_buffers(config["regions"])
    print(f"[Worker {worker_id}] Starting with {len(user_pool)} users...")
    await asyncio.gather(
        launch_emitters(user_pool, config, buffers), start_counter_logger(interval=1)
    )


if __name__ == "__main__":
    worker_id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    asyncio.run(main(worker_id))
