from lib.dashboard.auth import AuthSettings

SETTINGS = AuthSettings(
    enabled=True,
    guild_id=99,
    client_id="1234",
    client_secret="client-secret",
    redirect_uri="https://grace.example/auth/callback",
    session_secret="session-secret",
)
