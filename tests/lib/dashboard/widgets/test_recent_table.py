from datetime import UTC, datetime

import pytest
from dachshund import Dashboard
from dachshund.runtime.ws import hydrate, updates
from dachshund.storage.events import Event

from lib.dashboard.widgets.recent_table import RecentTable


def _table(events, **options):
    table = RecentTable("errors", columns=["time", "n"], **options)

    for event in events:
        table.accumulate(event)

    return table


def _events(count):
    return [Event("errors", {"n": n}) for n in range(count)]


def _ns(table):
    return [row["fields"]["n"] for row in table.render([])["rows"]]


def test_render__expect_newest_first():
    assert _ns(_table(_events(3))) == [2, 1, 0]


def test_render__with_more_than_keep__expect_only_the_newest():
    assert _ns(_table(_events(5), keep=2)) == [4, 3]


def test_render__expect_each_row_stamped_with_its_event_time_in_timezone():
    events = [
        Event("errors", {"n": 0}, at=datetime(2025, 2, 21, 3, 0, tzinfo=UTC)),
        Event("errors", {"n": 1}, at=datetime(2025, 2, 21, 4, 30, tzinfo=UTC)),
    ]

    rows = _table(events, timezone="US/Eastern").render([])["rows"]

    assert [row["fields"] for row in rows] == [
        {"n": 1, "time": "2025-02-20 23:30:00"},
        {"n": 0, "time": "2025-02-20 22:00:00"},
    ]


def test_render__by_default__expect_utc():
    event = Event("errors", {"n": 0}, at=datetime(2025, 2, 21, 3, 0, tzinfo=UTC))

    rows = _table([event]).render([])["rows"]

    assert rows[0]["fields"]["time"] == "2025-02-21 03:00:00"


def test_render__on_a_dashboard__expect_its_timezone():
    event = Event("errors", {"n": 0}, at=datetime(2025, 2, 21, 3, 0, tzinfo=UTC))
    table = _table([event])
    table.bind(Dashboard(path=":memory:", timezone="US/Eastern"))

    rows = table.render([])["rows"]

    assert rows[0]["fields"]["time"] == "2025-02-20 22:00:00"


def test_render__with_timezone_on_a_dashboard__expect_its_own():
    event = Event("errors", {"n": 0}, at=datetime(2025, 2, 21, 3, 0, tzinfo=UTC))
    table = _table([event], timezone="UTC")
    table.bind(Dashboard(path=":memory:", timezone="US/Eastern"))

    rows = table.render([])["rows"]

    assert rows[0]["fields"]["time"] == "2025-02-21 03:00:00"


def test_persist__expect_always_on():
    assert RecentTable("errors", columns=["n"]).persist is True


def test_persist__expect_only_one_raw_event_kept():
    assert RecentTable("errors", columns=["n"], keep=50).raw_events() == 1


def test_restore__expect_same_rows_and_times():
    event = Event("errors", {"n": 0}, at=datetime(2025, 2, 21, 3, 0, tzinfo=UTC))

    restored = RecentTable("errors", columns=["time", "n"])
    restored.restore(_table([event]).snapshot())

    assert restored.render([])["rows"] == [
        {"fields": {"n": 0, "time": "2025-02-21 03:00:00"}}
    ]


def test_restore__with_snapshot_over_keep__expect_only_the_newest():
    restored = RecentTable("errors", columns=["n"], keep=2)
    restored.restore(_table(_events(5)).snapshot())

    assert _ns(restored) == [4, 3]


def test_key__expect_error():
    with pytest.raises(ValueError, match="no key"):
        RecentTable("errors", columns=["n"], key="n")


def test_keep__below_one__expect_error():
    with pytest.raises(ValueError, match="keep"):
        RecentTable("errors", columns=["n"], keep=0)


class _MemoryStorage:
    def __init__(self):
        self.saved = {}

    async def save(self, key, value):
        self.saved[key] = value

    async def load(self, key):
        return self.saved.get(key)


@pytest.mark.asyncio
async def test_through_a_dashboard__expect_rows_saved_and_restored():
    storage = _MemoryStorage()

    def dashboard():
        board = Dashboard(path=":memory:", storage=storage)
        with board.row():
            board.add(RecentTable("logins", columns=["user"]))
        return board

    await updates(dashboard(), [Event("logins", {"user": "ada"})])

    restarted = dashboard()
    await hydrate(restarted)

    rows = restarted.widgets["logins"].render([])["rows"]
    assert [row["fields"]["user"] for row in rows] == ["ada"]
