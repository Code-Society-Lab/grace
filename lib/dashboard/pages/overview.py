from dachshund import Number, Page, Table, Text, TimeSeriesChart

from lib.dashboard.widgets.gauge import Gauge

GUILD_IDS: list[int] = [1349086642446532639]


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


overview_page = Page("overview", title="Overview")


@overview_page.action("greet", label="Greet")
async def greet_user(ctx: dict, name: str, guild_id: str) -> None:
    bot = ctx["bot"]

    if guild := bot.get_guild(int(guild_id)):
        await guild.system_channel.send(f"Hello {name}!")


summary = overview_page.add(Text("summary"))
latency = overview_page.add(
    TimeSeriesChart("latency", title="Live Latency", y=["check", "command"])
)
gauge = overview_page.add(
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
member_count = overview_page.add(Number("member_count"))
members = overview_page.add(
    Table(
        "members",
        columns=["id", "name", "guild", "_guild_id"],
        actions=["greet"],
        loader=load_members,
    )
)

overview_page.row(summary)
overview_page.row(latency, overview_page.column(gauge, member_count))
overview_page.row(members)
