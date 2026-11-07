from dachshund import Page
from dachshund.widgets import BarChart, Logs, Text, TimeSeriesChart
from lib.dashboard.widgets.gauge import Gauge

overview_page = Page("overview", title="Overview")

with overview_page.row():
    overview_page.add(Text("summary"))

with overview_page.row():
    with overview_page.column(span=4):
        overview_page.add(
            Gauge(
                "average_latency_gauge",
                title="Latency Health",
                source="average_latency",
                min=0,
                max=500,
                warning_at=150,
                critical_at=300,
                unit="ms",
            )
        )
    overview_page.add(
        TimeSeriesChart("latency", title="Live Latency", y=["check", "command"])
    )

with overview_page.row():
    overview_page.add(Logs("logs", title="Logs"))

with overview_page.row():
    overview_page.add(
        BarChart("connection_event", title="Connection Events", x="type", persist=True)
    )
