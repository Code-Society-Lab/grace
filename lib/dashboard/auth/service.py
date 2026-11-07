"""The dashboard's front door: a Discord login, then a proxy to dachshund."""

import logging
from typing import Any
from urllib.parse import urlencode

from aiohttp import web
from yarl import URL

from lib.dashboard.auth.oauth import DiscordOAuth
from lib.dashboard.auth.proxy import client_session, proxy_to
from lib.dashboard.auth.session import Sessions
from lib.dashboard.auth.settings import AuthSettings

logger = logging.getLogger(__name__)


class AuthService:
    """Serves `upstream` on `PORT`, behind a Discord login when enabled.

    Guild administrators get in, and members with the configured role.
    """

    PORT = 1212
    PUBLIC_PREFIX = "/auth/"

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

    @web.middleware
    async def require_login(self, request: web.Request, handler):
        # Runs on the bot's loop, so reading the member cache is safe, and
        # losing access ends the session on the next request.
        if request.path.startswith(self.PUBLIC_PREFIX) or self.is_allowed(
            self.sessions.current_user(request)
        ):
            return await handler(request)

        if request.method == "GET" and "text/html" in request.headers.get("Accept", ""):
            query = urlencode({"next": request.path_qs})
            raise web.HTTPFound(f"{self.oauth.LOGIN_PATH}?{query}")

        raise web.HTTPUnauthorized()

    def build_app(self) -> web.Application:
        secured = self.settings.enabled
        app = web.Application(middlewares=[self.require_login] if secured else [])
        app.cleanup_ctx.append(client_session)

        if secured:
            app.add_routes(self.oauth.routes())

        app.add_routes([web.route("*", "/{tail:.*}", proxy_to(self.upstream))])

        return app

    async def start(self) -> None:
        if not self.settings.enabled:
            logger.warning("Dashboard login is off, serving it on this machine only.")

        self._runner = web.AppRunner(self.build_app())
        await self._runner.setup()
        await web.TCPSite(self._runner, self.settings.host, self.PORT).start()

    async def stop(self) -> None:
        if self._runner is not None:
            await self._runner.cleanup()
            self._runner = None
