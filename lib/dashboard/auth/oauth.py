"""Discord OAuth2 login, with the `identify` scope."""

import hmac
import secrets

from aiohttp import BasicAuth, ClientSession, web
from discord.utils import oauth_url

from lib.dashboard.auth.session import Sessions, redirect, safe_next, set_cookie
from lib.dashboard.auth.settings import AuthSettings

DISCORD_API_URL = "https://discord.com/api/v10"


class DiscordOAuth:
    """The login, callback and logout routes."""

    LOGIN_PATH = "/login"
    CALLBACK_PATH = "/auth/callback"
    LOGOUT_PATH = "/logout"

    STATE_COOKIE = "grace_oauth_state"
    STATE_TTL = 10 * 60

    def __init__(self, settings: AuthSettings, sessions: Sessions) -> None:
        self.settings = settings
        self.sessions = sessions

    def routes(self) -> list[web.RouteDef]:
        return [
            web.get(self.LOGIN_PATH, self.login),
            web.get(self.CALLBACK_PATH, self.callback),
            web.get(self.LOGOUT_PATH, self.logout),
        ]

    async def login(self, request: web.Request) -> web.Response:
        """Send the visitor to Discord, remembering `next` and a fresh `state`."""
        state = secrets.token_urlsafe(32)
        response = redirect(
            oauth_url(
                self.settings.client_id,
                redirect_uri=self.settings.redirect_uri,
                scopes=["identify"],
                state=state,
            )
        )
        next_path = safe_next(request.query.get("next"))
        set_cookie(response, self.STATE_COOKIE, f"{state}|{next_path}", self.STATE_TTL)

        return response

    async def callback(self, request: web.Request) -> web.Response:
        """Finish the login: check `state`, start a session, return to `next`."""
        cookie = request.cookies.get(self.STATE_COOKIE, "")
        expected, _, next_path = cookie.partition("|")
        state = request.query.get("state", "")
        code = request.query.get("code")

        if not expected or not code or not hmac.compare_digest(state, expected):
            raise web.HTTPBadRequest(text="Invalid login attempt.")

        try:
            user_id = await self.fetch_user_id(code)
        except Exception as exc:
            raise web.HTTPBadGateway(text="Could not reach Discord.") from exc

        response = redirect(safe_next(next_path))
        response.del_cookie(self.STATE_COOKIE, path="/")
        set_cookie(response, Sessions.COOKIE, self.sessions.sign(user_id), Sessions.TTL)

        return response

    async def logout(self, _request: web.Request) -> web.Response:
        """End the session and return to the dashboard's home."""
        response = redirect("/")
        response.del_cookie(Sessions.COOKIE, path="/")

        return response

    async def fetch_user_id(self, code: str) -> int:
        """Exchange an OAuth2 `code` for the id of the Discord user who granted it.

        The token is only used for this, then dropped.
        """
        async with ClientSession() as http:
            async with http.post(
                f"{DISCORD_API_URL}/oauth2/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.settings.redirect_uri,
                },
                auth=BasicAuth(self.settings.client_id, self.settings.client_secret),
            ) as response:
                response.raise_for_status()
                token = (await response.json())["access_token"]

            async with http.get(
                f"{DISCORD_API_URL}/users/@me",
                headers={"Authorization": f"Bearer {token}"},
            ) as response:
                response.raise_for_status()
                return int((await response.json())["id"])
