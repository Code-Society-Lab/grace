from unittest.mock import patch

import dachshund

from lib.dashboard.dashboard import build_dashboard


@patch.object(dachshund, "widget")
@patch.object(dachshund, "chart")
def test_build_dashboard__expect_all_charts_registered(mock_chart, mock_widget):
    """Verify build_dashboard registers every chart and widget exactly once."""
    build_dashboard()

    chart_names = [call.args[0] for call in mock_chart.call_args_list]
    widget_names = [call.args[0] for call in mock_widget.call_args_list]
    assert chart_names == [
        "latency",
        "weekly_message_counts",
        "on_command",
        "command_error",
        "connection_event",
    ]
    assert widget_names == ["average_latency_gauge", "daily_message_rate"]


@patch.object(dachshund, "widget")
@patch.object(dachshund, "chart")
def test_build_dashboard__with_on_command_chart__expect_bar_chart_by_name(
    mock_chart, mock_widget
):
    """Verify the on_command chart is configured as a bar chart keyed by command name."""
    build_dashboard()

    on_command_call = next(
        call for call in mock_chart.call_args_list if call.args[0] == "on_command"
    )
    assert on_command_call.kwargs["type"] == "bar"
    assert on_command_call.kwargs["x"] == "name"
    assert on_command_call.kwargs["persist"] is True


@patch.object(dachshund, "widget")
@patch.object(dachshund, "chart")
def test_build_dashboard__with_weekly_message_counts_chart__expect_bar_chart_by_date(
    mock_chart, mock_widget
):
    """Verify the weekly_message_counts chart is configured as a persisted bar chart keyed by date."""
    build_dashboard()

    weekly_call = next(
        call
        for call in mock_chart.call_args_list
        if call.args[0] == "weekly_message_counts"
    )
    assert weekly_call.kwargs["type"] == "bar"
    assert weekly_call.kwargs["x"] == "date"
    assert weekly_call.kwargs["persist"] is True


@patch.object(dachshund, "widget")
@patch.object(dachshund, "chart")
def test_build_dashboard__with_average_latency_gauge__expect_gauge_widget_in_ms(
    mock_chart, mock_widget
):
    """Verify the average_latency_gauge widget reads the average_latency source in ms."""
    build_dashboard()

    gauge_call = next(
        call
        for call in mock_widget.call_args_list
        if call.args[0] == "average_latency_gauge"
    )
    assert gauge_call.kwargs["type"] == "gauge"
    assert gauge_call.kwargs["source"] == "average_latency"
    assert gauge_call.kwargs["unit"] == "ms"


@patch.object(dachshund, "widget")
@patch.object(dachshund, "chart")
def test_build_dashboard__with_command_error_chart__expect_bar_chart_by_name(
    mock_chart, mock_widget
):
    """Verify the command_error chart is configured as a persisted bar chart keyed by command name."""
    build_dashboard()

    command_error_call = next(
        call for call in mock_chart.call_args_list if call.args[0] == "command_error"
    )
    assert command_error_call.kwargs["type"] == "bar"
    assert command_error_call.kwargs["x"] == "name"
    assert command_error_call.kwargs["persist"] is True


@patch.object(dachshund, "widget")
@patch.object(dachshund, "chart")
def test_build_dashboard__with_connection_event_chart__expect_bar_chart_by_type(
    mock_chart, mock_widget
):
    """Verify the connection_event chart is configured as a persisted bar chart keyed by event type."""
    build_dashboard()

    connection_event_call = next(
        call for call in mock_chart.call_args_list if call.args[0] == "connection_event"
    )
    assert connection_event_call.kwargs["type"] == "bar"
    assert connection_event_call.kwargs["x"] == "type"
    assert connection_event_call.kwargs["persist"] is True
