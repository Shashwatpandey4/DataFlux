import asyncio
import time
from datetime import datetime
from typing import List

from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..counters import (
    counters,
    global_bytes,
    global_events,
    rolling_bytes,
    rolling_events,
    stream_bytes,
)

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

# Templates
templates = Jinja2Templates(directory="src/web/templates")

# Store active WebSocket connections
active_connections: List[WebSocket] = []


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.websocket("/ws/metrics")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics updates."""
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # Calculate metrics
            elapsed = time.time() - _start_time
            total_events = counters["total"]
            total_bytes = counters["bytes"]

            # Calculate rates
            rolling_eps = (
                sum(rolling_events) / len(rolling_events) if rolling_events else 0
            )
            global_eps = sum(global_events) / len(global_events) if global_events else 0
            rolling_bps = (
                sum(rolling_bytes) / len(rolling_bytes) if rolling_bytes else 0
            )
            global_bps = sum(global_bytes) / len(global_bytes) if global_bytes else 0

            # Prepare stream data
            stream_data = []
            for stream, count in sorted(counters.items(), key=lambda x: -x[1]):
                if stream in ("total", "bytes"):
                    continue
                percent = (count / total_events * 100) if total_events > 0 else 0
                stream_data.append(
                    {
                        "name": stream,
                        "count": count,
                        "percent": round(percent, 1),
                        "bytes": stream_bytes.get(stream, 0),
                    }
                )

            # Prepare metrics data
            metrics_data = {
                "timestamp": datetime.now().isoformat(),
                "elapsed": round(elapsed, 1),
                "total_events": total_events,
                "total_bytes": total_bytes,
                "rolling_eps": round(rolling_eps, 0),
                "global_eps": round(global_eps, 0),
                "rolling_bps": round(rolling_bps / 1024 / 1024, 2),  # Convert to MB/s
                "global_bps": round(global_bps / 1024 / 1024, 2),  # Convert to MB/s
                "streams": stream_data,
            }

            # Send metrics to client
            await websocket.send_json(metrics_data)
            await asyncio.sleep(1)  # Update every second

    except Exception:
        pass
    finally:
        active_connections.remove(websocket)


# Global variable for start time
_start_time = time.time()
