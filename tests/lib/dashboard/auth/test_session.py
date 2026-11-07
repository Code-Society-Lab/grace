import pytest
from aiohttp.test_utils import make_mocked_request

from lib.dashboard.auth.session import Sessions, safe_next

SESSIONS = Sessions("session-secret")


def test_read__with_signed_cookie__expect_user_id():
    assert SESSIONS.read(SESSIONS.sign(42)) == 42


@pytest.mark.parametrize("cookie", [None, "", "garbage", "42.9999999999.bad"])
def test_read__with_invalid_cookie__expect_none(cookie):
    assert SESSIONS.read(cookie) is None


def test_read__with_tampered_user__expect_none():
    _, expires_at, signature = SESSIONS.sign(42).split(".")

    assert SESSIONS.read(f"1.{expires_at}.{signature}") is None


def test_read__after_expiry__expect_none():
    cookie = SESSIONS.sign(42, now=0)

    assert SESSIONS.read(cookie, now=Sessions.TTL + 1) is None


def test_read__with_other_secret__expect_none():
    assert Sessions("rotated").read(SESSIONS.sign(42)) is None


def test_current_user__with_session_cookie__expect_user_id():
    cookie = f"{Sessions.COOKIE}={SESSIONS.sign(42)}"
    request = make_mocked_request("GET", "/", headers={"Cookie": cookie})

    assert SESSIONS.current_user(request) == 42


def test_current_user__without_cookie__expect_none():
    assert SESSIONS.current_user(make_mocked_request("GET", "/")) is None


@pytest.mark.parametrize(
    "value, expected",
    [
        ("/activity", "/activity"),
        ("/activity/tab?x=1", "/activity/tab?x=1"),
        (None, "/"),
        ("", "/"),
        ("https://evil.example", "/"),
        ("//evil.example", "/"),
        ("/\\evil.example", "/"),
    ],
)
def test_safe_next(value, expected):
    assert safe_next(value) == expected
