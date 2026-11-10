from datetime import UTC, datetime, timedelta, tzinfo
from typing import Any, Callable

from dachshund.widgets import TableQuery
from discord import Member

from lib.dashboard.context import DashboardContext
from lib.dashboard.handlers.paging import Page

COLUMNS = ["id", "name", "nickname", "joined at"]
RECENT_COLUMNS = [*COLUMNS, "account created"]
RECENT = timedelta(hours=24)

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


def _members(ctx: DashboardContext) -> list[Member]:
    guild = ctx.bot.get_guild(ctx.bot.config.get("guild_id"))

    return list(guild.members) if guild else []


def _recent_row(member: Member, timezone: tzinfo) -> dict[str, Any]:
    return {
        **_row(member),
        "joined at": member.joined_at.astimezone(timezone).strftime("%a %d %b %H:%M"),
        "account created": member.created_at.strftime("%d %b %Y"),
    }


def _page(
    members: list[Member],
    query: TableQuery,
    row: Callable[[Member], dict[str, Any]],
    newest_first: bool = False,
) -> Page:
    """`members` matching the search, sorted by their own values rather than their text."""
    if query.search:
        members = [member for member in members if _matches(member, query.search)]

    if sort_key := SORT_KEYS.get(query.sort_by):
        members.sort(key=sort_key, reverse=query.descending)
    elif newest_first:
        members.sort(key=SORT_KEYS["joined at"], reverse=True)

    page = members[query.offset : query.offset + query.limit]

    return [row(member) for member in page], len(members)


def load(ctx: DashboardContext, query: TableQuery) -> Page:
    return _page(_members(ctx), query, _row)


def load_recent(ctx: DashboardContext, query: TableQuery) -> Page:
    timezone = ctx.bot.timezone
    since = datetime.now(UTC) - RECENT
    members = [
        member
        for member in _members(ctx)
        if member.joined_at and member.joined_at >= since
    ]

    return _page(
        members,
        query,
        lambda member: _recent_row(member, timezone),
        newest_first=True,
    )
