import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytz
from bot.extensions.time_cog import TimeCog


@pytest.fixture
def mock_bot():
    """Create a mock Discord bot instance."""
    return MagicMock()


@pytest.fixture
def time_cog(mock_bot):
    """Instantiate the TimeCog with a mock bot."""
    return TimeCog(mock_bot)


def test_build_regex(time_cog):
    """Test that build regex includes common timezone abbreviations."""
    pattern = time_cog._build_regex()
    assert 'pst' in pattern
    assert 'est' in pattern
    assert 'utc' in pattern
    assert 'jst' in pattern
    assert 'cet' in pattern
    assert 'hkt' in pattern


def test_build_relative_date_today(time_cog):
    """Verify that today is replaced with the current UTC date."""
    now = datetime(2025, 10, 10, tzinfo=pytz.UTC)
    result = time_cog._build_relative_date('today 5pm', now)
    assert '2025-10-10' in result


def test_build_relative_date_tomorrow(time_cog):
    """Verify that tomorrow is replaced with the next day's UTC date."""
    now = datetime(2025, 10, 10, tzinfo=pytz.UTC)
    result = time_cog._build_relative_date('tomorrow 9am', now)
    assert '2025-10-11' in result


def test_build_timestamp_with_timezone(time_cog):
    """Check that timestamp parsing works."""
    utc = pytz.UTC
    result = time_cog._build_timestamp(utc, '2025-10-10 5PM UTC')
    assert isinstance(result, int)
    assert result == 1760115600


@pytest.mark.asyncio
async def test_on_message_valid_timestamp(time_cog):
    """Ensure that the reply has a valid timestamp."""
    mock_message = MagicMock()
    mock_message.author.bot = False
    mock_message.content = "Let's meet at 17:44 JST"
    mock_message.reply = AsyncMock()

    await time_cog.on_message(mock_message)

    mock_message.reply.assert_called_once()
    call_arg = mock_message.reply.call_args[0][0]
    assert call_arg.startswith('<t:')
    assert call_arg.endswith(':F>')


@pytest.mark.asyncio
async def test_on_message_valid_timezone(time_cog):
    """Ensure that messages with valid timezones trigger a reply."""
    mock_message = MagicMock()
    mock_message.author.bot = False
    mock_message.content = "Let's meet tomorrow at 5PM EST"
    mock_message.reply = AsyncMock()

    await time_cog.on_message(mock_message)
    mock_message.reply.assert_called_once()


@pytest.mark.asyncio
async def test_ignores_on_message_without_timezone(time_cog):
    """Ensure that messages without timezones are not triggered."""
    mock_message = MagicMock()
    mock_message.author.bot = False
    mock_message.content = "Let's meet at 5pm"
    mock_message.reply = AsyncMock()

    await time_cog.on_message(mock_message)
    mock_message.reply.assert_not_called()


@pytest.mark.asyncio
async def test_on_message_ignores_bot_messages(time_cog):
    """Ensure bot messages are ignored."""
    mock_message = MagicMock()
    mock_message.author.bot = True
    mock_message.content = '5pm PST'
    mock_message.reply = AsyncMock()

    await time_cog.on_message(mock_message)
    mock_message.reply.assert_not_called()


@pytest.mark.asyncio
async def test_on_message_without_time(time_cog):
    """Ensure messages without time aren't triggered."""
    mock_message = MagicMock()
    mock_message.author.bot = False
    mock_message.content = 'What are you doing today?'
    mock_message.reply = AsyncMock()

    await time_cog.on_message(mock_message)
    mock_message.reply.assert_not_called()
