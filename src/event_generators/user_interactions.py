import random

from ..utils import generate_ulid, now


def generate_user_interaction(user_id, device_id):
    return {
        "event_id": generate_ulid(),
        "user_id": user_id,
        "device_id": device_id,
        "timestamp": now(),
        "event_type": random.choice(["click", "hover", "scroll", "like"]),
        "element": random.choice(
            ["video_thumbnail", "play_button", "volume_control", "search_bar"]
        ),
        "page": random.choice(["/home", "/watch", "/search", "/profile"]),
    }
