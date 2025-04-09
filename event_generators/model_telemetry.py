import random

from utils import generate_ulid, now


def generate_model_telemetry(user_id, device_id):
    return {
        "event_id": generate_ulid(),
        "model_name": random.choice(
            ["gpt-4o", "gpt-3.5", "llama-3", "claude", "mixtral"]
        ),
        "user_id": user_id,
        "device_id": device_id,
        "timestamp": now(),
        "input_tokens": random.randint(10, 500),
        "output_tokens": random.randint(5, 200),
        "latency_ms": random.randint(80, 3000),
        "status": random.choice(["success", "timeout", "validation_error"]),
        "error_type": random.choice(
            [None, "rate_limit", "invalid_input", "server_error"]
        ),
    }
