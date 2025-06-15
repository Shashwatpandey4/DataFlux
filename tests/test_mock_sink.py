import pytest

from src.sinks.mock_sink import MockSink


@pytest.mark.asyncio
async def test_mock_sink_event_count_and_metrics():
    sink = MockSink()
    events = [{"event_id": i} for i in range(10)]
    await sink.send(events)
    metrics = sink.get_metrics()
    assert metrics["type"] == "mock"
    assert metrics["event_count"] == 10
    # Send more events
    await sink.send(events)
    metrics = sink.get_metrics()
    assert metrics["event_count"] == 20
