from configparser import ConfigParser
from dataclasses import replace

import pytest

from lib.dashboard.auth import AuthSettings
from lib.dashboard.auth.settings import REQUIRED
from tests.lib.dashboard.auth.settings import SETTINGS

DASHBOARD = {
    "client_id": "1234",
    "client_secret": "client-secret",
    "redirect_uri": "https://grace.example/_auth/callback",
    "session_secret": "session-secret",
}


class FakeConfig:
    def __init__(self, environment=None, dashboard=None, guild_id=99):
        parser = ConfigParser()
        parser.read_dict({"env": environment or {}})
        self.environment = parser["env"]
        self._values = {("client", "guild_id"): guild_id}
        self._values |= {("dashboard", k): v for k, v in (dashboard or {}).items()}

    def get(self, section, key, *_):
        return self._values.get((section, key))


def test_from_config__expect_every_setting():
    config = FakeConfig({"dashboard_auth": "True"}, {**DASHBOARD, "role_id": 5})

    assert AuthSettings.from_config(config) == replace(SETTINGS, role_id=5)


def test_from_config__without_flag__expect_enabled():
    assert AuthSettings.from_config(FakeConfig(dashboard=DASHBOARD)).enabled is True


def test_from_config__with_flag_off__expect_disabled_without_settings():
    settings = AuthSettings.from_config(FakeConfig({"dashboard_auth": "False"}))

    assert settings.enabled is False
    assert settings.host == "127.0.0.1"


@pytest.mark.parametrize("role_id", [None, ""])
def test_from_config__without_role__expect_none(role_id):
    config = FakeConfig(dashboard={**DASHBOARD, "role_id": role_id})

    assert AuthSettings.from_config(config).role_id is None


@pytest.mark.parametrize("key", REQUIRED)
def test_enabled__with_missing_setting__expect_error(key):
    with pytest.raises(RuntimeError, match=key):
        replace(SETTINGS, **{key: ""})


def test_host__when_enabled__expect_every_interface():
    assert SETTINGS.host == "0.0.0.0"


@pytest.mark.parametrize("client_id", ["1234# Developer portal", "abc", "12 34"])
def test_enabled__with_non_numeric_client_id__expect_error(client_id):
    with pytest.raises(RuntimeError, match="client_id"):
        replace(SETTINGS, client_id=client_id)
