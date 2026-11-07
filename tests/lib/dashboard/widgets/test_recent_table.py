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


def test_persist__expect_error():
    with pytest.raises(ValueError, match="keep"):
        RecentTable("errors", columns=["n"], persist=True, key="n")


def test_keep__below_one__expect_error():
    with pytest.raises(ValueError, match="keep"):
        RecentTable("errors", columns=["n"], keep=0)
