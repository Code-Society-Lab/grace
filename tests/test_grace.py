from types import SimpleNamespace
from zoneinfo import ZoneInfo

from bot.grace import Grace


def test_timezone__expect_the_configured_zone():
    bot = SimpleNamespace(config={"timezone": "US/Eastern"})

    assert Grace.timezone.fget(bot) == ZoneInfo("US/Eastern")
