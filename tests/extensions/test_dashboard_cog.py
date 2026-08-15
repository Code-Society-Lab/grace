from unittest.mock import patch

import pytest

from bot.extensions.dashboard_cog import DashboardCog


@pytest.fixture
def dashboard_cog(mock_bot):
    """Instantiate the DashboardCog with a mock bot."""
    mock_bot.latency_ms = 50
    return DashboardCog(mock_bot)


def test_report_latency__expect_records_latency_from_bot(dashboard_cog):
    """Verify _report_latency hands the bot's latency reading to the metrics recorder."""
    dashboard_cog._report_latency()

    dashboard_cog.bot.metrics.record_latency.assert_called_once_with(50)


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_message__expect_emits_on_message(mock_emit, dashboard_cog):
    """Verify on_message emits an on_message event."""
    await dashboard_cog.on_message(object())

    mock_emit.assert_called_once_with("on_message")


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_command__expect_emits_command_name(mock_emit, dashboard_cog):
    """Verify on_command emits the qualified command name."""
    ctx = type("Ctx", (), {"command": type("Cmd", (), {"qualified_name": "ping"})()})()

    await dashboard_cog.on_command(ctx)

    mock_emit.assert_called_once_with("on_command", name="ping", value=1)


def test_cog_load__expect_schedules_cron_job(dashboard_cog):
    """Verify cog_load schedules _report_latency to run every minute."""
    dashboard_cog.cog_load()

    dashboard_cog.bot.scheduler.add_job.assert_called_once_with(
        dashboard_cog._report_latency, "cron", minute="*/1"
    )
    assert len(dashboard_cog.jobs) == 1


def test_cog_unload__expect_removes_scheduled_jobs(dashboard_cog):
    """Verify cog_unload removes every job scheduled by cog_load."""
    dashboard_cog.cog_load()
    job = dashboard_cog.jobs[0]

    dashboard_cog.cog_unload()

    dashboard_cog.bot.scheduler.remove_job.assert_called_once_with(job.id)
