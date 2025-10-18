from datetime import timedelta
from unittest.mock import MagicMock, AsyncMock
import re
import pytest
from discord import Embed
from bot.extensions.reminder_cog import ReminderCog


@pytest.fixture
def mock_bot():
    """Create a mock Discord bot instance."""
    bot = MagicMock()
    bot.default_color = 0xFFFFFF
    bot.app.config.get = MagicMock(return_value=None)
    bot.scheduler = MagicMock()
    return bot


@pytest.fixture
def reminder_cog(mock_bot):
    """Instantiate the ReminderCog with a mock bot."""
    return ReminderCog(mock_bot)


def test_valid_timer(reminder_cog):
    """Verify that valid timer format is parsed correctly."""
    timer = "10m"
    time_pattern = re.compile(r"(\d+)([smhd])")
    match = time_pattern.fullmatch(timer)
    assert match is not None

    result = reminder_cog._build_timer(match)
    assert isinstance(result, timedelta)


def test_invalid_timer(reminder_cog):
    """Verify that invalid timer format is rejected."""
    timer = "10minutes"
    time_pattern = re.compile(r"(\d+)([smhd])")
    match = time_pattern.fullmatch(timer)
    assert match is None


def test_valid_embed(reminder_cog):
    """Verify that embed is built correctly with valid input."""
    title = "Reminder"
    message = "Hello World"
    author = "Astra Al-Maarifa"

    result = reminder_cog._build_embed(title, message, author)
    assert isinstance(result, Embed)


@pytest.mark.asyncio
async def test_reminder_validation(reminder_cog):
    """Verify that reminder works with valid input."""
    ctx = AsyncMock()

    timer = "1m"
    message = "Time for a break!"
    await reminder_cog.reminder.callback(
        reminder_cog,
        ctx,
        timer=timer,
        message=message,
    )

    ctx.send.assert_awaited_once()


@pytest.mark.asyncio
async def test_reminder_failure(reminder_cog):
    """Verify that reminder fails with invalid input."""
    ctx = AsyncMock()

    timer = "one minute"
    message = "Time for a break!"
    await reminder_cog.reminder.callback(
        reminder_cog,
        ctx,
        timer=timer,
        message=message,
    )

    ctx.send.assert_awaited_once()
    args, _ = ctx.send.call_args
    assert "Invalid time format" in args[0]
