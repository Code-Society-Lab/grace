import asyncio
from contextlib import asynccontextmanager
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from aiohttp.test_utils import TestClient, TestServer, make_mocked_request
from dachshund import Dashboard, Page
from dachshund.widgets import Text
from yarl import URL

from lib.dashboard.auth import AuthService, AuthSettings
from lib.dashboard.auth.service import client_ip
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


class _Named(SimpleNamespace):
    def __str__(self):
        return self.name


def _login_bot():
    admin = _Named(
        name="ada",
        guild_permissions=SimpleNamespace(administrator=True),
        roles=[],
    )
    stranger = _Named(
        name="bob", guild_permissions=SimpleNamespace(administrator=False), roles=[]
    )
    bot = _bot({ADMIN: admin})
    # Not in the guild, but still a Discord user the bot can name.
    bot.get_user.side_effect = {STRANGER: stranger}.get
    bot.loop = asyncio.get_running_loop()
    return bot


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "result, user_id, expected",
    [
        ("login", ADMIN, {"result": "login", "user": "ada", "id": "42"}),
        ("login", STRANGER, {"result": "denied", "user": "bob", "id": "7"}),
        ("logout", ADMIN, {"result": "logout", "user": "ada", "id": "42"}),
        ("invalid", None, {"result": "invalid", "user": "", "id": ""}),
    ],
)
@patch("lib.dashboard.auth.service.dachshund.emit")
async def test_record_login__expect_named_row_denied_without_access(
    mock_record, result, user_id, expected
):
    request = make_mocked_request("GET", "/_auth/callback")

    await _service(_login_bot()).record_login(request, result, user_id)

    mock_record.assert_called_once_with("dashboard_logins", ip="", **expected)


@pytest.mark.asyncio
@patch("lib.dashboard.auth.service.dachshund.emit")
async def test_record_login__from_another_thread__expect_lookup_on_the_bots_loop(
    mock_record,
):
    """The dashboard serves the login on its own thread and loop."""
    service = _service(_login_bot())
    request = make_mocked_request("GET", "/_auth/callback")

    await asyncio.to_thread(asyncio.run, service.record_login(request, "login", ADMIN))

    assert mock_record.call_args.args == ("dashboard_logins",)
    assert mock_record.call_args.kwargs["result"] == "login"
    assert mock_record.call_args.kwargs["user"] == "ada"


@pytest.mark.parametrize(
    "headers, expected",
    [
        ({"X-Forwarded-For": "203.0.113.7, 10.0.0.1"}, "203.0.113.7"),
        ({}, ""),
    ],
)
def test_client_ip__expect_the_first_forwarded_hop(headers, expected):
    assert client_ip(make_mocked_request("GET", "/", headers=headers)) == expected
