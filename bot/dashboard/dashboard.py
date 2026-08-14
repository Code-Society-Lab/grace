import dachshund


def build_dashboard() -> None:
    """Register every chart shown on the dashboard.

    Called once, at bot construction, so registration never re-runs on
    cog/extension reload (dachshund raises if a widget name is added twice).
    """
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
    )
