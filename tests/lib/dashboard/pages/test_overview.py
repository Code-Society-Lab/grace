from datetime import timedelta

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
                Column(["average_latency_gauge", "worst_latency"], 4),
                Column(["latency"]),
            ]
        ),
        Row([Column(["connection_event"])]),
    ]


def test_overview_page__with_worst_latency__expect_max_check_over_24h_in_ms():
    number = overview_page.widgets["worst_latency"]

    assert isinstance(number, Number)
    assert (number.source, number.y, number.aggregate) == ("latency", "check", "max")
    assert number.over == timedelta(hours=24)
    assert number.unit == "ms"


def test_overview_page__with_average_latency_gauge__expect_gauge_widget_in_ms():
    gauge = overview_page.widgets["average_latency_gauge"]

    assert isinstance(gauge, Gauge)
    assert gauge.source == "average_latency"
    assert gauge.unit == "ms"
