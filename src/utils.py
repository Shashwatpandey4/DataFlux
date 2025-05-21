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
