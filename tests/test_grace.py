from types import SimpleNamespace
from zoneinfo import ZoneInfo

from bot.grace import Grace


def test_timezone__expect_the_configured_zone():
    bot = SimpleNamespace(config={"timezone": "US/Eastern"})

    assert Grace.timezone.fget(bot) == ZoneInfo("US/Eastern")


def test_guild_id__expect_the_configured_id_as_an_int():
    bot = SimpleNamespace(config={"guild_id": "1349"})

    assert Grace.guild_id.fget(bot) == 1349


def test_guild_id__with_no_configured_id__expect_none():
    bot = SimpleNamespace(config={"guild_id": ""})

    assert Grace.guild_id.fget(bot) is None


def test_guild__expect_the_guild_for_the_configured_id():
    guild = object()
    bot = SimpleNamespace(
        guild_id=1349,
        get_guild=lambda guild_id: guild if guild_id == 1349 else None,
    )

    assert Grace.guild.fget(bot) is guild


def test_guild__with_no_configured_id__expect_none():
    bot = SimpleNamespace(guild_id=None, get_guild=lambda guild_id: object())

    assert Grace.guild.fget(bot) is None
