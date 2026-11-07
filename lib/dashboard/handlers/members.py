from typing import Any, Callable

from dachshund.widgets import TableQuery
from discord import Member

from bot import app
from lib.dashboard.handlers.paging import Page

COLUMNS = ["id", "name", "nickname", "joined at"]

SORT_KEYS: dict[str, Callable[[Member], Any]] = {
    "id": lambda member: member.id,
    "name": lambda member: member.name.lower(),
    "nickname": lambda member: (member.nick or "").lower(),
    "joined at": lambda member: member.joined_at,
}


def _row(member: Member) -> dict[str, Any]:
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


def load(ctx: dict, query: TableQuery) -> Page:
    """The guild's members, sorted by their own values rather than their text."""
    guild = ctx["bot"].get_guild(app.config.get("client", "guild_id"))
    members = list(guild.members) if guild else []

    if query.search:
        members = [member for member in members if _matches(member, query.search)]

    if sort_key := SORT_KEYS.get(query.sort_by):
        members.sort(key=sort_key, reverse=query.descending)

    page = members[query.offset : query.offset + query.limit]

    return [_row(member) for member in page], len(members)
