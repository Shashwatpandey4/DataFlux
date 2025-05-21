import asyncio
import random

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


async def emit(user, config, buffers):
    while True:
        stream = weighted_random_choice(config["streams"])
        device_id = random.choice(user["devices"])
        event = event_generators_map[stream](user["user_id"], device_id)
        event["stream"] = stream
        add_to_buffer(
            event,
            user["region"],
            config["flush_batch_size"],
            config["flush_interval_sec"],
            counters,
        )
        interval = config["streams"][stream]["interval_sec"]
        if config.get("mode") == "safe":
            await asyncio.sleep(max(interval, 0.01))
        else:
            await asyncio.sleep(interval)


async def launch_emitters(user_pool, config, buffers):
    max_emitters = config.get("emitters_per_worker", len(user_pool))
    user_pool = user_pool[:max_emitters]

    tasks = []
    for user in user_pool:
        tasks.append(asyncio.create_task(emit(user, config, buffers)))
    await asyncio.gather(*tasks)
