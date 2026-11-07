import pytest
from dachshund.storage.events import Event

from lib.dashboard.widgets.recent_table import RecentTable


def _events(count):
    return [Event("errors", {"n": n}) for n in range(count)]


def test_render__expect_newest_first():
    table = RecentTable("errors", columns=["n"])

    rows = table.render(_events(3))["rows"]

    assert [row["fields"]["n"] for row in rows] == [2, 1, 0]


def test_render__with_more_than_keep__expect_only_the_newest():
    table = RecentTable("errors", columns=["n"], keep=2)

    rows = table.render(_events(5))["rows"]

    assert [row["fields"]["n"] for row in rows] == [4, 3]


def test_keep__expect_honoured_by_compaction():
    from dachshund import Dashboard
    from dachshund.runtime.ws import kept_raw

    dashboard = Dashboard(path=":memory:")
    with dashboard.row():
        dashboard.add(RecentTable("errors", columns=["n"], keep=50))

    assert kept_raw(dashboard)["errors"] == 50


def test_render__expect_each_row_stamped_with_its_event_time_in_timezone():
    from datetime import UTC, datetime

    table = RecentTable("errors", columns=["time", "n"], timezone="US/Eastern")
    events = [
        Event("errors", {"n": 0}, at=datetime(2025, 2, 21, 3, 0, tzinfo=UTC)),
        Event("errors", {"n": 1}, at=datetime(2025, 2, 21, 4, 30, tzinfo=UTC)),
    ]

    rows = table.render(events)["rows"]

    assert [row["fields"] for row in rows] == [
        {"n": 1, "time": "2025-02-20 23:30:00"},
        {"n": 0, "time": "2025-02-20 22:00:00"},
    ]


def test_render__by_default__expect_utc():
    from datetime import UTC, datetime

    event = Event("errors", {"n": 0}, at=datetime(2025, 2, 21, 3, 0, tzinfo=UTC))

    rows = RecentTable("errors", columns=["time"]).render([event])["rows"]

    assert rows[0]["fields"]["time"] == "2025-02-21 03:00:00"


def test_key__expect_error():
    with pytest.raises(ValueError, match="no key"):
        RecentTable("errors", columns=["n"], key="n")


def test_persist__expect_error():
    with pytest.raises(ValueError, match="keep"):
        RecentTable("errors", columns=["n"], persist=True, key="n")


def test_keep__below_one__expect_error():
    with pytest.raises(ValueError, match="keep"):
        RecentTable("errors", columns=["n"], keep=0)
