import random

from utils import generate_ulid, now


def generate_device_telemetry(user_id, device_id):
    return {
        "event_id": generate_ulid(),
        "user_id": user_id,
        "device_id": device_id,
        "timestamp": now(),
        "os": random.choice(["Android", "iOS", "Windows", "macOS", "Linux"]),
        "app_version": f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
        "battery": random.randint(10, 100),
        "temperature_c": round(random.uniform(30.0, 45.0), 2),
        "errors": random.choices(
            ["", "crash", "timeout", "memory_leak"], weights=[0.85, 0.05, 0.05, 0.05]
        )[0],
        "network_type": random.choice(["wifi", "4g", "5g", "ethernet"]),
    }
