from typing import Any, Callable

from dachshund import Page
from dachshund.widgets import BarChart, Number, Table, TableQuery
from discord import Member

from bot import app

activity_page = Page("activity", title="Activity")


MEMBER_SORT_KEYS: dict[str, Callable[[Member], Any]] = {
    "id": lambda member: member.id,
    "name": lambda member: member.name.lower(),
    "nickname": lambda member: (member.nick or "").lower(),
    "joined at": lambda member: member.joined_at,
}


def _member_row(member: Member) -> dict[str, Any]:
    return {
        "id": member.id,
        "name": member.name,
        "nickname": member.nick,
        "joined at": member.joined_at.strftime("%a %d %b %Y"),
    }


def _matches(member: Member, search: str) -> bool:
    needle = search.lower()
    haystack = (str(member.id), member.name, member.nick or "")

    return any(needle in value.lower() for value in haystack)


def load_members(ctx: dict, query: TableQuery) -> tuple[list[dict[str, Any]], int]:
    guild = ctx["bot"].get_guild(app.config.get("client", "guild_id"))
    members = list(guild.members) if guild else []

    if query.search:
        members = [member for member in members if _matches(member, query.search)]

    if sort_key := MEMBER_SORT_KEYS.get(query.sort_by):
        members.sort(key=sort_key, reverse=query.descending)

    page = members[query.offset : query.offset + query.limit]

    return [_member_row(member) for member in page], len(members)


with activity_page.row():
    with activity_page.column(span=4):
        activity_page.add(Number("member_count"))
        activity_page.add(
            Number(
                "active_members",
                title="Active Today",
                source="message",
                y="author",
                aggregate="distinct",
                over="day",
            )
        )
    activity_page.add(
        Table(
            "members",
            columns=["id", "name", "nickname", "joined at"],
            search=True,
            page_size=5,
            loader=load_members,
        )
    )

with activity_page.row():
    with activity_page.column(span=4):
        activity_page.add(
            Number(
                "daily_message_rate",
                title="Today's Messages Rate",
                source="message",
                aggregate="count",
                over="day",
            )
        )

    activity_page.add(
        BarChart(
            "weekly_message_counts",
            title="Messages / day",
            source="message",
            x="date",
            persist=True,
        )
    )

with activity_page.row():
    activity_page.add(
        BarChart("on_command", title="Calls Per Command", x="name", persist=True)
    )

with activity_page.row():
    activity_page.add(
        BarChart("command_error", title="Errors Per Command", x="name", persist=True)
    )
