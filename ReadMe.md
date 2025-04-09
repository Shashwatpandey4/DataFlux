# DataFlux

**High-performance, multi-stream data ingestion simulator**  
Built for testing real-time pipelines, PB-scale throughput, and stream processing systems like Kafka, Flink, FastAPI, and Iceberg.

---

## Features

- Simulates geo-distributed telemetry streams
- Multi-agent emitters with async + multiprocessing
- Configurable EPS, payload size, flush batching
- Built-in fault injection and retry logic
- Real-time CLI dashboard with rolling stats
- Extensible stream generator architecture
- Easy to plug into Kafka, APIs, or file sinks

---

## Use Cases

- Load testing data ingestion pipelines
- Benchmarking Kafka or Iceberg clusters
- Simulating PB-scale event generation locally
- Testing fault tolerance and batching strategies
- Creating synthetic datasets for analytics

---

## Getting Started

### 1. Clone the Repo

```bash
git clone https://github.com/yourname/dataflux.git
cd dataflux
```

### 2. Install Requirements

```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Emission

Edit config.yaml:

```yaml
mode: safe
emitters: 100000
emitters_per_worker: 25000
flush_batch_size: 500
flush_interval_sec: 2
retry_probability: 0.05
time_jitter_sec: 2

streams:
  video_logs:
    weight: 0.2
    interval_sec: 0.05
  user_interactions:
    weight: 0.2
    interval_sec: 0.05
  ...
```

### 4. Run the Simulator
```bash
nice -n 10 python3 launch.py
```


### Customizing Streams
All streams live in `event_generators/`.

Add your own by creating a new file and defining a function:


```python
def generate_my_custom_event(user_id, device_id):
    return {...}
```
Then register it manually in `emitter.py`.

## License 
MIT

