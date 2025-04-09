from counters import count_event
from fault_injection import maybe_fail
from utils import apply_jitter


def flush_batch(region, batch, counters):
    for event in batch:
        if maybe_fail():
            counters["failed"] += 1
            continue

        event["timestamp"] = apply_jitter(event["timestamp"], 2)

        count_event(event)
