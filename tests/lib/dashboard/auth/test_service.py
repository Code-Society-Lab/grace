from contextlib import asynccontextmanager
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from aiohttp import WSMsgType, web
from aiohttp.test_utils import TestClient, TestServer
from yarl import URL

from lib.dashboard.auth import AuthService, AuthSettings
from lib.dashboard.auth.session import Sessions
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


@pytest.mark.asyncio
async def test_secured__without_session__page_expect_login_redirect():
    async with _client(secured=True) as client:
        response = await client.get(
            "/activity?x=1", headers={"Accept": "text/html"}, allow_redirects=False
        )

        location = URL(response.headers["Location"])
        assert response.status == 302
        assert location.path == "/auth/login"
        assert location.query["next"] == "/activity?x=1"


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["GET", "POST"])
async def test_secured__without_session__request_expect_unauthorized(method):
    async with _client(secured=True) as client:
        response = await client.request(method, "/_widgets/logs/page")

        assert response.status == 401


@pytest.mark.asyncio
async def test_secured__with_stranger_session__expect_unauthorized():
    async with _client(secured=True) as client:
        response = await client.get("/_widgets/logs/page", cookies=_session(STRANGER))

        assert response.status == 401


@pytest.mark.asyncio
async def test_secured__without_session__websocket_expect_refused():
    async with _client(secured=True) as client:
        with pytest.raises(Exception):
            await client.ws_connect("/_ws")


@pytest.mark.asyncio
async def test_secured__login_route__expect_open_without_session():
    async with _client(secured=True) as client:
        response = await client.get("/auth/login", allow_redirects=False)

        assert response.status == 302
        assert response.headers["Location"].startswith("https://discord.com/")


@pytest.mark.asyncio
async def test_secured__with_admin_session__expect_proxied():
    async with _client(secured=True) as client:
        response = await client.post(
            "/_actions/run?x=1", data="payload", cookies=_session(ADMIN)
        )

        body = await response.json()
        assert response.status == 200
        assert response.headers["X-Upstream"] == "yes"
        assert body["method"] == "POST"
        assert body["path"] == "/_actions/run?x=1"
        assert body["body"] == "payload"


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
    async with _client(secured=True) as client:
        client.session.cookie_jar.update_cookies(_session(ADMIN))
        ws = await client.ws_connect("/_ws")

        await ws.send_str("hi")
        message = await ws.receive(timeout=2)
        await ws.close()

        assert message.type == WSMsgType.TEXT
        assert message.data == "echo hi"
