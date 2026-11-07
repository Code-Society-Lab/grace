from datetime import timedelta

import pytest
from dachshund import Column, Row
from dachshund.widgets import BarChart, Number, TimeSeriesChart

from lib.dashboard.widgets.top_bar_chart import TopBarChart

from lib.dashboard.pages.activity import activity_page


def test_activity_page__expect_public():
    assert activity_page.public is True


def test_activity_page__expect_counts_then_members_then_messages_then_commands():
    assert activity_page.rows == [
        Row(
            [
                Column(["active_members"]),
                Column(["daily_message_rate"]),
                Column(["commands_24h"]),
                Column(["recent_joins"]),
            ]
        ),
        Row([Column(["member_flow"])]),
        Row([Column(["weekly_message_counts"]), Column(["channel_messages"])]),
        Row([Column(["commands_per_day"]), Column(["on_command"])]),
        Row([Column(["reactions_per_day"]), Column(["reaction_emojis"])]),
    ]


@pytest.mark.parametrize(
    "name, x",
    [
        ("weekly_message_counts", "date"),
        ("channel_messages", "channel"),
        ("on_command", "name"),
        ("commands_per_day", "date"),
        ("reactions_per_day", "date"),
        ("reaction_emojis", "emoji"),
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


def test_activity_page__with_recent_joins__expect_joins_summed_over_an_hour():
    number = activity_page.widgets["recent_joins"]

    assert isinstance(number, Number)
    assert number.source == "member_flow"
    assert number.y == "joined"
    assert number.aggregate == "sum"
    assert number.over == timedelta(hours=1)


def test_activity_page__with_member_flow__expect_daily_joins_and_leaves():
    chart = activity_page.widgets["member_flow"]

    assert isinstance(chart, TimeSeriesChart)
    assert chart.y == ["joined", "left"]
    assert chart.aggregate == "sum"
    assert chart.every == timedelta(days=1)
    assert chart.over == timedelta(days=30)


def test_activity_page__expect_messages_per_channel_fed_by_messages():
    assert activity_page.widgets["channel_messages"].source == "message"


def test_activity_page__with_commands_24h__expect_commands_counted_over_a_day():
    number = activity_page.widgets["commands_24h"]

    assert isinstance(number, Number)
    assert number.source == "on_command"
    assert number.aggregate == "count"
    assert number.over == timedelta(hours=24)


def test_activity_page__with_top_emojis__expect_the_ten_most_used():
    chart = activity_page.widgets["reaction_emojis"]

    assert isinstance(chart, TopBarChart)
    assert chart.top == 10
