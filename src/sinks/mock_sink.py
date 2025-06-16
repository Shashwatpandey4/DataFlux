import json
import os
from datetime import datetime
from typing import Any, Dict, List

from src.sinks.base import BaseSink


class MockSink(BaseSink):
    """Mock sink for testing that stores first 100 events in a file and counts the rest."""

    def __init__(self):
        """Initialize the mock sink."""
        self.event_count = 0
        self.stored_count = 0
        self.max_stored_events = 100
        self.output_dir = "mock_data"
        self.current_file = None
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        """Ensure the output directory exists."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _get_current_file(self):
        """Get the current output file based on timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.output_dir, f"events_{timestamp}.jsonl")

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the mock sink."""
        self.current_file = self._get_current_file()

    async def send(self, events: List[Dict[str, Any]]) -> None:
        """Store first 100 events in a file, count the rest."""
        self.event_count += len(events)

        # Calculate how many more events we can store
        remaining_slots = max(0, self.max_stored_events - self.stored_count)

        if remaining_slots > 0:
            # Write only the events that fit within our remaining slots
            events_to_store = events[:remaining_slots]
            with open(self.current_file, "a") as f:
                for event in events_to_store:
                    f.write(json.dumps(event) + "\n")
            self.stored_count += len(events_to_store)

    async def close(self) -> None:
        """No cleanup needed for mock sink."""
        pass

    def get_metrics(self) -> dict:
        """Return metrics for the mock sink."""
        return {
            "type": "mock",
            "total_event_count": self.event_count,
            "stored_event_count": self.stored_count,
            "output_file": self.current_file,
        }
