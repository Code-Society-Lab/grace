import pytest
from dachshund import BarChart, Number, Row

from lib.dashboard.pages.activity import activity_page


def test_activity_page__expect_messages_beside_their_rate_then_one_chart_per_row():
    assert activity_page.rows == [
        Row(["daily_message_rate", "weekly_message_counts"], (1, 2)),
        Row(["on_command"]),
        Row(["command_error"]),
    ]
    assert isinstance(activity_page.widgets["daily_message_rate"], Number)


@pytest.mark.parametrize(
    "name, x",
    [
        ("weekly_message_counts", "date"),
        ("on_command", "name"),
        ("command_error", "name"),
    ],
)
def test_activity_page__expect_persisted_bar_charts(name, x):
    chart = activity_page.widgets[name]

    assert isinstance(chart, BarChart)
    assert chart.x == x
    assert chart.persist is True
