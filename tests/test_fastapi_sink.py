from unittest.mock import MagicMock

import pytest

from src.sinks.fastapi_sink import FastAPISink


@pytest.mark.asyncio
async def test_fastapi_sink_event_count_and_metrics():
    sink = FastAPISink()
    sink.client = MagicMock()  # Mock the HTTP client
    events = [{"event_id": i} for i in range(5)]
    await sink.send(events)
    metrics = sink.get_metrics()
    assert metrics["type"] == "fastapi"
    assert metrics["event_count"] == 5
    # Send more events
    await sink.send(events)
    metrics = sink.get_metrics()
    assert metrics["event_count"] == 10
