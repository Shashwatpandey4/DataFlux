import random
import uuid
from datetime import datetime, timedelta


def now():
    return datetime.utcnow().isoformat()


def generate_ulid():
    return uuid.uuid4().hex


def apply_jitter(timestamp, jitter_seconds):
    return (
        datetime.fromisoformat(timestamp)
        + timedelta(seconds=random.uniform(-jitter_seconds, jitter_seconds))
    ).isoformat()


def generate_user_device_pool(emitters, regions):
    """Generate a pool of users and their devices for data generation."""
    users = []
    # If emitters is a number, use it directly as the number of users
    num_users = emitters if isinstance(emitters, int) else emitters["num_users"]

    for _ in range(num_users):
        user = {
            "user_id": generate_ulid(),
            "region": random.choice(regions)[
                "name"
            ],  # Get the name from the region dictionary
            "devices": [generate_ulid() for _ in range(random.randint(1, 3))],
        }
        users.append(user)
    return users
