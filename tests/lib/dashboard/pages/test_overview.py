from datetime import timedelta

import pytest
from dachshund import Column, Row
from dachshund.widgets import Number

from lib.dashboard.pages.overview import overview_page
from lib.dashboard.widgets.gauge import Gauge


def test_overview_page__expect_public():
    assert overview_page.public is True


def test_overview_page__expect_summary_then_latency_then_connections():
    assert overview_page.rows == [
        Row([Column(["summary"]), Column(["member_count"], 4)]),
        Row(
            [
                Column(
                    ["average_latency_gauge", "avg_response_time", "worst_latency"], 4
                ),
                Column(["latency"]),
            ]
        ),
        Row([Column(["connection_event"])]),
    ]


@pytest.mark.parametrize(
    "name, source, y, aggregate",
    [
        ("avg_response_time", "command_duration", "value", "average"),
        ("worst_latency", "latency", "check", "max"),
    ],
)
def test_overview_page__expect_24h_response_numbers_in_ms(name, source, y, aggregate):
    number = overview_page.widgets[name]

    assert isinstance(number, Number)
    assert (number.source, number.y, number.aggregate) == (source, y, aggregate)
    assert number.over == timedelta(hours=24)
    assert number.unit == "ms"


def test_overview_page__with_average_latency_gauge__expect_gauge_widget_in_ms():
    gauge = overview_page.widgets["average_latency_gauge"]

    assert isinstance(gauge, Gauge)
    assert gauge.source == "average_latency"
    assert gauge.unit == "ms"
