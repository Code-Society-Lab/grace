from unittest.mock import patch

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

    assert mock_emit.call_count == 1
    assert mock_emit.call_args.args[0] == "latency"
