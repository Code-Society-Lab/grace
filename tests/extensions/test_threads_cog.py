import pytest

from bot.extensions.threads_cog import ThreadsCog
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_bot():
    """Create a mock Discord bot instance."""
    bot = MagicMock()
    bot.default_color = 0xFFFFFF
    bot.app.config.get = MagicMock(return_value=None)
    bot.scheduler = MagicMock()
    return bot


@pytest.fixture
def threads_cog(mock_bot):
    """Instantiate the ThreadsCog with a mock bot."""

    return ThreadsCog(mock_bot)


@pytest.fixture
def dummy_modal(monkeypatch):
    """Fixture that patches ThreadModal and records constructor args."""
    called_args = {}

    class DummyModal:
        def __init__(self, recurrence, reminder=None, thread=None):
            called_args["recurrence"] = recurrence
            called_args["reminder"] = reminder
            called_args["thread"] = thread

    monkeypatch.setattr("bot.extensions.threads_cog.ThreadModal", DummyModal)

    return called_args


@pytest.mark.asyncio
async def test_create_thread_modal_called(threads_cog):
    """Verify that thread modal is called."""
    ctx = MagicMock()
    ctx.interaction = MagicMock()
    ctx.interaction.response = MagicMock()
    ctx.interaction.response.send_modal = AsyncMock()

    recurrence = "DAILY"
    reminder = True
    await threads_cog.create.callback(
        threads_cog,
        ctx,
        recurrence=recurrence,
        reminder=reminder,
    )

    ctx.interaction.response.send_modal.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_modal_args(threads_cog, dummy_modal):
    ctx = MagicMock()
    ctx.interaction = MagicMock()
    ctx.interaction.response = MagicMock()
    ctx.interaction.response.send_modal = AsyncMock()

    recurrence = "DAILY"
    reminder = True

    await threads_cog.create.callback(
        threads_cog,
        ctx,
        recurrence=recurrence,
        reminder=reminder,
    )

    ctx.interaction.response.send_modal.assert_awaited_once()
    assert dummy_modal["recurrence"] == recurrence
    assert dummy_modal["reminder"] == reminder
    assert dummy_modal["thread"] is None


@pytest.mark.asyncio
async def test_daily_reminder_no_threads(threads_cog, mock_bot):
    """Test daily_reminder when there are no threads."""
    with patch("bot.extensions.threads_cog.Thread.all", return_value=[]):
        mock_channel = MagicMock()
        mock_bot.get_channel.return_value = mock_channel

        await threads_cog.daily_reminder()
        mock_channel.send.assert_not_called()


@pytest.mark.asyncio
async def test_daily_reminder_with_active_threads(threads_cog, mock_bot):
    """Test daily_reminder sends reminders for active threads."""
    thread1 = MagicMock()
    thread1.latest_thread = 123
    thread1.daily_reminder = True
    thread1.title = "Thread 1"
    thread1.content = "Content 1"

    thread2 = MagicMock()
    thread2.latest_thread = 456
    thread2.daily_reminder = False  # Should not be included

    # discord_thread is not archived or locked
    discord_thread = MagicMock()
    discord_thread.archived = False
    discord_thread.locked = False

    with patch(
        "bot.extensions.threads_cog.Thread.all",
        return_value=[thread1, thread2]
    ):
        mock_bot.fetch_channel = AsyncMock(return_value=discord_thread)
        mock_channel = MagicMock()
        mock_channel.send = AsyncMock()
        mock_bot.get_channel.return_value = mock_channel

        await threads_cog.daily_reminder()

        mock_channel.send.assert_awaited_once()
        args, kwargs = mock_channel.send.await_args
        embed = kwargs.get("embed")
        assert embed is not None
        assert "Daily Reminder" in embed.title

        assert len(embed.fields) == 1
        assert embed.fields[0].value == f"- <#{thread1.latest_thread}>"
        assert any(
            thread2.latest_thread != field.value
            for field in embed.fields
        )


@pytest.mark.asyncio
async def test_daily_reminder_skips_archived_and_locked(threads_cog, mock_bot):
    """Test daily_reminder skips archived and locked threads."""
    thread = MagicMock()
    thread.latest_thread = 789
    thread.daily_reminder = True

    discord_thread = MagicMock()
    discord_thread.archived = True
    discord_thread.locked = True

    with patch("bot.extensions.threads_cog.Thread.all", return_value=[thread]):
        mock_bot.fetch_channel = AsyncMock(return_value=discord_thread)
        mock_channel = MagicMock()
        mock_bot.get_channel.return_value = mock_channel

        await threads_cog.daily_reminder()
        mock_channel.send.assert_not_called()
