from counters import count_event
from sinks.factory import SinkFactory


class Dispatcher:
    def __init__(self, config):
        self.sink = SinkFactory.create_sink(config["sink"], config)

    def flush_batch(self, region, batch, counters):
        """Flush a batch of events using the configured sink."""
        self.sink.flush(region, batch, counters)
        for event in batch:
            count_event(event)

    def close(self):
        """Clean up resources."""
        self.sink.close()
