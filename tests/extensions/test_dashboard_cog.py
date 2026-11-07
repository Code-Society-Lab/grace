from unittest.mock import patch

import pytest
from freezegun import freeze_time

from bot.extensions.dashboard_cog import SUMMARY, DashboardCog


def _fake_message(author_id=1, bot=False):
    author = type("Author", (), {"id": author_id, "bot": bot})()
    return type("Message", (), {"author": author})()


@pytest.fixture
def dashboard_cog(mock_bot):
    """Instantiate the DashboardCog with a mock bot."""
    mock_bot.latency_ms = 50
    return DashboardCog(mock_bot)


def test_report_latency__expect_records_latency_from_bot(dashboard_cog):
    """Verify _report_latency hands the bot's latency reading to the metrics recorder."""
    dashboard_cog._report_latency()

    dashboard_cog.bot.metrics.record_latency.assert_called_once_with(50)


@patch("bot.extensions.dashboard_cog.dachshund.emit")
def test_report_member_count__expect_emits_member_count_for_configured_guild(
    mock_emit, dashboard_cog
):
    """Verify _report_member_count emits the member count for the configured guild."""
    guild = type("Guild", (), {"member_count": 15})()
    dashboard_cog.bot.get_guild = lambda guild_id: guild

    dashboard_cog._report_member_count()

    mock_emit.assert_called_once_with("member_count", value=15)


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_ready__expect_reports_member_count(mock_emit, dashboard_cog):
    """Verify on_ready reports the current member count."""
    guild = type("Guild", (), {"member_count": 7})()
    dashboard_cog.bot.get_guild = lambda guild_id: guild

    await dashboard_cog.on_ready()

    mock_emit.assert_any_call("member_count", value=7)


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_ready__expect_a_members_refresh_ping(mock_emit, dashboard_cog):
    """Verify on_ready pings the members table to refetch its loader."""
    await dashboard_cog.on_ready()

    mock_emit.assert_any_call("members")


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_member_join__expect_reports_member_count(mock_emit, dashboard_cog):
    """Verify on_member_join reports the current member count."""
    guild = type("Guild", (), {"member_count": 8})()
    dashboard_cog.bot.get_guild = lambda guild_id: guild

    await dashboard_cog.on_member_join(object())

    mock_emit.assert_any_call("member_count", value=8)


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_member_join__expect_a_members_refresh_ping(mock_emit, dashboard_cog):
    """Verify on_member_join pings the members table to refetch its loader."""
    await dashboard_cog.on_member_join(object())

    mock_emit.assert_any_call("members")


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_member_remove__expect_reports_member_count(mock_emit, dashboard_cog):
    """Verify on_member_remove reports the current member count."""
    guild = type("Guild", (), {"member_count": 6})()
    dashboard_cog.bot.get_guild = lambda guild_id: guild

    await dashboard_cog.on_member_remove(object())

    mock_emit.assert_any_call("member_count", value=6)


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_member_remove__expect_a_members_refresh_ping(
    mock_emit, dashboard_cog
):
    """Verify on_member_remove pings the members table to refetch its loader."""
    await dashboard_cog.on_member_remove(object())

    mock_emit.assert_any_call("members")


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_message__expect_one_message_event_with_date_and_author(
    mock_emit, dashboard_cog
):
    """Verify on_message emits one event per message, dated in the cog's timezone."""
    with freeze_time("2025-02-21 03:00:00"):  # still the 20th in US/Eastern
        await dashboard_cog.on_message(_fake_message(author_id=7))

    mock_emit.assert_called_once_with("message", date="2025-02-20", author="7", value=1)


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_message__from_a_bot__expect_no_author(mock_emit, dashboard_cog):
    """Verify a bot's message still counts, but not toward active members."""
    with freeze_time("2025-02-20 12:00:00"):
        await dashboard_cog.on_message(_fake_message(author_id=99, bot=True))

    mock_emit.assert_called_once_with(
        "message", date="2025-02-20", author=None, value=1
    )


def _command_ctx():
    command = type("Cmd", (), {"qualified_name": "ping"})()

    return type("Ctx", (), {"command": command})()


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_command__expect_emits_command_name(mock_emit, dashboard_cog):
    """Verify on_command emits the qualified command name."""
    ctx = _command_ctx()

    await dashboard_cog.on_command(ctx)

    mock_emit.assert_any_call("on_command", name="ping", value=1)


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_command_error__expect_emits_command_name(mock_emit, dashboard_cog):
    """Verify on_command_error emits the qualified command name."""
    ctx = _command_ctx()

    await dashboard_cog.on_command_error(ctx, Exception("boom"))

    mock_emit.assert_called_once_with("command_error", name="ping", value=1)


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_command_error__without_a_command__expect_emits_unknown(
    mock_emit, dashboard_cog
):
    """Verify on_command_error falls back to 'unknown' when ctx.command is missing."""
    ctx = type("Ctx", (), {"command": None})()

    await dashboard_cog.on_command_error(ctx, Exception("boom"))

    mock_emit.assert_called_once_with("command_error", name="unknown", value=1)


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_disconnect__expect_emits_disconnect_event(mock_emit, dashboard_cog):
    """Verify on_disconnect emits a connection_event of type disconnect."""
    await dashboard_cog.on_disconnect()

    mock_emit.assert_called_once_with("connection_event", type="disconnect", value=1)


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_resumed__expect_emits_resume_event(mock_emit, dashboard_cog):
    """Verify on_resumed emits a connection_event of type resume."""
    await dashboard_cog.on_resumed()

    mock_emit.assert_called_once_with("connection_event", type="resume", value=1)


def test_cog_load__expect_schedules_the_latency_job(dashboard_cog):
    """Verify cog_load schedules the latency report every minute."""
    dashboard_cog.cog_load()

    dashboard_cog.bot.scheduler.add_job.assert_called_once_with(
        dashboard_cog._report_latency, "interval", minutes=1
    )
    assert len(dashboard_cog.jobs) == 1


@patch("bot.extensions.dashboard_cog.dachshund.emit")
def test_cog_load__expect_emits_the_summary(mock_emit, dashboard_cog):
    """Verify cog_load emits the summary text."""
    dashboard_cog.cog_load()

    mock_emit.assert_called_once_with("summary", value=SUMMARY)


def test_cog_unload__expect_removes_scheduled_jobs(dashboard_cog):
    """Verify cog_unload removes every job scheduled by cog_load."""
    dashboard_cog.cog_load()
    jobs = list(dashboard_cog.jobs)

    dashboard_cog.cog_unload()

    for job in jobs:
        dashboard_cog.bot.scheduler.remove_job.assert_any_call(job.id)
