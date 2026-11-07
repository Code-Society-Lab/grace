from dachshund.storage.events import Event

from lib.dashboard.widgets.stat import Stat


def test_render__expect_the_newest_events_field_as_text():
    stat = Stat("python", source="deployment", y="python")
    events = [
        Event("deployment", {"python": "3.11.0"}),
        Event("deployment", {"python": "3.12.3"}),
    ]

    assert stat.render(events) == {"value": "3.12.3"}


def test_render__with_a_number__expect_text():
    assert Stat("count").render([Event("count", {"value": 7})]) == {"value": "7"}


def test_render__without_events_or_field__expect_none():
    stat = Stat("commit", source="deployment", y="commit")

    assert stat.render([]) == {"value": None}
    assert stat.render([Event("deployment", {"python": "3.12.3"})]) == {"value": None}
