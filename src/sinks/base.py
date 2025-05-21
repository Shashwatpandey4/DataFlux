from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseSink(ABC):
    """Base class for all sink implementations. Defines the interface for sinks."""

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the sink with configuration."""
        pass

    @abstractmethod
    def flush(
        self, region: str, batch: List[Dict[str, Any]], counters: Dict[str, int]
    ) -> None:
        """Flush a batch of events to the sink."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Clean up resources when shutting down."""
        pass

    @abstractmethod
    def get_metrics(self) -> dict:
        """Return a dict of metrics for this sink."""
        pass
