import random

from utils import generate_ulid, now


def generate_recommendation_feedback(user_id, device_id):
    items = [f"v{random.randint(1000, 9999)}" for _ in range(6)]
    clicked = random.choice(items)
    return {
        "event_id": generate_ulid(),
        "user_id": user_id,
        "device_id": device_id,
        "timestamp": now(),
        "recommendation_id": f"rec_{random.randint(100, 999)}",
        "items_shown": items,
        "item_clicked": clicked,
        "click_rank": items.index(clicked) + 1,
        "engagement_time_sec": random.randint(5, 300),
    }
