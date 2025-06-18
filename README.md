# DataFlux

DataFlux is a high-throughput data simulation framework designed to generate and ingest large-scale streaming data for analytics and testing. 

**Scale:**
- DataFlux can simulate data at the terabyte (TB) scale, generating approximately 5.7 TB of data per day at peak throughput on a single node.

---

## Features
- **Pluggable Sink Architecture**: Easily add new sinks (FastAPI/HTTP, Mock, Kafka, etc.)
- **Multi-Region & Multi-Sink**: Route events to different sinks per region
- **Event Generators**: Simulate various event types (telemetry, feedback, logs, etc.)
- **Real-time Web Dashboard**: Live display of ingestion statistics and stream metrics via web UI
- **Kafka Integration**: Built-in Kafka producer for seamless integration with data pipelines
- **Dockerized**: One-command setup for the application
- **Kubernetes Ready**: Helm chart for production deployment
- **Configurable**: All behavior via `config.yaml`
- **Development Friendly**: Auto-reload support for rapid development

---

## Quick Start

### Using Docker

1. **Build and start the infrastructure:**
   ```sh
   docker compose up --build -d
   ```
   - This launches DataFlux with Kafka, Zookeeper, and all necessary configurations
   - The containers will be ready but the app won't start automatically (for development flexibility)

2. **Start the DataFlux application:**
   ```sh
   docker exec -it dataflux-dataflux-1 python -m src.main run
   ```
   - This starts the DataFlux app inside the running container
   - You'll see real-time statistics in the console
   - Web dashboard will be available at http://localhost:8000

3. **Stop the application:**
   ```sh
   docker compose down
   ```

### Web Dashboard
- **URL**: http://localhost:8000
- **Features**: Real-time metrics, event rates, bandwidth monitoring, stream distribution
- **Auto-reload**: Code changes are automatically reflected (development mode)

### Using Kubernetes (Production)

1. **Add the Helm repository:**
   ```sh
   helm repo add dataflux https://your-helm-repo-url
   helm repo update
   ```

2. **Install the chart:**
   ```sh
   helm install dataflux dataflux/dataflux
   ```

3. **Customize the deployment:**
   ```sh
   helm install dataflux dataflux/dataflux \
     --set replicaCount=3 \
     --set config.events_per_second=5000
   ```

4. **Upgrade the deployment:**
   ```sh
   helm upgrade dataflux dataflux/dataflux
   ```

5. **Uninstall the deployment:**
   ```sh
   helm uninstall dataflux
   ```

### Development Mode (Editable)

1. **Set up a virtual environment:**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies in editable mode:**
   ```sh
   pip install -e .
   ```

3. **Run the application:**
   ```sh
   python -m src.main run
   ```

---

## Configuration
- Edit `config.yaml` to control regions, sinks, event types, and more.
- Example sink config:
  ```yaml
  sinks:
    kafka:
      type: kafka
      kafka:
        bootstrap_servers: "kafka:29092"
        topic: "dataflux-events"
        acks: "all"
        max_retries: 3
        retry_backoff_ms: 100
    mock:
      type: mock
  region_sinks:
    default: [kafka, mock]
  ```

### Event Types
The system supports the following event types with configurable weights:
- `video_logs`: Video streaming and playback events
- `user_interactions`: User engagement and interaction events
- `device_telemetry`: Device status and health metrics
- `recommendation_feedback`: Recommendation system feedback
- `training_data`: Machine learning training data
- `model_telemetry`: Model performance and inference metrics

### Mock Data Storage
- The mock sink stores the first 100 events in a JSONL file
- File location: `mock_data/events_TIMESTAMP.jsonl`
- Events are stored in JSONL format (one JSON object per line)
- All events are counted, but only the first 100 are stored for inspection
- The file is persisted between container runs using Docker volumes

---

## Integration with Data Pipelines

### Kafka Integration
DataFlux can be easily integrated with external data pipeline projects via Kafka:

1. **DataFlux as Producer**: Generates events and sends them to Kafka topics
2. **External Pipeline as Consumer**: Reads events from the same Kafka topics

### Connecting External Projects
To connect your data pipeline project to DataFlux:

1. **Update your pipeline's `docker-compose.yml`:**
   ```yaml
   networks:
     dataflux_dataflux_network:
       external: true
   
   services:
     your-consumer:
       # ... your config ...
       networks:
         - dataflux_dataflux_network
       environment:
         - KAFKA_BOOTSTRAP_SERVERS=kafka:29092
   ```

2. **Start DataFlux first:**
   ```sh
   cd /path/to/dataflux
   docker compose up -d
   docker exec -it dataflux-dataflux-1 python -m src.main run
   ```

3. **Start your pipeline project:**
   ```sh
   cd /path/to/your/pipeline
   docker compose up -d
   ```

### Kafka Topic Details
- **Topic**: `dataflux-events`
- **Broker**: `kafka:29092` (from within the Docker network)
- **Data Format**: JSON events with fields like `event_id`, `user_id`, `device_id`, `timestamp`, `stream`, etc.

---

## Development
- All source code is in `src/`
- Sinks in `src/sinks/`, event generators in `src/event_generators/`
- Web dashboard templates in `src/web/templates/`
- The application uses relative imports for better module handling
- Auto-reload is enabled for development (uvicorn with `reload=True`)
- For local development, use editable mode installation as shown above

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

## Results
In our tests, DataFlux achieved a sustained data generation rate of ~68 MB/s, which translates to approximately 5.7 terabytes of data per day, demonstrating its capability to simulate TB-scale data ingestion scenarios.
