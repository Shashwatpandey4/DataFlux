import time
from typing import Any, Dict, List

from src.sinks.base import BaseSink


class MockSink(BaseSink):
    """Mock sink for testing, stores events in memory and simulates success."""

    def __init__(self):
        """Initialize the mock sink and its metrics."""
        self.events = []
        self.flush_count = 0
        self.latencies = []

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize or reset the mock sink state."""
        self.config = config
        self.events.clear()
        self.flush_count = 0
        self.latencies.clear()

    def flush(
        self, region: str, batch: List[Dict[str, Any]], counters: Dict[str, int]
    ) -> None:
        """Simulate flushing a batch by storing events and updating metrics."""
        start = time.time()
        self.events.extend(batch)
        self.flush_count += 1
        self.latencies.append(time.time() - start)
        # Simulate success
        for _ in batch:
            counters["mock_success"] = counters.get("mock_success", 0) + 1

    def close(self) -> None:
        """No-op for mock sink."""
        pass

    def get_metrics(self) -> dict:
        """Return metrics for the mock sink."""
        return {
            "type": "mock",
            "flush_count": self.flush_count,
            "event_count": len(self.events),
            "latencies": self.latencies,
        }
