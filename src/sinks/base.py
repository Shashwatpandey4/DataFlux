from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseSink(ABC):
    """Base class for all sinks."""

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the sink with configuration."""
        pass

    @abstractmethod
    async def send(self, events: List[Dict[str, Any]]) -> None:
        """Send events to the sink."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the sink and cleanup resources."""
        pass

    @abstractmethod
    def get_metrics(self) -> dict:
        """Return a dict of metrics for this sink."""
        pass
