from unittest.mock import MagicMock
from zoneinfo import ZoneInfo

import pytest


@pytest.fixture
def mock_bot():
    """Create a mock Discord bot instance."""
    bot = MagicMock()
    bot.default_color = 0xFFFFFF
    bot.timezone = ZoneInfo("US/Eastern")
    bot.app.config.get = MagicMock(return_value=None)
    bot.scheduler = MagicMock()
    return bot
