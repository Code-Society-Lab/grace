import pytest
from dachshund.storage.events import Event

from lib.dashboard.widgets.gauge import Gauge


def test_gauge_type_and_op__expect_a_full_replace() -> None:
    assert (Gauge.type, Gauge.op) == ("gauge", "replace")


def test_gauge_script_and_style__expect_them_set() -> None:
    assert Gauge.script is not None and Gauge.script.is_file()
    assert Gauge.style is not None and Gauge.style.is_file()


def test_gauge_with_max_not_greater_than_min__expect_value_error() -> None:
    with pytest.raises(ValueError, match="max must be greater than its min"):
        Gauge("cpu", source="cpu", min=100, max=100)


def test_gauge_thresholds_default__expect_60_and_85_percent_of_range() -> None:
    widget = Gauge("cpu", source="cpu", min=0, max=100)

    assert widget.warning_at == 60
    assert widget.critical_at == 85


def test_gauge_thresholds_explicit__expect_them_respected() -> None:
    widget = Gauge("cpu", source="cpu", min=0, max=500, warning_at=150, critical_at=300)

    assert widget.warning_at == 150
    assert widget.critical_at == 300


def test_gauge_render_without_events__expect_no_value() -> None:
    widget = Gauge("cpu", source="cpu", min=0, max=100)

    assert widget.render([]) == {
        "value": None,
        "min": 0,
        "max": 100,
        "warning_at": 60,
        "critical_at": 85,
        "unit": None,
    }


def test_gauge_render__expect_the_latest_event_not_a_total() -> None:
    widget = Gauge("cpu", source="cpu", min=0, max=100)
    events = [Event("cpu", {"value": 20}), Event("cpu", {"value": 55})]

    assert widget.render(events)["value"] == 55.0


def test_gauge_render_with_an_unreadable_value__expect_no_value() -> None:
    widget = Gauge("cpu", source="cpu", min=0, max=100)

    assert widget.render([Event("cpu", {"value": "fast"})])["value"] is None


def test_gauge_render_with_a_unit__expect_it_carried_through() -> None:
    widget = Gauge("cpu", source="cpu", min=0, max=100, unit="%")

    assert widget.render([Event("cpu", {"value": 42})])["unit"] == "%"
