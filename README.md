# DataFlux

DataFlux is a high-throughput data simulation framework designed to generate and ingest large-scale streaming data for analytics and testing. 

**Scale:**
- DataFlux can simulate data at the terabyte (TB) scale, generating approximately 5.7 TB of data per day at peak throughput on a single node.

---

## Features
- **Pluggable Sink Architecture**: Easily add new sinks (FastAPI/HTTP, Mock, etc.)
- **Multi-Region & Multi-Sink**: Route events to different sinks per region
- **Event Generators**: Simulate various event types (telemetry, feedback, logs, etc.)
- **Real-time Metrics**: Live display of ingestion statistics and stream metrics
- **Dockerized**: One-command setup for the application
- **Kubernetes Ready**: Helm chart for production deployment
- **Configurable**: All behavior via `config.yaml`

---

## Quick Start

### Using Docker

1. **Build and start the application:**
   ```sh
   docker-compose up --build
   ```
   - This launches DataFlux with all necessary configurations
   - The application will start generating and processing events immediately
   - You'll see real-time statistics in the console

2. **Stop the application:**
   ```sh
   docker-compose down
   ```

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
   python -m src.main
   ```

---

## Configuration
- Edit `config.yaml` to control regions, sinks, event types, and more.
- Example sink config:
  ```yaml
  sinks:
    fastapi_sink:
      type: fastapi
      fastapi:
        endpoint: http://host.docker.internal:8000/ingest
        timeout: 5
    mock_sink:
      type: mock
  region_sinks:
    us-east: [fastapi_sink]
    default: [mock_sink]
  ```

### Kubernetes Configuration
The Helm chart supports various configuration options:
- `replicaCount`: Number of DataFlux instances
- `resources`: CPU and memory limits/requests
- `config`: Application configuration
- `persistence`: Log storage configuration

See `helm/dataflux/values.yaml` for all available options.

---

## Development
- All source code is in `src/`
- Sinks in `src/sinks/`, event generators in `src/event_generators/`
- The application uses relative imports for better module handling
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
