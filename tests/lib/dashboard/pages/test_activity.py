import pytest
from dachshund import BarChart, Number

from lib.dashboard.pages.activity import activity_page


def test_activity_page__expect_one_tab_per_topic():
    assert list(activity_page.tabs) == ["messages", "commands", "connections"]


@pytest.mark.parametrize(
    "tab, name, x",
    [
        ("messages", "weekly_message_counts", "date"),
        ("commands", "on_command", "name"),
        ("commands", "command_error", "name"),
        ("connections", "connection_event", "type"),
    ],
)
def test_activity_page__expect_persisted_bar_charts(tab, name, x):
    chart = activity_page.tabs[tab].widgets[name]

    assert isinstance(chart, BarChart)
    assert chart.x == x
    assert chart.persist is True


def test_activity_page__with_messages_tab__expect_rate_beside_counts():
    messages = activity_page.tabs["messages"]

    assert isinstance(messages.widgets["daily_message_rate"], Number)
    assert messages.rows == [["daily_message_rate", "weekly_message_counts"]]
