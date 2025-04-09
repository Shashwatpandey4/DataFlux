import asyncio
import os
import time
from collections import defaultdict, deque

counters = defaultdict(int)
stream_bytes = defaultdict(int)

# Rolling history (5s)
rolling_events = deque(maxlen=5)
rolling_bytes = deque(maxlen=5)

_start_time = time.time()
_last_total = 0
_last_bytes = 0


def count_event(event):
    stream = event.get("stream", "unknown")
    counters["total"] += 1
    counters[stream] += 1
    size = len(str(event).encode("utf-8"))
    stream_bytes[stream] += size
    counters["bytes"] += size


async def start_counter_logger(interval=1):
    global _last_total, _last_bytes

    while True:
        await asyncio.sleep(interval)

        elapsed = time.time() - _start_time

        # Calculate this window's EPS and BPS
        eps = counters["total"] - _last_total
        bps = counters["bytes"] - _last_bytes

        # Store in rolling history
        rolling_events.append(eps)
        rolling_bytes.append(bps)

        # Rolling averages
        rolling_eps = sum(rolling_events) / len(rolling_events)
        rolling_bps = sum(rolling_bytes) / len(rolling_bytes)

        global_eps = counters["total"] / elapsed
        global_bps = counters["bytes"] / elapsed

        os.system("clear")
        print("=" * 46)
        print("             DataFlux Ingestion Stats")
        print("=" * 46)
        print(f"\nElapsed Time        : {elapsed:,.1f}s")
        print(f"Rolling EPS (5s avg): {rolling_eps:,.0f}")
        print(f"Global EPS          : {global_eps:,.0f}")
        print(f"Rolling Bandwidth   : {rolling_bps/1024/1024:,.2f} MB/s")
        print(f"Global Bandwidth    : {global_bps/1024/1024:,.2f} MB/s")
        print(f"Total Events        : {counters['total']:,}")
        print(f"Total Data          : {counters['bytes']/1024/1024:,.2f} MB\n")

        print("-" * 49)
        print(f"{'| Stream Name':<26}| {'Events':>10} | {'% Total':>7} | {'MB/s':>6} |")
        print(f"{'-' * 49}")

        total = counters["total"]
        stream_data = []

        for stream, count in sorted(counters.items(), key=lambda x: -x[1]):
            if stream in ("total", "bytes"):
                continue
            percent = (count / total * 100) if total > 0 else 0
            mbps = (stream_bytes[stream] / elapsed) / 1024 / 1024
            stream_data.append((stream, count, percent, mbps))

        for stream, count, percent, mbps in stream_data:
            print(f"| {stream:<24} | {count:>10,} | {percent:>6.1f}% | {mbps:>6.2f} |")

        print("-" * 49)
        print("Note: Rolling metrics are averaged over the last 5 seconds.")

        _last_total = counters["total"]
        _last_bytes = counters["bytes"]
