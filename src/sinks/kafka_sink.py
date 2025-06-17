import asyncio
import json
from typing import Any, Dict, List

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from src.sinks.base import BaseSink


class KafkaSink(BaseSink):
    """Kafka sink implementation with async support."""

    def __init__(self):
        """Initialize the Kafka sink."""
        self.producer = None
        self.event_count = 0
        self.error_count = 0
        self.topic = None
        self.bootstrap_servers = None
        self.retry_count = 0
        self.max_retries = 3

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the Kafka sink with configuration."""
        kafka_config = config.get("kafka", {})
        self.bootstrap_servers = kafka_config.get("bootstrap_servers", "localhost:9092")
        self.topic = kafka_config.get("topic", "dataflux-events")
        self.max_retries = kafka_config.get("max_retries", 3)

        # Create producer configuration
        self.producer_config = {
            "bootstrap_servers": self.bootstrap_servers,
            "value_serializer": lambda v: json.dumps(v).encode("utf-8"),
            "acks": kafka_config.get("acks", "all"),
            "retries": self.max_retries,
            "retry_backoff_ms": kafka_config.get("retry_backoff_ms", 100),
        }

    async def _ensure_producer(self):
        """Ensure Kafka producer is initialized."""
        if self.producer is None:
            try:
                self.producer = AIOKafkaProducer(**self.producer_config)
                await self.producer.start()
            except KafkaError as e:
                self.error_count += 1
                raise RuntimeError(f"Failed to initialize Kafka producer: {e}")

    async def send(self, events: List[Dict[str, Any]]) -> None:
        """Send events to Kafka with retry logic."""
        await self._ensure_producer()

        for event in events:
            retry_count = 0
            while retry_count < self.max_retries:
                try:
                    # Add metadata to the event
                    event_with_metadata = {
                        **event,
                        "_kafka_metadata": {
                            "topic": self.topic,
                            "timestamp": asyncio.get_event_loop().time(),
                        },
                    }

                    # Send to Kafka
                    await self.producer.send_and_wait(
                        topic=self.topic, value=event_with_metadata
                    )
                    self.event_count += 1
                    break
                except KafkaError as e:
                    retry_count += 1
                    self.error_count += 1
                    if retry_count == self.max_retries:
                        print(
                            f"Failed to send event to Kafka after {self.max_retries} retries: {e}"
                        )
                    else:
                        await asyncio.sleep(0.1 * retry_count)  # Exponential backoff

    async def close(self) -> None:
        """Close the Kafka sink."""
        if self.producer:
            try:
                await self.producer.stop()
            except KafkaError as e:
                print(f"Error closing Kafka producer: {e}")

    def get_metrics(self) -> dict:
        """Return metrics for the Kafka sink."""
        return {
            "type": "kafka",
            "event_count": self.event_count,
            "error_count": self.error_count,
            "topic": self.topic,
            "bootstrap_servers": self.bootstrap_servers,
        }
