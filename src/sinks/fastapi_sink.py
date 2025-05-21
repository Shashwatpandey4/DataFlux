import time
from typing import Any, Dict, List

import requests

from src.sinks.base import BaseSink


class FastAPISink(BaseSink):
    """FastAPI sink that POSTs events to a configurable HTTP endpoint."""

    def __init__(self):
        self.endpoint = None
        self.timeout = 5
        self.latencies = []
        self.success_count = 0
        self.fail_count = 0

    def initialize(self, config: Dict[str, Any]) -> None:
        fastapi_config = config.get("fastapi", {})
        self.endpoint = fastapi_config.get("endpoint", "http://localhost:8000/ingest")
        self.timeout = fastapi_config.get("timeout", 5)
        self.latencies.clear()
        self.success_count = 0
        self.fail_count = 0

    def flush(
        self, region: str, batch: List[Dict[str, Any]], counters: Dict[str, int]
    ) -> None:
        start = time.time()
        try:
            resp = requests.post(
                self.endpoint,
                json={"region": region, "events": batch},
                timeout=self.timeout,
            )
            resp.raise_for_status()
            self.success_count += len(batch)
            counters["fastapi_success"] = counters.get("fastapi_success", 0) + len(
                batch
            )
        except Exception:
            self.fail_count += len(batch)
            counters["fastapi_failed"] = counters.get("fastapi_failed", 0) + len(batch)
        finally:
            self.latencies.append(time.time() - start)

    def close(self) -> None:
        pass

    def get_metrics(self) -> dict:
        return {
            "type": "fastapi",
            "success_count": self.success_count,
            "fail_count": self.fail_count,
            "latencies": self.latencies,
        }
