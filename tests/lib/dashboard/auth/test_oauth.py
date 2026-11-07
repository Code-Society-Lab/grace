from unittest.mock import AsyncMock
from urllib.parse import parse_qs, urlparse

import pytest
from aiohttp import web
from aiohttp.test_utils import make_mocked_request

from lib.dashboard.auth.oauth import DiscordOAuth
from lib.dashboard.auth.session import Sessions
from tests.lib.dashboard.auth.settings import SETTINGS

SESSIONS = Sessions(SETTINGS.session_secret)
STATE = DiscordOAuth.STATE_COOKIE


@pytest.fixture
def oauth():
    return DiscordOAuth(SETTINGS, SESSIONS)


def _request(path="/", cookies=None):
    headers = {}

    if cookies:
        headers["Cookie"] = "; ".join(f"{k}={v}" for k, v in cookies.items())

    return make_mocked_request("GET", path, headers=headers)


@pytest.mark.asyncio
async def test_login__expect_redirect_to_discord_with_state_cookie(oauth):
    response = await oauth.login(_request("/login?next=/activity"))

    location = urlparse(response.headers["Location"])
    query = parse_qs(location.query)
    state, _, next_path = response.cookies[STATE].value.partition("|")

    assert response.status == 302
    assert f"{location.netloc}{location.path}" == "discord.com/oauth2/authorize"
    assert query["client_id"] == ["1234"]
    assert query["response_type"] == ["code"]
    assert query["scope"] == ["identify"]
    assert query["redirect_uri"] == [SETTINGS.redirect_uri]
    assert query["state"] == [state]
    assert next_path == "/activity"


@pytest.mark.asyncio
async def test_login__with_offsite_next__expect_home(oauth):
    response = await oauth.login(_request("/login?next=//evil.example"))

    assert response.cookies[STATE].value.endswith("|/")


@pytest.mark.asyncio
async def test_callback__with_matching_state__expect_session_and_redirect(oauth):
    oauth.fetch_user_id = AsyncMock(return_value=42)
    request = _request(
        "/auth/callback?code=abc&state=xyz", cookies={STATE: "xyz|/activity"}
    )

    response = await oauth.callback(request)

    oauth.fetch_user_id.assert_awaited_once_with("abc")
    assert response.status == 302
    assert response.headers["Location"] == "/activity"
    assert SESSIONS.read(response.cookies[Sessions.COOKIE].value) == 42
    assert response.cookies[Sessions.COOKIE]["httponly"] is True
    assert response.cookies[STATE].value == ""


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path, cookies",
    [
        ("/auth/callback?code=abc&state=wrong", {STATE: "xyz|/"}),
        ("/auth/callback?code=abc&state=xyz", {}),
        ("/auth/callback?state=xyz", {STATE: "xyz|/"}),
        ("/auth/callback?code=abc&state=", {STATE: "|/"}),
    ],
)
async def test_callback__with_bad_state_or_code__expect_bad_request(
    oauth, path, cookies
):
    oauth.fetch_user_id = AsyncMock(return_value=42)

    with pytest.raises(web.HTTPBadRequest):
        await oauth.callback(_request(path, cookies=cookies))

    oauth.fetch_user_id.assert_not_awaited()


@pytest.mark.asyncio
async def test_callback__when_discord_fails__expect_bad_gateway(oauth):
    oauth.fetch_user_id = AsyncMock(side_effect=OSError)
    request = _request("/auth/callback?code=abc&state=xyz", cookies={STATE: "xyz|/"})

    with pytest.raises(web.HTTPBadGateway):
        await oauth.callback(request)


@pytest.mark.asyncio
async def test_logout__expect_session_cleared(oauth):
    response = await oauth.logout(_request("/logout"))

    assert response.status == 302
    assert response.headers["Location"] == "/"
    assert response.cookies[Sessions.COOKIE].value == ""
