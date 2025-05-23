from typing import Any, Dict

from src.sinks.base import BaseSink
from src.sinks.fastapi_sink import FastAPISink
from src.sinks.kafka_sink import KafkaSink
from src.sinks.mock_sink import MockSink


class SinkFactory:
    """Factory for creating and managing sink instances based on configuration."""

    _sinks = {
        "kafka": KafkaSink,
        "mock": MockSink,
        "fastapi": FastAPISink,
    }

    @classmethod
    def create_sink(cls, sink_type: str, config: Dict[str, Any]) -> BaseSink:
        """Create and initialize a sink instance of the given type."""
        if sink_type not in cls._sinks:
            raise ValueError(f"Unknown sink type: {sink_type}")

        sink = cls._sinks[sink_type]()
        sink.initialize(config)
        return sink


def get_sink(sink_type: str):
    """Get the appropriate sink based on sink type."""
    if sink_type == "mock":
        return MockSink()
    elif sink_type == "kafka":
        return KafkaSink()
    elif sink_type == "fastapi":
        return FastAPISink()
    else:
        raise ValueError(f"Unknown sink type: {sink_type}")
