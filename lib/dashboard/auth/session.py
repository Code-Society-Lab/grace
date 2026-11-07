"""Signed session cookies holding a Discord user id."""

import hashlib
import hmac
import time
from urllib.parse import urlsplit

from aiohttp import web


class Sessions:
    """Signs and reads session cookies with `secret`."""

    COOKIE = "grace_session"
    TTL = 7 * 24 * 60 * 60

    def __init__(self, secret: str) -> None:
        self._secret = secret.encode()

    def _signature(self, payload: str) -> str:
        return hmac.new(self._secret, payload.encode(), hashlib.sha256).hexdigest()

    def sign(self, user_id: int, now: float | None = None) -> str:
        """A cookie value for `user_id`, valid for `TTL` seconds."""
        expires_at = int((time.time() if now is None else now) + self.TTL)
        payload = f"{user_id}.{expires_at}"

        return f"{payload}.{self._signature(payload)}"

    def read(self, cookie: str | None, now: float | None = None) -> int | None:
        """The user id in `cookie`, or `None` if it's missing, tampered with or expired."""
        if not cookie:
            return None

        try:
            user_id, expires_at, signature = cookie.split(".")
            payload = f"{user_id}.{expires_at}"

            if not hmac.compare_digest(signature, self._signature(payload)):
                return None

            if int(expires_at) < (time.time() if now is None else now):
                return None

            return int(user_id)
        except ValueError:
            return None

    def current_user(self, request: web.Request) -> int | None:
        """The user id of `request`'s session, if it has a valid one."""
        return self.read(request.cookies.get(self.COOKIE))


def safe_next(value: str | None) -> str:
    """The path and query of `value`, `/` if that isn't a path on this site.

    The dashboard sends its own full URL, behind the proxy, so only the path is kept.
    """
    parts = urlsplit(value or "")
    path = parts.path

    if not path.startswith("/") or path.startswith(("//", "/\\")):
        return "/"

    return f"{path}?{parts.query}" if parts.query else path


def set_cookie(response: web.Response, name: str, value: str, max_age: int) -> None:
    response.set_cookie(
        name,
        value,
        max_age=max_age,
        path="/",
        httponly=True,
        secure=True,
        samesite="Lax",
    )


def redirect(location: str) -> web.Response:
    """A 302 to `location`, returned rather than raised so it can set cookies."""
    return web.Response(status=302, headers={"Location": location})
