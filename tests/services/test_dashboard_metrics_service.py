from unittest.mock import AsyncMock, patch

import pytest
from dachshund.storage.events import Event

from bot.services.dashboard_metrics_service import DashboardMetrics


@patch("bot.services.dashboard_metrics_service.dachshund.emit")
def test_record_latency__expect_emits_latency(mock_emit):
    """Verify record_latency always emits a latency event."""
    DashboardMetrics().record_latency(50)

    mock_emit.assert_any_call("latency", check=50, command=None)


@patch("bot.services.dashboard_metrics_service.dachshund.emit")
def test_record_latency__with_is_from_command__expect_emits_command_latency(mock_emit):
    """Verify record_latency tags the command latency when triggered by a command."""
    DashboardMetrics().record_latency(50, is_from_command=True)

    mock_emit.assert_any_call("latency", check=50, command=50)


@patch("bot.services.dashboard_metrics_service.dachshund.emit")
def test_record_latency__expect_emits_average_latency(mock_emit):
    """Verify record_latency always emits an average_latency event."""
    DashboardMetrics().record_latency(50)

    mock_emit.assert_any_call("average_latency", value=50)


@patch("bot.services.dashboard_metrics_service.dachshund.emit")
def test_record_latency__with_new_max__expect_emits_highest_latency(mock_emit):
    """Verify highest_latency is emitted when a new maximum is reached."""
    DashboardMetrics().record_latency(50)

    assert mock_emit.call_args_list[-1].args[0] == "highest_latency"


@patch("bot.services.dashboard_metrics_service.dachshund.emit")
def test_record_latency__with_lower_latency__expect_no_highest_latency_emit(mock_emit):
    """Verify highest_latency is not re-emitted when latency stays below the max."""
    metrics = DashboardMetrics()
    metrics.record_latency(50)
    mock_emit.reset_mock()

    metrics.record_latency(20)

    names = [call.args[0] for call in mock_emit.call_args_list]
    assert "highest_latency" not in names
    assert metrics.lowest_latency_ms == 20


@patch("bot.services.dashboard_metrics_service.dachshund.emit")
def test_record_latency__with_higher_latency__expect_no_lowest_latency_emit(mock_emit):
    """Verify lowest_latency is not re-emitted when latency stays above the min."""
    metrics = DashboardMetrics()
    metrics.record_latency(50)
    mock_emit.reset_mock()

    metrics.record_latency(80)

    names = [call.args[0] for call in mock_emit.call_args_list]
    assert "lowest_latency" not in names
    assert metrics.highest_latency_ms == 80


@patch("bot.services.dashboard_metrics_service.dachshund.emit")
def test_record_latency__expect_average_eases_toward_new_value(mock_emit):
    """Verify average_latency_ms moves by EMA_ALPHA * delta, not straight to the new value."""
    metrics = DashboardMetrics()
    metrics.record_latency(50)

    metrics.record_latency(150)

    assert metrics.average_latency_ms == 50 + 0.2 * (150 - 50)


@pytest.mark.asyncio
async def test_load__with_no_history__expect_defaults():
    """Verify load starts from defaults when dachshund has no latency history."""
    with patch(
        "bot.services.dashboard_metrics_service.dachshund.default"
    ) as mock_default:
        mock_default.return_value.events.events = AsyncMock(return_value=[])

        metrics = await DashboardMetrics.load()

    assert metrics == DashboardMetrics()


@pytest.mark.asyncio
async def test_load__expect_stats_replayed_from_kept_events():
    """Verify load rebuilds highest/lowest/average from dachshund's own kept history."""
    events = [
        Event("latency", {"check": 50}),
        Event("latency", {"check": 150}),
        Event("latency", {"check": 20}),
    ]

    with patch(
        "bot.services.dashboard_metrics_service.dachshund.default"
    ) as mock_default:
        mock_default.return_value.events.events = AsyncMock(return_value=events)

        metrics = await DashboardMetrics.load()

    assert metrics.highest_latency_ms == 150
    assert metrics.lowest_latency_ms == 20
    # seed 50 -> +0.2*(150-50) = 70 -> +0.2*(20-70) = 60
    assert metrics.average_latency_ms == 60


@pytest.mark.asyncio
async def test_load__with_an_event_missing_check__expect_it_skipped():
    """Verify load ignores latency events that don't carry a check field."""
    events = [Event("latency", {"command": 30})]

    with patch(
        "bot.services.dashboard_metrics_service.dachshund.default"
    ) as mock_default:
        mock_default.return_value.events.events = AsyncMock(return_value=events)

        metrics = await DashboardMetrics.load()

    assert metrics == DashboardMetrics()
