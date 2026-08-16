import dachshund

from bot import app
from lib.dashboard.sqlmodel_storage import SQLModelStorage
from lib.dashboard.widgets.gauge import (
    Gauge,
)  # registers the "gauge" widget type on import

DACHSHUND_EVENT_STORE = app.config.get("dachshund", "event_store") or "dachshund.db"


def init_dachshund():
    """Stop any previous run and (re)open the dashboard's storage."""
    dachshund.shutdown()
    dachshund.default(path=DACHSHUND_EVENT_STORE, storage=SQLModelStorage())


def start_dashboard():
    dachshund.init(
        "Grace",
        description="Code Society's Discord Bot",
        host="0.0.0.0",
    )


def build_dashboard() -> None:
    # latency
    dachshund.chart(
        "latency",
        type="timeseries",
        title="Live Latency",
        y=["check", "command"],
        size=2,
    )

    dachshund.widget(
        "average_latency_gauge",
        type="gauge",
        title="Latency Health",
        source="average_latency",
        min=0,
        max=500,
        warning_at=150,
        critical_at=300,
        unit="ms",
        size=1,
    )

    dachshund.widget(
        "average_latency",
        type="number",
        title="Average Latency",
        unit="ms",
        size=1,
    )

    dachshund.widget(
        "highest_latency",
        type="number",
        title="Highest Latency",
        unit="ms",
        size=1,
    )

    dachshund.widget(
        "lowest_latency",
        type="number",
        title="Lowest Latency",
        unit="ms",
        size=1,
    )

    # member
    dachshund.widget(
        "daily_message_rate",
        type="number",
        title="Messages / day",
        size=1,
    )

    # message
    dachshund.widget(
        "minutely_message_rate",
        type="number",
        title="Messages / min",
        size=1,
    )

    # commands
    dachshund.widget(
        "minutely_command_rate",
        type="number",
        title="Commands / min",
        size=1,
    )

    dachshund.chart(
        "on_command",
        type="bar",
        title="Calls Per Command",
        x="name",
        size=3,
        persist=True,
    )

    dachshund.chart(
        "command_error",
        type="bar",
        title="Errors Per Command",
        x="name",
        size=3,
        persist=True,
    )

    # connection events
    dachshund.chart(
        "connection_event",
        type="bar",
        title="Connection Events",
        x="type",
        size=3,
        persist=True,
    )
