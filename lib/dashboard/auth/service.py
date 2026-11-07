"""The dashboard's front door: a Discord login, then a proxy to dachshund."""

import logging
from typing import Any

from aiohttp import web
from yarl import URL

from lib.dashboard.auth.oauth import DiscordOAuth
from lib.dashboard.auth.proxy import client_session, proxy_to
from lib.dashboard.auth.session import Sessions
from lib.dashboard.auth.settings import AuthSettings

logger = logging.getLogger(__name__)


class AuthService:
    """Serves `upstream` on `PORT`, with a Discord login when enabled.

    The dashboard decides which pages are private and asks `authorize`, which
    lets in guild administrators and members with the configured role.
    """

    PORT = 1212

    def __init__(self, bot: Any, upstream: URL, settings: AuthSettings) -> None:
        self.bot = bot
        self.upstream = upstream
        self.settings = settings
        self.sessions = Sessions(settings.session_secret)
        self.oauth = DiscordOAuth(settings, self.sessions)
        self._runner: web.AppRunner | None = None

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
        """The `authorize` and `login_url` to start the dashboard with, none when the login is off."""
        if not self.settings.enabled:
            return {}

        return {"authorize": self.authorize, "login_url": self.oauth.LOGIN_PATH}

    def build_app(self) -> web.Application:
        app = web.Application()
        app.cleanup_ctx.append(client_session)

        if self.settings.enabled:
            app.add_routes(self.oauth.routes())

        app.add_routes([web.route("*", "/{tail:.*}", proxy_to(self.upstream))])

        return app

    async def start(self) -> None:
        if not self.settings.enabled:
            logger.warning("Dashboard login is off, serving it on this machine only.")

        # No access log: dachshund already logs each request, and these lines,
        # logged on the bot's thread, would feed the Logs widget its own refreshes.
        self._runner = web.AppRunner(self.build_app(), access_log=None)
        await self._runner.setup()
        await web.TCPSite(self._runner, self.settings.host, self.PORT).start()

    async def stop(self) -> None:
        if self._runner is not None:
            await self._runner.cleanup()
            self._runner = None
