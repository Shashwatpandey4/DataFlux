import random
import uuid


def generate_user_device_pool(count, regions):
    pool = []
    for i in range(count):
        user_id = f"u{str(i).zfill(6)}"
        devices = [f"d{uuid.uuid4().hex[:6]}" for _ in range(random.randint(1, 3))]
        region = random.choice(regions)["name"]
        pool.append({"user_id": user_id, "devices": devices, "region": region})
    return pool
