import random

from utils import generate_ulid, now


def generate_video_log(user_id, device_id):
    return {
        "event_id": generate_ulid(),
        "user_id": user_id,
        "device_id": device_id,
        "timestamp": now(),
        "video_id": f"vid_{random.randint(1000,9999)}",
        "action": random.choice(["play", "pause", "seek", "buffer"]),
        "position": round(random.uniform(0, 3600), 2),
        "quality": random.choice(["480p", "720p", "1080p"]),
        "bandwidth_mbps": round(random.uniform(0.5, 5.0), 2),
    }
