import asyncio
import json

import pytest
from kafka import KafkaConsumer

from src.sinks.factory import SinkFactory
from src.sinks.kafka_sink import KafkaSink


async def test_kafka_sink():
    config = {
        "sink": "kafka",
        "kafka": {
            "bootstrap_servers": "localhost:9092",
            "topic_prefix": "dataflux_test",
        },
    }

    sink = SinkFactory.create_sink("kafka", config)

    test_region = "us-west"
    test_batch = [
        {
            "event_id": "test1",
            "user_id": "u1",
            "device_id": "d1",
            "timestamp": "2024-03-20T10:00:00",
            "stream": "test_stream",
        },
        {
            "event_id": "test2",
            "user_id": "u2",
            "device_id": "d2",
            "timestamp": "2024-03-20T10:00:01",
            "stream": "test_stream",
        },
    ]
    counters = {"failed": 0}

    consumer = KafkaConsumer(
        f"{config['kafka']['topic_prefix']}.{test_region}",
        bootstrap_servers=config["kafka"]["bootstrap_servers"],
        auto_offset_reset="earliest",
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    )

    try:
        print("Flushing test batch...")
        sink.flush(test_region, test_batch, counters)

        await asyncio.sleep(2)

        print("\nVerifying messages...")
        received_messages = []
        for message in consumer:
            received_messages.append(message.value)
            if len(received_messages) == len(test_batch):
                break

        print(f"\nSent {len(test_batch)} messages")
        print(f"Received {len(received_messages)} messages")
        print(f"Failed messages: {counters['failed']}")

        for sent, received in zip(test_batch, received_messages):
            print(f"\nSent: {sent}")
            print(f"Received: {received}")
            assert sent["event_id"] == received["event_id"], "Message content mismatch"

        print("\nTest completed successfully!")

    finally:
        sink.close()
        consumer.close()


@pytest.mark.asyncio
async def test_kafka_sink_event_count_and_metrics():
    sink = KafkaSink()
    sink.producer = None  # No real producer needed for this unit test
    events = [{"event_id": i} for i in range(7)]
    await sink.send(events)
    metrics = sink.get_metrics()
    assert metrics["type"] == "kafka"
    assert metrics["event_count"] == 7
    # Send more events
    await sink.send(events)
    metrics = sink.get_metrics()
    assert metrics["event_count"] == 14


if __name__ == "__main__":
    asyncio.run(test_kafka_sink())
