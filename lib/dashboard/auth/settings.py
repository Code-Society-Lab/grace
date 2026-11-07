"""The dashboard login's settings, read and checked once at startup."""

from dataclasses import dataclass
from typing import Any

REQUIRED = ("client_id", "client_secret", "redirect_uri", "session_secret")


@dataclass(frozen=True)
class AuthSettings:
    """`[dashboard]` and the environment's `dashboard_auth`.

    The login is on unless the environment sets `dashboard_auth = False`, so
    an environment that doesn't mention it never serves the dashboard openly.
    """

    enabled: bool
    guild_id: int
    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = ""
    session_secret: str = ""
    role_id: int | None = None

    def __post_init__(self) -> None:
        missing = [key for key in REQUIRED if self.enabled and not getattr(self, key)]

        if missing:
            raise RuntimeError(f"Missing dashboard settings: {', '.join(missing)}.")

        # It goes in the login URL as is, so stray text, like an inline comment
        # in .env, would break it.
        if self.enabled and not self.client_id.isdigit():
            raise RuntimeError(
                "The dashboard client_id must be the application's numeric id."
            )

    @classmethod
    def from_config(cls, config: Any) -> "AuthSettings":
        def get(key: str) -> str:
            return str(config.get("dashboard", key) or "")

        return cls(
            enabled=config.environment.getboolean("dashboard_auth", fallback=True),
            guild_id=config.get("client", "guild_id"),
            client_id=get("client_id"),
            client_secret=get("client_secret"),
            redirect_uri=get("redirect_uri"),
            session_secret=get("session_secret"),
            role_id=int(get("role_id")) if get("role_id") else None,
        )

    @property
    def host(self) -> str:
        """Where the service listens: only this machine when the login is off."""
        return "0.0.0.0" if self.enabled else "127.0.0.1"
