import pytest
from dachshund import Column, Row
from dachshund.widgets import BarChart, Number

from lib.dashboard.pages.activity import activity_page


def test_activity_page__expect_public():
    assert activity_page.public is True


def test_activity_page__expect_counts_then_messages_then_commands():
    assert activity_page.rows == [
        Row(
            [
                Column(["member_count"]),
                Column(["active_members"]),
                Column(["daily_message_rate"]),
            ]
        ),
        Row([Column(["weekly_message_counts"])]),
        Row([Column(["on_command"])]),
    ]


@pytest.mark.parametrize(
    "name, x",
    [
        ("weekly_message_counts", "date"),
        ("on_command", "name"),
    ],
)
def test_activity_page__expect_persisted_bar_charts(name, x):
    chart = activity_page.widgets[name]

    assert isinstance(chart, BarChart)
    assert chart.x == x
    assert chart.persist is True


@pytest.mark.parametrize(
    "name, y, aggregate",
    [
        ("daily_message_rate", "value", "count"),
        ("active_members", "author", "distinct"),
    ],
)
def test_activity_page__expect_todays_message_numbers_aggregated_from_messages(
    name, y, aggregate
):
    number = activity_page.widgets[name]

    assert isinstance(number, Number)
    assert number.source == "message"
    assert number.y == y
    assert number.aggregate == aggregate
    assert number.over == "day"


def test_activity_page__expect_messages_per_day_fed_by_messages():
    assert activity_page.widgets["weekly_message_counts"].source == "message"
