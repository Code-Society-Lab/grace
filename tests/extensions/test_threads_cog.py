import pytest

from bot.extensions.threads_cog import ThreadsCog
from unittest.mock import AsyncMock, MagicMock
from bot.models.extensions.thread import Thread


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
    _ = Thread.create(
        title="Thread 1",
        content="Content 1",
        recurrence=None,
        daily_reminder=False,  # Should not be included
        latest_thread_id=123,
    )

    mock_channel = MagicMock()
    mock_channel.send = AsyncMock()
    mock_bot.get_channel.return_value = mock_channel
    await threads_cog.daily_reminder()
    mock_channel.send.assert_not_called()


@pytest.mark.asyncio
async def test_daily_reminder_with_active_threads(threads_cog, mock_bot):
    """Test daily_reminder sends reminders for active threads."""
    thread1 = Thread.create(
        title="Thread 1",
        content="Content 1",
        recurrence=None,
        daily_reminder=True,
        latest_thread_id=123,
    )

    thread2 = Thread.create(
        title="Thread 2",
        content="Content 2",
        recurrence=None,
        daily_reminder=False,  # Should not be included
        latest_thread_id=456,
    )

    discord_thread = MagicMock()
    discord_thread.archived = False
    discord_thread.locked = False

    mock_channel = MagicMock()
    mock_channel.send = AsyncMock()

    mock_bot.get_channel.return_value = mock_channel
    mock_bot.fetch_channel = AsyncMock(return_value=discord_thread)

    await threads_cog.daily_reminder()
    mock_channel.send.assert_awaited_once()

    args, kwargs = mock_channel.send.await_args
    embed = kwargs.get("embed")
    assert embed is not None

    assert "Daily Reminder" in embed.title
    assert len(embed.fields) == 1
    assert embed.fields[0].value == f"- <#{thread1.latest_thread_id}>"
    assert any(thread2.latest_thread_id != field.value for field in embed.fields)


@pytest.mark.asyncio
async def test_daily_reminder_skips_archived_and_locked(threads_cog, mock_bot):
    """Test daily_reminder skips archived and locked threads."""
    discord_thread = MagicMock()
    discord_thread.archived = True
    discord_thread.locked = True

    mock_channel = MagicMock()
    mock_channel.send = AsyncMock()
    mock_bot.get_channel.return_value = mock_channel
    mock_bot.fetch_channel = AsyncMock(return_value=discord_thread)

    await threads_cog.daily_reminder()
    mock_channel.send.assert_not_called()


@pytest.mark.asyncio
async def test_post_thread(threads_cog, mock_bot):
    """Test post_thread creates a thread in the specified channel."""
    thread = Thread.create(
        title="Test Thread",
        content="This is a test thread.",
        recurrence=None,
        daily_reminder=False,
        latest_thread_id=None,
    )

    mock_channel = MagicMock()
    mock_channel.send = AsyncMock()
    mock_bot.get_channel.return_value = mock_channel

    message_mock = MagicMock()
    message_mock.create_thread = AsyncMock()
    mock_channel.send.return_value = message_mock

    await threads_cog.post_thread(thread)

    mock_channel.send.assert_awaited_once()
    args, kwargs = mock_channel.send.await_args
    embed = kwargs.get("embed")
    assert embed is not None
    assert embed.title == thread.title
    assert embed.description == thread.content

    message_mock.create_thread.assert_awaited_once_with(name=thread.title)


@pytest.mark.asyncio
async def test_cog_unload_removes_jobs(threads_cog, mock_bot):
    """Test that cog_unload removes scheduled jobs."""
    job1 = MagicMock()
    job2 = MagicMock()
    threads_cog.jobs = [job1, job2]

    threads_cog.cog_unload()

    mock_bot.scheduler.remove_job.assert_any_call(job1.id)
    mock_bot.scheduler.remove_job.assert_any_call(job2.id)
    assert mock_bot.scheduler.remove_job.call_count == 2
