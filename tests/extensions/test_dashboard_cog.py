from unittest.mock import patch

import pytest
from freezegun import freeze_time

from bot.extensions.dashboard_cog import DashboardCog
from bot.models.extensions.widget_state import WidgetState


@pytest.fixture
def dashboard_cog(mock_bot):
    """Instantiate the DashboardCog with a mock bot."""
    mock_bot.latency_ms = 50
    return DashboardCog(mock_bot)


def test_report_latency__expect_records_latency_from_bot(dashboard_cog):
    """Verify _report_latency hands the bot's latency reading to the metrics recorder."""
    dashboard_cog._report_latency()

    dashboard_cog.bot.metrics.record_latency.assert_called_once_with(50)


def test_reset_daily_count__expect_resets_daily_message_count(dashboard_cog):
    """Verify _reset_daily_count resets the daily message counter."""
    dashboard_cog._daily_message_count = 42

    dashboard_cog._reset_daily_count()

    assert dashboard_cog._daily_message_count == 0


def test_reset_daily_count__expect_persists_zeroed_count(dashboard_cog):
    """Verify _reset_daily_count saves the zeroed count so it survives a restart."""
    dashboard_cog._daily_message_count = 42

    dashboard_cog._reset_daily_count()

    assert WidgetState.find("daily_message_rate").value == "0"


@patch("bot.extensions.dashboard_cog.dachshund.emit")
def test_report_member_count__expect_emits_summed_member_count(
    mock_emit, dashboard_cog
):
    """Verify _report_member_count sums member_count across every guild."""
    dashboard_cog.bot.guilds = [
        type("Guild", (), {"member_count": 10})(),
        type("Guild", (), {"member_count": 5})(),
    ]

    dashboard_cog._report_member_count()

    mock_emit.assert_called_once_with("member_count", value=15)


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_ready__expect_reports_member_count(mock_emit, dashboard_cog):
    """Verify on_ready reports the current member count."""
    dashboard_cog.bot.guilds = [type("Guild", (), {"member_count": 7})()]

    await dashboard_cog.on_ready()

    mock_emit.assert_called_once_with("member_count", value=7)


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_member_join__expect_reports_member_count(mock_emit, dashboard_cog):
    """Verify on_member_join reports the current member count."""
    dashboard_cog.bot.guilds = [type("Guild", (), {"member_count": 8})()]

    await dashboard_cog.on_member_join(object())

    mock_emit.assert_called_once_with("member_count", value=8)


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_member_remove__expect_reports_member_count(mock_emit, dashboard_cog):
    """Verify on_member_remove reports the current member count."""
    dashboard_cog.bot.guilds = [type("Guild", (), {"member_count": 6})()]

    await dashboard_cog.on_member_remove(object())

    mock_emit.assert_called_once_with("member_count", value=6)


@pytest.mark.asyncio
async def test_on_message__expect_increments_minutely_and_daily_counts(dashboard_cog):
    """Verify on_message counts the message toward both the minute and day totals."""
    await dashboard_cog.on_message(object())

    assert dashboard_cog._minutely_message_count == 1
    assert dashboard_cog._daily_message_count == 1


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_message__expect_emits_running_minutely_and_daily_counts(
    mock_emit, dashboard_cog
):
    """Verify on_message emits the running minute and day counts."""
    await dashboard_cog.on_message(object())
    await dashboard_cog.on_message(object())

    mock_emit.assert_any_call("minutely_message_rate", value=2)
    mock_emit.assert_any_call("daily_message_rate", value=2)


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_message__expect_emits_a_same_day_delta_for_the_weekly_chart(
    mock_emit, dashboard_cog
):
    """Verify on_message emits a delta of 1 for today's date, not a running total."""
    with freeze_time("2025-02-20 12:00:00"):
        await dashboard_cog.on_message(object())
        await dashboard_cog.on_message(object())

    mock_emit.assert_any_call("weekly_message_counts", date="2025-02-20", value=1)


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_command__expect_emits_command_name(mock_emit, dashboard_cog):
    """Verify on_command emits the qualified command name."""
    ctx = type("Ctx", (), {"command": type("Cmd", (), {"qualified_name": "ping"})()})()

    await dashboard_cog.on_command(ctx)

    mock_emit.assert_any_call("on_command", name="ping", value=1)


@pytest.mark.asyncio
async def test_on_command__expect_increments_minutely_command_count(dashboard_cog):
    """Verify on_command counts the command in addition to emitting."""
    ctx = type("Ctx", (), {"command": type("Cmd", (), {"qualified_name": "ping"})()})()

    await dashboard_cog.on_command(ctx)

    assert dashboard_cog._minutely_command_count == 1


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_command__expect_emits_running_command_count(mock_emit, dashboard_cog):
    """Verify on_command emits the running count for the current minute."""
    ctx = type("Ctx", (), {"command": type("Cmd", (), {"qualified_name": "ping"})()})()

    await dashboard_cog.on_command(ctx)
    await dashboard_cog.on_command(ctx)

    mock_emit.assert_any_call("minutely_command_rate", value=2)


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_command_error__expect_emits_command_name(mock_emit, dashboard_cog):
    """Verify on_command_error emits the qualified command name."""
    ctx = type("Ctx", (), {"command": type("Cmd", (), {"qualified_name": "ping"})()})()

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


def test_load_count__with_no_saved_value__expect_defaults_to_zero(dashboard_cog):
    """Verify _load_count returns 0 for a key that was never saved."""
    assert dashboard_cog._load_count("a_key_nobody_saved") == 0


def test_load_counts__with_saved_values__expect_rehydrates_counts(dashboard_cog):
    """Verify _load_counts restores counters from previously saved values."""
    dashboard_cog._daily_message_count = 42
    dashboard_cog._minutely_message_count = 7
    dashboard_cog._minutely_command_count = 3
    dashboard_cog._save_counts()

    fresh_cog = DashboardCog(dashboard_cog.bot)
    fresh_cog._load_counts()

    assert fresh_cog._daily_message_count == 42
    assert fresh_cog._minutely_message_count == 7
    assert fresh_cog._minutely_command_count == 3


@patch("bot.extensions.dashboard_cog.dachshund.emit")
def test_load_counts__expect_emits_restored_counts(mock_emit, dashboard_cog):
    """Verify _load_counts emits the restored counts so widgets update immediately."""
    dashboard_cog._daily_message_count = 5
    dashboard_cog._minutely_message_count = 2
    dashboard_cog._minutely_command_count = 1
    dashboard_cog._save_counts()

    dashboard_cog._load_counts()

    mock_emit.assert_any_call("daily_message_rate", value=5)
    mock_emit.assert_any_call("minutely_message_rate", value=2)
    mock_emit.assert_any_call("minutely_command_rate", value=1)


def test_cog_load__expect_schedules_cron_jobs(dashboard_cog):
    """Verify cog_load schedules latency, count-persistence, and day-reset jobs, pinned to the cog's timezone."""
    dashboard_cog.cog_load()

    dashboard_cog.bot.scheduler.add_job.assert_any_call(
        dashboard_cog._report_latency,
        "cron",
        minute="*/1",
        timezone=dashboard_cog.timezone,
    )
    dashboard_cog.bot.scheduler.add_job.assert_any_call(
        dashboard_cog._save_counts,
        "cron",
        minute="*/1",
        timezone=dashboard_cog.timezone,
    )
    dashboard_cog.bot.scheduler.add_job.assert_any_call(
        dashboard_cog._reset_daily_count,
        "cron",
        hour=0,
        minute=0,
        second=0,
        timezone=dashboard_cog.timezone,
    )
    assert len(dashboard_cog.jobs) == 3


def test_cog_unload__expect_removes_scheduled_jobs(dashboard_cog):
    """Verify cog_unload removes every job scheduled by cog_load."""
    dashboard_cog.cog_load()
    jobs = list(dashboard_cog.jobs)

    dashboard_cog.cog_unload()

    for job in jobs:
        dashboard_cog.bot.scheduler.remove_job.assert_any_call(job.id)
