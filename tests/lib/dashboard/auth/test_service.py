from contextlib import asynccontextmanager
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from aiohttp.test_utils import TestClient, TestServer, make_mocked_request
from dachshund import Dashboard, Page
from dachshund.widgets import Text
from yarl import URL

from lib.dashboard.auth import AuthService, AuthSettings
from lib.dashboard.auth.session import Sessions, safe_next
from tests.lib.dashboard.auth.settings import SETTINGS

ADMIN = 42
STRANGER = 7
ROLE = 5
SESSIONS = Sessions(SETTINGS.session_secret)


def _member(administrator=False, roles=()):
    return SimpleNamespace(
        guild_permissions=SimpleNamespace(administrator=administrator),
        roles=[SimpleNamespace(id=role) for role in roles],
    )


def _bot(members=None, guild=True):
    members = {ADMIN: _member(administrator=True)} if members is None else members
    guild_obj = MagicMock()
    guild_obj.get_member.side_effect = members.get

    bot = MagicMock()
    bot.get_guild.return_value = guild_obj if guild else None
    return bot


def _service(bot=None, settings=SETTINGS):
    return AuthService(bot or _bot(), settings)


def test_is_allowed__with_administrator__expect_true():
    bot = _bot()

    assert _service(bot).is_allowed(ADMIN) is True
    bot.get_guild.assert_called_once_with(99)


def test_is_allowed__with_configured_role__expect_true():
    service = _service(
        _bot({STRANGER: _member(roles=[1, ROLE])}), replace(SETTINGS, role_id=ROLE)
    )

    assert service.is_allowed(STRANGER) is True


def test_is_allowed__with_other_roles__expect_false():
    service = _service(
        _bot({STRANGER: _member(roles=[1, 2])}), replace(SETTINGS, role_id=ROLE)
    )

    assert service.is_allowed(STRANGER) is False


def test_is_allowed__without_configured_role__expect_only_administrators():
    assert (
        _service(_bot({STRANGER: _member(roles=[ROLE])})).is_allowed(STRANGER) is False
    )


def test_is_allowed__when_not_in_guild__expect_false():
    assert _service().is_allowed(STRANGER) is False


def test_is_allowed__when_guild_unavailable__expect_false():
    assert _service(_bot(guild=False)).is_allowed(ADMIN) is False


def test_is_allowed__without_user__expect_false():
    assert _service().is_allowed(None) is False


def _session(user_id):
    return {Sessions.COOKIE: SESSIONS.sign(user_id)}


def test_dashboard_access__when_enabled__expect_authorize_and_the_login_handlers():
    service = _service()
    access = service.dashboard_access()

    assert access["host"] == "0.0.0.0"
    assert access["authorize"] == service.authorize
    assert sorted(access["login"]) == ["callback", "login", "logout"]


def test_dashboard_access__when_disabled__expect_this_machine_only():
    service = _service(settings=AuthSettings(enabled=False, guild_id=99))

    assert service.dashboard_access() == {"host": "127.0.0.1"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, expected", [(None, False), (STRANGER, False), (ADMIN, True)]
)
async def test_authorize__expect_only_allowed_sessions(user_id, expected):
    headers = {}

    if user_id:
        headers["Cookie"] = f"{Sessions.COOKIE}={SESSIONS.sign(user_id)}"

    request = make_mocked_request("GET", "/", headers=headers)

    assert await _service().authorize(request) is expected


@asynccontextmanager
async def _dashboard_client():
    """A real dashboard with the service's login, a public and a private page."""
    service = _service()
    access = service.dashboard_access()
    access.pop("host")
    dashboard = Dashboard(path=":memory:", **access)

    public = Page("open", title="Open", public=True)
    private = Page("admin", title="Admin")

    for page, widget in ((public, "hello"), (private, "secret")):
        with page.row():
            page.add(Text(widget))

    dashboard.include(public)
    dashboard.include(private)

    client = TestClient(TestServer(dashboard._create_app()))
    await client.start_server()

    try:
        yield client
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_secured__public_page__expect_shown_without_session():
    async with _dashboard_client() as client:
        response = await client.get("/open")

        assert response.status == 200


@pytest.mark.asyncio
@pytest.mark.parametrize("user_id", [None, STRANGER])
async def test_secured__private_page__expect_login_redirect_back_to_it(user_id):
    async with _dashboard_client() as client:
        cookies = _session(user_id) if user_id else {}
        response = await client.get("/admin", cookies=cookies, allow_redirects=False)

        location = URL(response.headers["Location"])
        assert response.status == 302
        assert location.path == "/_auth/login"
        assert safe_next(location.query["next"]) == "/admin"


@pytest.mark.asyncio
async def test_secured__private_page__with_admin_session__expect_shown():
    async with _dashboard_client() as client:
        response = await client.get("/admin", cookies=_session(ADMIN))

        assert response.status == 200


@pytest.mark.asyncio
async def test_secured__login_route__expect_discord():
    async with _dashboard_client() as client:
        response = await client.get("/_auth/login", allow_redirects=False)

        assert response.status == 302
        assert response.headers["Location"].startswith("https://discord.com/")
