import dachshund

from bot import app
from lib.dashboard.sqlmodel_storage import SQLModelStorage

DACHSHUND_EVENT_STORE = app.config.get("dachshund", "event_store") or "dachshund.db"


def init_dachshund():
    dachshund.shutdown()

    dachshund.init(
        "Grace",
        description="Code Society's Discord Bot",
        host="0.0.0.0",
        path=DACHSHUND_EVENT_STORE,
        storage=SQLModelStorage(),
    )


def build_dashboard() -> None:
    dachshund.chart(
        "latency",
        type="timeseries",
        title="Live Latency",
        y=["check", "command"],
        size=2,
    )

    # for now it's a graph instead of a text/number
    dachshund.chart(
        "highest_latency",
        type="timeseries",
        title="Highest Latency Overtime",
    )

    dachshund.chart(
        "on_command",
        type="bar",
        title="Calls Per Command",
        x="name",
        size=3,
        persist=True,
    )
