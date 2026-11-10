"""Who may see the dashboard's private pages, and the Discord login that decides it."""

import asyncio
from typing import Any

import dachshund
from aiohttp import web

from lib.dashboard.auth.oauth import DiscordOAuth
from lib.dashboard.auth.session import Sessions
from lib.dashboard.auth.settings import AuthSettings


def client_ip(request: web.Request) -> str:
    """The visitor's address: the first X-Forwarded-For hop behind Railway's proxy."""
    forwarded = request.headers.get("X-Forwarded-For", "")

    return forwarded.split(",")[0].strip() or request.remote or ""


class AuthService:
    """Lets in guild administrators and members with the configured role.

    The dashboard decides which pages are private, asks `authorize`, and serves
    the Discord login itself.
    """

    def __init__(self, bot: Any, settings: AuthSettings) -> None:
        self.bot = bot
        self.settings = settings
        self.sessions = Sessions(settings.session_secret)
        self.oauth = DiscordOAuth(settings, self.sessions, self.record_login)

    def is_allowed(self, user_id: int | None) -> bool:
        guild = self.bot.get_guild(self.settings.guild_id)
        member = guild.get_member(user_id) if guild and user_id else None

        if member is None:
            return False

        return member.guild_permissions.administrator or any(
            role.id == self.settings.role_id for role in member.roles
        )

    async def _lookup(self, user_id: int) -> tuple[str, bool]:
        """The user's name, and whether they may see private pages."""
        guild = self.bot.get_guild(self.settings.guild_id)
        user = (guild.get_member(user_id) if guild else None) or self.bot.get_user(
            user_id
        )

        return (str(user) if user else "unknown"), self.is_allowed(user_id)

    async def record_login(
        self, request: web.Request, result: str, user_id: int | None
    ) -> None:
        """Log a login attempt or logout to the dashboard logins table.

        The dashboard serves the login on its own thread, so reading the member
        cache hops onto the bot's loop. A Discord login without access is
        "denied": the session starts, but private pages stay closed.
        """
        name, allowed = "", False

        if user_id is not None:
            name, allowed = await asyncio.wrap_future(
                asyncio.run_coroutine_threadsafe(self._lookup(user_id), self.bot.loop)
            )

        if result == "login" and not allowed:
            result = "denied"

        dachshund.emit(
            "dashboard_logins",
            user=name,
            id="" if user_id is None else str(user_id),
            result=result,
            ip=client_ip(request),
        )

    async def authorize(self, request: web.Request) -> bool:
        """The dashboard's `authorize`, run on the bot's loop, so reading the
        member cache is safe. Losing access ends the session on the next request.
        """
        return self.is_allowed(self.sessions.current_user(request))

    def dashboard_access(self) -> dict[str, Any]:
        """The dashboard's `host` and `port`, and its `authorize` and `login` when the login is on."""
        address = {"host": self.settings.host, "port": self.settings.port}

        if not self.settings.enabled:
            return address

        return {
            **address,
            "authorize": self.authorize,
            "login": self.oauth.handlers(),
        }
