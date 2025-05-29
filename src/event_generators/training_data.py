import random

from ..utils import generate_ulid, now


def generate_training_data(user_id, device_id):
    return {
        "event_id": generate_ulid(),
        "doc_id": f"doc_{random.randint(100000,999999)}",
        "user_id": user_id,
        "device_id": device_id,
        "timestamp": now(),
        "source": random.choice(["web", "upload", "s3_dump", "api"]),
        "language": random.choice(["en", "es", "fr", "de", "zh"]),
        "length_tokens": random.randint(50, 2000),
        "embedding_hash": generate_ulid()[:12],
        "embedding": [round(random.random(), 4) for _ in range(128)],
        "license": random.choice(["open", "restricted", "unknown"]),
    }
