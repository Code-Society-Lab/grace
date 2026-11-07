"""Who may see the dashboard's private pages, and the Discord login that decides it."""

from typing import Any

from aiohttp import web

from lib.dashboard.auth.oauth import DiscordOAuth
from lib.dashboard.auth.session import Sessions
from lib.dashboard.auth.settings import AuthSettings


class AuthService:
    """Lets in guild administrators and members with the configured role.

    The dashboard decides which pages are private, asks `authorize`, and serves
    the Discord login itself.
    """

    def __init__(self, bot: Any, settings: AuthSettings) -> None:
        self.bot = bot
        self.settings = settings
        self.sessions = Sessions(settings.session_secret)
        self.oauth = DiscordOAuth(settings, self.sessions)

    def is_allowed(self, user_id: int | None) -> bool:
        guild = self.bot.get_guild(self.settings.guild_id)
        member = guild.get_member(user_id) if guild and user_id else None

        if member is None:
            return False

        return member.guild_permissions.administrator or any(
            role.id == self.settings.role_id for role in member.roles
        )

    async def authorize(self, request: web.Request) -> bool:
        """The dashboard's `authorize`, run on the bot's loop, so reading the
        member cache is safe. Losing access ends the session on the next request.
        """
        return self.is_allowed(self.sessions.current_user(request))

    def dashboard_access(self) -> dict[str, Any]:
        """The dashboard's `host`, and its `authorize` and `login` when the login is on."""
        if not self.settings.enabled:
            return {"host": self.settings.host}

        return {
            "host": self.settings.host,
            "authorize": self.authorize,
            "login": self.oauth.handlers(),
        }
