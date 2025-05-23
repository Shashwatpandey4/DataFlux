from typing import Any, Dict, List

from src.sinks.base import BaseSink


class MockSink(BaseSink):
    """Mock sink for testing that silently tracks events."""

    def __init__(self):
        """Initialize the mock sink."""
        self.event_count = 0

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the mock sink."""
        pass

    async def send(self, events: List[Dict[str, Any]]) -> None:
        """Silently track events."""
        self.event_count += len(events)

    async def close(self) -> None:
        """No cleanup needed for mock sink."""
        pass

    def get_metrics(self) -> dict:
        """Return metrics for the mock sink."""
        return {"type": "mock", "event_count": self.event_count}
