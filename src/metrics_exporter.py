"""
Prometheus metrics exporter for DataFlux sinks.
Exposes /metrics endpoint and updates metrics from the EmitterRegistry.
"""

import threading
import time

from prometheus_client import Gauge, start_http_server

from src.emitter_registry import EmitterRegistry

# Define Prometheus metrics
sink_success = Gauge("sink_success", "Number of successful events per sink", ["sink"])
sink_fail = Gauge("sink_fail", "Number of failed events per sink", ["sink"])
sink_flush_latency = Gauge("sink_flush_latency", "Flush latency per sink", ["sink"])


def update_metrics(registry: EmitterRegistry, interval: int = 5):
    """Periodically update Prometheus metrics from the registry."""
    while True:
        metrics = registry.get_all_metrics()
        for name, m in metrics.items():
            sink_success.labels(sink=name).set(m.get("success_count", 0))
            sink_fail.labels(sink=name).set(m.get("fail_count", 0))
            latencies = m.get("latencies", [])
            avg_latency = sum(latencies) / len(latencies) if latencies else 0
            sink_flush_latency.labels(sink=name).set(avg_latency)
        time.sleep(interval)


def start_metrics_exporter(registry: EmitterRegistry, port: int = 9100):
    """Start the Prometheus metrics HTTP server and background updater."""
    start_http_server(port)
    t = threading.Thread(target=update_metrics, args=(registry,), daemon=True)
    t.start()
