from datetime import datetime
from types import SimpleNamespace

import pytest
from dachshund.widgets import TableQuery

from lib.dashboard.handlers.jobs import load


def _query(**kwargs):
    return TableQuery(**{"offset": 0, "limit": 10, **kwargs})


def _job(name, next_run_time, trigger="interval[0:01:00]"):
    return SimpleNamespace(name=name, trigger=trigger, next_run_time=next_run_time)


@pytest.mark.asyncio
async def test_load__expect_jobs_with_next_run_in_eastern_time():
    from pytz import UTC

    jobs = [
        _job("reminder", UTC.localize(datetime(2026, 11, 7, 15, 30))),
        _job("paused", None),
    ]
    bot = SimpleNamespace(scheduler=SimpleNamespace(get_jobs=lambda: jobs))

    rows, total = await load({"bot": bot}, _query())

    assert total == 2
    assert rows == [
        {
            "job": "reminder",
            "trigger": "interval[0:01:00]",
            "next run": "2026-11-07 10:30",
        },
        {"job": "paused", "trigger": "interval[0:01:00]", "next run": "paused"},
    ]


@pytest.mark.asyncio
async def test_load__sorted_and_paged__expect_that_page_and_the_total():
    jobs = [_job(name, None) for name in ("c", "a", "b")]
    bot = SimpleNamespace(scheduler=SimpleNamespace(get_jobs=lambda: jobs))

    rows, total = await load(
        {"bot": bot}, _query(sort_by="job", descending=True, offset=1, limit=1)
    )

    assert total == 3
    assert [row["job"] for row in rows] == ["b"]
