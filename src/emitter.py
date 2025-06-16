import asyncio
import random
from typing import Any, Dict, List

from src.counters import counters
from src.edge_buffer import add_to_buffer
from src.event_generators import (
    device_telemetry,
    model_telemetry,
    recommendation_feedback,
    training_data,
    user_interactions,
    video_logs,
)
from src.stream_weights import weighted_random_choice

event_generators_map = {
    "video_logs": video_logs.generate_video_log,
    "user_interactions": user_interactions.generate_user_interaction,
    "device_telemetry": device_telemetry.generate_device_telemetry,
    "recommendation_feedback": recommendation_feedback.generate_recommendation_feedback,
    "training_data": training_data.generate_training_data,
    "model_telemetry": model_telemetry.generate_model_telemetry,
}

# Rate limiting semaphore to control concurrent emissions
rate_limit_semaphore = None


async def emit(
    user: Dict[str, Any], config: Dict[str, Any], buffers: Dict[str, List]
) -> None:
    """Emit events for a single user with rate limiting."""
    global rate_limit_semaphore

    while True:
        # Acquire rate limit semaphore
        async with rate_limit_semaphore:
            stream = weighted_random_choice(config["streams"])
            device_id = random.choice(user["devices"])
            event = event_generators_map[stream](user["user_id"], device_id)
            event["stream"] = stream
            await add_to_buffer(
                event,
                user["region"],
                config["flush_batch_size"],
                config["flush_interval_sec"],
                counters,
            )

            # Calculate sleep time with jitter
            interval = config["streams"][stream]["interval_sec"]
            jitter = random.uniform(
                -config["time_jitter_sec"], config["time_jitter_sec"]
            )
            sleep_time = (
                max(interval + jitter, 0.01)
                if config.get("mode") == "safe"
                else interval + jitter
            )

            await asyncio.sleep(sleep_time)


async def launch_emitters(
    user_pool: List[Dict[str, Any]], config: Dict[str, Any], buffers: Dict[str, List]
) -> None:
    """Launch emitters with rate limiting and batch processing."""
    global rate_limit_semaphore
    max_concurrent_emissions = min(100000, len(user_pool))  # Limit concurrent emissions
    rate_limit_semaphore = asyncio.Semaphore(max_concurrent_emissions)

    # Launch all tasks at once
    tasks = [
        asyncio.create_task(emit(user, config, buffers))
        for user in user_pool[:max_concurrent_emissions]
    ]
    await asyncio.gather(*tasks)
