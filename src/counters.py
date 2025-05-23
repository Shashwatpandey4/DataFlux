import asyncio
import signal
import time
from collections import defaultdict, deque

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

# Global flag for shutdown
should_exit = False

counters = defaultdict(int)
stream_bytes = defaultdict(int)

# Rolling history (5s)
rolling_events = deque(maxlen=5)
rolling_bytes = deque(maxlen=5)
stream_rolling_bytes = defaultdict(lambda: deque(maxlen=5))

# Global history (30s)
global_events = deque(maxlen=30)
global_bytes = deque(maxlen=30)
stream_global_bytes = defaultdict(lambda: deque(maxlen=30))

_start_time = time.time()
_last_total = 0
_last_bytes = 0
_last_stream_bytes = defaultdict(int)


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global should_exit
    should_exit = True


def count_event(event):
    stream = event.get("stream", "unknown")
    counters["total"] += 1
    counters[stream] += 1
    size = len(str(event).encode("utf-8"))
    stream_bytes[stream] += size
    counters["bytes"] += size


def create_metrics_panel(
    elapsed, rolling_eps, global_eps, rolling_bps, global_bps, total_events, total_data
):
    """Create a panel with the main metrics."""
    metrics_text = Text()
    metrics_text.append(f"Elapsed Time        : {elapsed:,.1f}s\n", style="cyan")
    metrics_text.append(f"Rolling EPS (5s avg): {rolling_eps:,.0f}\n", style="green")
    metrics_text.append(f"Global EPS (30s avg): {global_eps:,.0f}\n", style="yellow")
    metrics_text.append(
        f"Rolling Bandwidth   : {rolling_bps/1024/1024:,.2f} MB/s\n", style="green"
    )
    metrics_text.append(
        f"Global Bandwidth    : {global_bps/1024/1024:,.2f} MB/s\n", style="yellow"
    )
    metrics_text.append(f"Total Events        : {total_events:,}\n", style="magenta")
    metrics_text.append(
        f"Total Data          : {total_data/1024/1024:,.2f} MB", style="magenta"
    )

    return Panel(metrics_text, title="DataFlux Ingestion Stats", border_style="blue")


def create_stream_table(stream_data):
    """Create a table with stream metrics."""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Stream Name", style="cyan", width=24)
    table.add_column("Events", justify="right", style="green")
    table.add_column("% Total", justify="right", style="yellow")
    table.add_column("MB/s", justify="right", style="blue")

    for stream, count, percent, mbps in stream_data:
        table.add_row(stream, f"{count:,}", f"{percent:,.1f}%", f"{mbps:,.2f}")

    return table


async def start_counter_logger(interval=1):
    """Start the counter logger with clean shutdown support."""
    global _last_total, _last_bytes, _last_stream_bytes, should_exit

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        with Live(console=console, refresh_per_second=1, auto_refresh=False) as live:
            while not should_exit:
                await asyncio.sleep(interval)

                elapsed = time.time() - _start_time

                # Calculate this window's EPS and BPS
                eps = counters["total"] - _last_total
                bps = counters["bytes"] - _last_bytes

                # Store in rolling history (5s)
                rolling_events.append(eps)
                rolling_bytes.append(bps)

                # Store in global history (30s)
                global_events.append(eps)
                global_bytes.append(bps)

                # Calculate per-stream metrics
                for stream in stream_bytes:
                    stream_bps = stream_bytes[stream] - _last_stream_bytes[stream]
                    # Store in both rolling and global history
                    stream_rolling_bytes[stream].append(stream_bps)
                    stream_global_bytes[stream].append(stream_bps)
                    _last_stream_bytes[stream] = stream_bytes[stream]

                # Calculate averages
                rolling_eps = sum(rolling_events) / len(rolling_events)
                rolling_bps = sum(rolling_bytes) / len(rolling_bytes)
                global_eps = sum(global_events) / len(global_events)
                global_bps = sum(global_bytes) / len(global_bytes)

                # Create stream data
                total = counters["total"]
                stream_data = []
                for stream, count in sorted(counters.items(), key=lambda x: -x[1]):
                    if stream in ("total", "bytes"):
                        continue
                    percent = (count / total * 100) if total > 0 else 0
                    # Use rolling average for MB/s display
                    rolling_stream_bps = (
                        sum(stream_rolling_bytes[stream])
                        / len(stream_rolling_bytes[stream])
                        if stream_rolling_bytes[stream]
                        else 0
                    )
                    mbps = rolling_stream_bps / 1024 / 1024
                    stream_data.append((stream, count, percent, mbps))

                # Create layout
                layout = Layout()
                layout.split_column(Layout(name="metrics"), Layout(name="streams"))

                # Add content to layout
                layout["metrics"].update(
                    create_metrics_panel(
                        elapsed,
                        rolling_eps,
                        global_eps,
                        rolling_bps,
                        global_bps,
                        counters["total"],
                        counters["bytes"],
                    )
                )
                layout["streams"].update(create_stream_table(stream_data))

                # Update display
                live.update(layout)
                live.refresh()

                _last_total = counters["total"]
                _last_bytes = counters["bytes"]

    except asyncio.CancelledError:
        # Handle graceful shutdown
        console.print("\n[bold red]Shutting down DataFlux...[/bold red]")
        return
    except Exception as e:
        console.print(f"\n[bold red]Error in counter logger: {str(e)}[/bold red]")
        raise
