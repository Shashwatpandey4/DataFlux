from typing import Any, Dict, List

from src.counters import count_event
from src.sinks.factory import SinkFactory


class EmitterRegistry:
    """Registry to initialize and manage sinks, and flush events to all sinks for a region."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the registry and all sinks from config."""
        self.sinks: Dict[str, Any] = {}
        self.region_sinks: Dict[str, List[str]] = {}
        self.default_sinks: List[str] = []
        self._init_sinks(config)

    def _init_sinks(self, config: Dict[str, Any]):
        """Load sinks and region mappings from config."""
        for sink_name, sink_conf in config.get("sinks", {}).items():
            sink_type = sink_conf["type"]
            self.sinks[sink_name] = SinkFactory.create_sink(sink_type, sink_conf)
        self.region_sinks = config.get("region_sinks", {})
        self.default_sinks = self.region_sinks.get("default", list(self.sinks.keys()))

    def get_sinks_for_region(self, region: str):
        """Return a list of sink instances for the given region."""
        sink_names = self.region_sinks.get(region, self.default_sinks)
        return [self.sinks[name] for name in sink_names if name in self.sinks]

    async def flush(
        self, region: str, batch: List[Dict[str, Any]], counters: Dict[str, int]
    ):
        """Flush a batch to all sinks for the given region."""
        # Count events before flushing
        for event in batch:
            count_event(event)

        # Send to all sinks for this region
        for sink in self.get_sinks_for_region(region):
            await sink.send(batch)

    async def close(self):
        """Close all sinks managed by the registry."""
        for sink in self.sinks.values():
            await sink.close()

    def get_all_metrics(self) -> dict:
        """Aggregate and return metrics from all sinks."""
        return {name: sink.get_metrics() for name, sink in self.sinks.items()}
