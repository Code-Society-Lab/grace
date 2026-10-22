import dachshund

from bot import app
from lib.dashboard.sqlmodel_storage import SQLModelStorage
from lib.dashboard.widgets.gauge import (
    Gauge,
)  # registers the "gauge" widget type on import

DACHSHUND_EVENT_STORE = app.config.get("dachshund", "event_store", "dachshund.db")
GUILD_IDS: list[int] = [1349086642446532639]


def init_dachshund():
    """Stop any previous run and (re)open the dashboard's storage."""
    dachshund.shutdown()
    dachshund.default(path=DACHSHUND_EVENT_STORE, storage=SQLModelStorage())


def start_dashboard(context: dict):
    dachshund.init(
        "Grace",
        description="Code Society's Discord Bot",
        host="0.0.0.0",
        context=context
    )

@dachshund.action("greet", label="Greet")
async def greet_user(ctx: dict, name: str, guild_id: str) -> None:
    bot = ctx["bot"]

    if guild := bot.get_guild(int(guild_id)):
        await guild.system_channel.send(f"Hello {name}!")


def load_members(ctx: dict, cursor: str | None, page_size: int):
    bot = ctx["bot"]
    members = []

    for guild_id in GUILD_IDS:
        if guild := bot.get_guild(guild_id):
            for member in guild.members:
                members.append(
                    {
                        "id": member.id,
                        "name": member.name,
                        "guild": guild.name,
                        "_guild_id": str(guild.id),
                    }
                )

    start = int(cursor) if cursor else 0
    rows = members[start : start + page_size]
    next_cursor = str(start + page_size) if start + page_size < len(members) else None

    return rows, next_cursor


def build_dashboard() -> None:
    dachshund.widget(
        "summary",
        type="text",
        size=3
    )

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

    # message
    dachshund.widget(
        "daily_message_rate",
        type="number",
        title="Today's Messages Rate",
        size=1,
    )

    dachshund.chart(
        "weekly_message_counts",
        type="bar",
        title="Messages / day",
        x="date",
        size=2,
        persist=True,
    )

    # members
    dachshund.widget(
        "member_count",
        type="number",
        size=1,
    )

    dachshund.widget(
        "members",
        type="table",
        columns=["id", "name", "guild", "_guild_id"],
        actions=["greet"],
        loader=load_members,
        size=2,
    )

    # commands
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
