from collections import defaultdict

from src.emitter_registry import EmitterRegistry

buffers = defaultdict(list)
flush_counts = defaultdict(int)
emitter_registry = None


def initialize_buffers(regions, config):
    global emitter_registry
    emitter_registry = EmitterRegistry(config)
    return {r["name"]: [] for r in regions}


def add_to_buffer(event, region, batch_size, flush_interval, counters):
    buffers[region].append(event)
    if len(buffers[region]) >= batch_size:
        emitter_registry.flush(region, buffers[region][:], counters)
        flush_counts[region] += 1
        buffers[region].clear()


def cleanup():
    if emitter_registry:
        emitter_registry.close()
