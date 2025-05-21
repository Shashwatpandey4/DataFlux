import json
from typing import Any, Dict, List

from kafka import KafkaProducer

from fault_injection import maybe_fail
from src.sinks.base import BaseSink
from utils import apply_jitter


class KafkaSink(BaseSink):
    """Kafka sink implementation that sends events to Kafka topics."""

    def __init__(self):
        """Initialize the Kafka sink."""
        self.producer = None
        self.topic_prefix = "dataflux"

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize Kafka producer with configuration."""
        kafka_config = config.get("kafka", {})
        bootstrap_servers = kafka_config.get("bootstrap_servers", "localhost:9092")
        self.topic_prefix = kafka_config.get("topic_prefix", "dataflux")

        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

    def flush(
        self, region: str, batch: List[Dict[str, Any]], counters: Dict[str, int]
    ) -> None:
        """Flush events to Kafka topics."""
        if not self.producer:
            raise RuntimeError("Kafka sink not initialized")

        for event in batch:
            if maybe_fail():
                counters["failed"] += 1
                continue

            # Apply jitter to timestamp
            event["timestamp"] = apply_jitter(event["timestamp"], 2)

            # Send to region-specific topic
            topic = f"{self.topic_prefix}.{region}"
            self.producer.send(topic, value=event)

        # Ensure all messages are delivered
        self.producer.flush()

    def close(self) -> None:
        """Close Kafka producer connection."""
        if self.producer:
            self.producer.close()

    def get_metrics(self) -> dict:
        """Return metrics for the Kafka sink."""
        return {
            "type": "kafka",
            "success_count": getattr(self, "success_count", 0),
            "fail_count": getattr(self, "fail_count", 0),
            "latencies": getattr(self, "latencies", []),
        }
