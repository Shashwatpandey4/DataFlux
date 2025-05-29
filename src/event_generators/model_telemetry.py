import random

from ..utils import generate_ulid, now


def generate_model_telemetry(user_id, device_id):
    return {
        "event_id": generate_ulid(),
        "user_id": user_id,
        "device_id": device_id,
        "timestamp": now(),
        "model_id": f"model_{random.randint(1, 100)}",
        "version": f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
        "accuracy": round(random.uniform(0.85, 0.99), 4),
        "latency_ms": random.randint(10, 1000),
        "errors": random.choices(
            ["", "timeout", "memory_error", "inference_error"],
            weights=[0.85, 0.05, 0.05, 0.05],
        )[0],
        "batch_size": random.choice([1, 4, 8, 16, 32]),
    }
