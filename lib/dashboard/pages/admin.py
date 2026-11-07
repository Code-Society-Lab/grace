from typing import Any, Callable

from dachshund import Page
from dachshund.widgets import BarChart, Logs, Table, TableQuery
from discord import Member

from bot import app

admin_page = Page("admin", title="Admin")


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


with admin_page.row():
    admin_page.add(Logs("logs", title="Logs"))

with admin_page.row():
    admin_page.add(
        Table(
            "members",
            columns=["id", "name", "nickname", "joined at"],
            search=True,
            page_size=5,
            loader=load_members,
        )
    )

with admin_page.row():
    admin_page.add(
        BarChart("command_error", title="Errors Per Command", x="name", persist=True)
    )
