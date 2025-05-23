from typing import Any, Dict, List

from src.sinks.base import BaseSink


class KafkaSink(BaseSink):
    """Kafka sink implementation."""

    def __init__(self):
        """Initialize the Kafka sink."""
        self.producer = None
        self.event_count = 0

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the Kafka sink with configuration."""
        # For now, just store the config
        self.config = config

    async def send(self, events: List[Dict[str, Any]]) -> None:
        """Send events to Kafka."""
        # For now, just print events
        for event in events:
            print(f"[KafkaSink] Event: {event}")
            self.event_count += 1

    async def close(self) -> None:
        """Close the Kafka sink."""
        if self.producer:
            await self.producer.close()

    def get_metrics(self) -> dict:
        """Return metrics for the Kafka sink."""
        return {"type": "kafka", "event_count": self.event_count}
