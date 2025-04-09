from collections import defaultdict

from dispatcher import flush_batch

buffers = defaultdict(list)
flush_counts = defaultdict(int)


def initialize_buffers(regions):
    return {r["name"]: [] for r in regions}


def add_to_buffer(event, region, batch_size, flush_interval, counters):
    buffers[region].append(event)
    if len(buffers[region]) >= batch_size:
        flush_batch(region, buffers[region][:], counters)
        flush_counts[region] += 1
        buffers[region].clear()
