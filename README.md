# DataFlux

DataFlux is a flexible, pluggable data pipeline for simulating and emitting streaming events to multiple sinks (Kafka, HTTP, Mock, etc.), with support for multi-region, multi-sink, and real-time metrics via Prometheus.

---

## Features
- **Pluggable Sink Architecture**: Easily add new sinks (Kafka, FastAPI/HTTP, Mock, etc.)
- **Multi-Region & Multi-Sink**: Route events to different sinks per region
- **Event Generators**: Simulate various event types (telemetry, feedback, logs, etc.)
- **Metrics Exporter**: Prometheus-compatible metrics on `/metrics`
- **Dockerized**: One-command setup for the app, Kafka, and Zookeeper
- **Configurable**: All behavior via `config.yaml`

---

## Architecture
```
+-------------------+      +-------------------+
|  Event Generators |----->|     Edge Buffer   |-----> Sinks (Kafka, HTTP, ...)
+-------------------+      +-------------------+
                                 |
                                 v
                        +----------------+
                        | Prometheus /metrics |
                        +----------------+
```

---

## Quick Start (Docker Compose)

1. **Build and start everything:**
   ```sh
   docker-compose up --build
   ```
   - This launches DataFlux, Kafka, and Zookeeper.
   - Prometheus metrics available at [localhost:9100/metrics](http://localhost:9100/metrics)
   - Kafka broker available at `localhost:9092`

2. **Stop everything:**
   ```sh
   docker-compose down
   ```

---

## Configuration
- Edit `config.yaml` to control regions, sinks, event types, and more.
- Example sink config:
  ```yaml
  sinks:
    kafka_sink:
      type: kafka
      kafka:
        bootstrap_servers: kafka:9092
        topic_prefix: dataflux
    fastapi_sink:
      type: fastapi
      fastapi:
        endpoint: http://host.docker.internal:8000/ingest
        timeout: 5
  region_sinks:
    us-east: [kafka_sink, fastapi_sink]
    default: [mock_sink]
  ```

---

## Development
- All source code is in `src/`
- Sinks in `src/sinks/`, event generators in `src/event_generators/`
- To run locally (without Docker):
  ```sh
  export PYTHONPATH=src
  pip install -r requirements.txt
  python src/main.py
  ```

---

## Adding a New Sink
1. Create a new class in `src/sinks/` inheriting from `BaseSink`
2. Register it in `SinkFactory` (`src/sinks/factory.py`)
3. Add config in `config.yaml`

---

## Contributing
Pull requests and issues are welcome! Please:
- Write clear docstrings and comments
- Add tests for new sinks or features
- Follow PEP8 and best practices

---

## License
MIT
