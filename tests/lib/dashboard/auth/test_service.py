import asyncio
import logging
from contextlib import asynccontextmanager
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from aiohttp import ClientSession, WSMsgType, web
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


def _service(bot=None, settings=SETTINGS, upstream=URL("http://upstream")):
    return AuthService(bot or _bot(), upstream, settings)


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


async def _echo_ws(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for message in ws:
        if message.type == WSMsgType.TEXT:
            await ws.send_str(f"echo {message.data}")

    return ws


async def _echo(request):
    return web.json_response(
        {
            "method": request.method,
            "path": request.path_qs,
            "body": (await request.read()).decode(),
            "cookie": request.headers.get("Cookie"),
            "host": request.host,
        },
        headers={"X-Upstream": "yes"},
    )


async def _moved(_request):
    raise web.HTTPFound("/elsewhere")


def _upstream():
    app = web.Application()
    app.router.add_get("/_ws", _echo_ws)
    app.router.add_get("/moved", _moved)
    app.router.add_route("*", "/{tail:.*}", _echo)
    return app


@asynccontextmanager
async def _client(*, secured):
    upstream = TestServer(_upstream())
    await upstream.start_server()

    settings = SETTINGS if secured else AuthSettings(enabled=False, guild_id=99)
    app = _service(
        upstream=URL(str(upstream.make_url("/"))), settings=settings
    ).build_app()
    client = TestClient(TestServer(app))
    await client.start_server()

    try:
        yield client
    finally:
        await client.close()
        await upstream.close()


def _session(user_id):
    return {Sessions.COOKIE: SESSIONS.sign(user_id)}


def test_dashboard_access__when_enabled__expect_authorize_and_login_url():
    service = _service()

    assert service.dashboard_access() == {
        "authorize": service.authorize,
        "login_url": "/auth/login",
    }


def test_dashboard_access__when_disabled__expect_nothing():
    service = _service(settings=AuthSettings(enabled=False, guild_id=99))

    assert service.dashboard_access() == {}


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
    """The service in front of a real dashboard with a public and a private page."""
    service = _service()
    dashboard = Dashboard(path=":memory:", **service.dashboard_access())

    public = Page("open", title="Open", public=True)
    private = Page("admin", title="Admin")

    for page, widget in ((public, "hello"), (private, "secret")):
        with page.row():
            page.add(Text(widget))

    dashboard.include(public)
    dashboard.include(private)

    upstream = TestServer(dashboard._create_app())
    await upstream.start_server()
    service.upstream = URL(str(upstream.make_url("/")))

    client = TestClient(TestServer(service.build_app()))
    await client.start_server()

    try:
        yield client
    finally:
        await client.close()
        await upstream.close()


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
        assert location.path == "/auth/login"
        assert safe_next(location.query["next"]) == "/admin"


@pytest.mark.asyncio
async def test_secured__private_page__with_admin_session__expect_shown():
    async with _dashboard_client() as client:
        response = await client.get("/admin", cookies=_session(ADMIN))

        assert response.status == 200


@pytest.mark.asyncio
async def test_secured__login_route__expect_discord():
    async with _dashboard_client() as client:
        response = await client.get("/auth/login", allow_redirects=False)

        assert response.status == 302
        assert response.headers["Location"].startswith("https://discord.com/")


@pytest.mark.asyncio
async def test_proxy__expect_request_forwarded_with_cookies():
    async with _client(secured=False) as client:
        response = await client.post(
            "/_actions/run?x=1", data="payload", cookies={"a": "b"}
        )

        body = await response.json()
        assert response.status == 200
        assert response.headers["X-Upstream"] == "yes"
        assert body["method"] == "POST"
        assert body["path"] == "/_actions/run?x=1"
        assert body["body"] == "payload"
        assert body["cookie"] == "a=b"
        assert body["host"] == f"{client.host}:{client.port}"


@pytest.mark.asyncio
async def test_not_secured__expect_proxied_without_session():
    async with _client(secured=False) as client:
        response = await client.get("/activity", headers={"Accept": "text/html"})

        assert response.status == 200
        assert (await response.json())["path"] == "/activity"


@pytest.mark.asyncio
async def test_not_secured__login_route__expect_proxied():
    async with _client(secured=False) as client:
        response = await client.get("/auth/login")

        assert (await response.json())["path"] == "/auth/login"


@pytest.mark.asyncio
async def test_proxy__upstream_redirect__expect_passed_through():
    async with _client(secured=False) as client:
        response = await client.get("/moved", allow_redirects=False)

        assert response.status == 302
        assert response.headers["Location"] == "/elsewhere"


@pytest.mark.asyncio
async def test_proxy__websocket__expect_messages_both_ways():
    async with _client(secured=False) as client:
        ws = await client.ws_connect("/_ws")

        await ws.send_str("hi")
        message = await ws.receive(timeout=2)
        await ws.close()

        assert message.type == WSMsgType.TEXT
        assert message.data == "echo hi"


@pytest.mark.asyncio
async def test_start__expect_no_access_log(caplog, monkeypatch):
    service = _service(settings=AuthSettings(enabled=False, guild_id=99))
    monkeypatch.setattr(service, "PORT", 0)
    # Test setup (alembic's fileConfig) disables existing loggers.
    monkeypatch.setattr(logging.getLogger("aiohttp.access"), "disabled", False)
    caplog.set_level(logging.INFO, logger="aiohttp.access")
    await service.start()

    try:
        host, port = service._runner.addresses[0][:2]
        async with ClientSession() as http:
            async with http.get(f"http://{host}:{port}/auth/login"):
                pass
        # The access line is written once the response is done.
        await asyncio.sleep(0.05)
    finally:
        await service.stop()

    assert not [r for r in caplog.records if r.name == "aiohttp.access"]
