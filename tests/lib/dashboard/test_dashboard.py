from unittest.mock import patch

import dachshund

from lib.dashboard.dashboard import build_dashboard


@patch.object(dachshund, "chart")
def test_build_dashboard__expect_all_charts_registered(mock_chart):
    """Verify build_dashboard registers every chart exactly once."""
    build_dashboard()

    names = [call.args[0] for call in mock_chart.call_args_list]
    assert names == ["latency", "highest_latency", "on_command"]


@patch.object(dachshund, "chart")
def test_build_dashboard__with_on_command_chart__expect_bar_chart_by_name(mock_chart):
    """Verify the on_command chart is configured as a bar chart keyed by command name."""
    build_dashboard()

    on_command_call = next(
        call for call in mock_chart.call_args_list if call.args[0] == "on_command"
    )
    assert on_command_call.kwargs["type"] == "bar"
    assert on_command_call.kwargs["x"] == "name"
    assert on_command_call.kwargs["persist"] is True
