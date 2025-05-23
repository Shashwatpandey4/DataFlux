from typing import Any, Dict, List

from src.sinks.base import BaseSink


class FastAPISink(BaseSink):
    """FastAPI sink implementation."""

    def __init__(self):
        """Initialize the FastAPI sink."""
        self.client = None
        self.event_count = 0

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the FastAPI sink with configuration."""
        # For now, just store the config
        self.config = config

    async def send(self, events: List[Dict[str, Any]]) -> None:
        """Send events to FastAPI endpoint."""
        # For now, just print events
        for event in events:
            print(f"[FastAPISink] Event: {event}")
            self.event_count += 1

    async def close(self) -> None:
        """Close the FastAPI sink."""
        if self.client:
            await self.client.close()

    def get_metrics(self) -> dict:
        """Return metrics for the FastAPI sink."""
        return {"type": "fastapi", "event_count": self.event_count}
