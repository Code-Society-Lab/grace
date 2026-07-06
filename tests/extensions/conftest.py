from unittest.mock import MagicMock

import pytest

@pytest.fixture
def mock_bot():
    """Create a mock Discord bot instance."""
    bot = MagicMock()
    bot.default_color = 0xFFFFFF
    bot.app.config.get = MagicMock(return_value=None)
    bot.scheduler = MagicMock()
    return bot
