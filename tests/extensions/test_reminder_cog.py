import re
import pytest

from datetime import timedelta, datetime
from freezegun import freeze_time
from unittest.mock import MagicMock, AsyncMock
from discord import Embed
from bot.extensions.reminder_cog import ReminderCog
from dateutil.tz import tzlocal


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


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("10s", timedelta(seconds=10)),
        ("5m", timedelta(minutes=5)),
        ("2h", timedelta(hours=2)),
        ("1d", timedelta(days=1)),
        ("0s", timedelta(seconds=0)),
    ],
)
def test_convert_to_timedelta_valid_formats(reminder_cog, input_str, expected):
    """Ensure _convert_to_timedelta correctly parses valid time strings."""
    pattern = re.compile(r"(\d+)([smhd])")
    match = pattern.fullmatch(input_str)
    assert match, f"Regex failed to match valid timer format '{input_str}'"

    result = reminder_cog._convert_to_timedelta(match)

    assert isinstance(result, timedelta), f"Expected timedelta, got {type(result)}"
    assert result == expected, f"For '{input_str}', expected {expected}, got {result}"


@pytest.mark.parametrize(
    "input_str",
    [
        "10minutes",
        "5 hours",
        "twoh",
        "1 dayy",
        "1 s",
        "-5m",
        "",
    ],
)
def test_convert_to_timedelta_invalid_formats_expect_error(reminder_cog, input_str):
    """Verify that invalid timer formats are rejected."""
    with pytest.raises(AttributeError):
        reminder_cog._convert_to_timedelta(input_str)


def test_valid_embed(reminder_cog):
    """Verify that embed is built correctly with valid input."""
    title = "Reminder"
    message = "Hello World"
    author = "Astra Al-Maarifa"

    with freeze_time("2025-02-20 12:00:01"):
        result = reminder_cog._build_embed(title, message, author)

        assert isinstance(result, Embed), f"Expected Embed, got {type(result)}"
        assert result.timestamp == datetime(2025, 2, 20, 12, 0, 1, tzinfo=tzlocal())
        assert result.title == f"**{title}**"
        assert result.description == message
        assert result.author.name == author

        assert result.thumbnail.url == "attachment://stopwatch.png"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "timer",
    ["0s", "10s", "5m", "2h", "1d", "10000d"],
)
async def test_reminder_valid_input(reminder_cog, timer):
    """Verify that reminder works with valid input."""
    with freeze_time("2025-02-20 12:00:01"):
        ctx = AsyncMock()
        ctx.author.display_name = "Astra Al-Maarifa"

        message = "Time for a break!"
        await reminder_cog.reminder.callback(
            reminder_cog,
            ctx,
            timer=timer,
            message=message,
        )

        ctx.send.assert_awaited_once()
        assert ctx.send.await_count == 1, "ctx.send should be awaited once"

        sent_Embed = ctx.send.call_args[1]["embed"]
        assert isinstance(sent_Embed, Embed), f"Expected Embed, got {type(sent_Embed)}"
        assert f"Reminder set for {timer} from now!" in sent_Embed.description
        assert "You will be reminded on" in sent_Embed.description
        assert sent_Embed.author.name == ctx.author.display_name

        reminder_cog.bot.scheduler.add_job.assert_called_once()
        _, kwargs = reminder_cog.bot.scheduler.add_job.call_args
        assert kwargs["args"][0] == ctx
        assert kwargs["args"][1] == message
        assert kwargs["id"].startswith(
            f"reminder_{ctx.author.id}_{datetime.now().timestamp()}"
        )
        assert kwargs["run_date"] >= datetime.now(tz=tzlocal())


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "timer",
    [
        "10seconds",
        "5minutes",
        "2hours",
        "1days",
        "-5m",
        "abc",
        "",
    ],
)
async def test_reminder_invalid_input(reminder_cog, timer):
    """Verify that reminder fails with invalid input."""
    ctx = AsyncMock()

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
    reminder_cog.bot.scheduler.add_job.assert_not_called()
