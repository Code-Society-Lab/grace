from dachshund import Number, Page, Table, Text, TimeSeriesChart, BarChart

from bot import app
from lib.dashboard.widgets.gauge import Gauge

overview_page = Page("overview", title="Overview")


def load_members(ctx: dict, cursor: str | None, page_size: int):
    bot = ctx["bot"]
    members = []

    if guild := bot.get_guild(app.config.get("client", "guild_id")):
        for member in guild.members:
            members.append(
                {
                    "id": member.id,
                    "name": member.name,
                    "nickname": member.nick,
                    "joined at": member.joined_at.strftime("%a %d %b %Y"),
                }
            )

    start = int(cursor) if cursor else 0
    rows = members[start : start + page_size]
    next_cursor = str(start + page_size) if start + page_size < len(members) else None

    return rows, next_cursor


overview_page.row(Text("summary"))
overview_page.row(
    Gauge(
        "average_latency_gauge",
        title="Latency Health",
        source="average_latency",
        min=0,
        max=500,
        warning_at=150,
        critical_at=300,
        unit="ms",
    ),
    TimeSeriesChart("latency", title="Live Latency", y=["check", "command"]),
    widths=(1, 2),
)
overview_page.row(
    Number("member_count"),
    Table(
        "members",
        columns=["id", "name", "nickname", "joined at"],
        loader=load_members,
    ),
    widths=(1, 2),
)
overview_page.row(
    BarChart("connection_event", title="Connection Events", x="type", persist=True)
)
