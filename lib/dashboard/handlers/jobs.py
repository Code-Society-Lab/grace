from dachshund.widgets import TableQuery
from pytz import timezone

from lib.dashboard.handlers.paging import Page, page_rows

COLUMNS = ["job", "trigger", "next run"]
TIMEZONE = timezone("US/Eastern")


async def load(ctx: dict, query: TableQuery) -> Page:
    """The scheduler's jobs, like pending reminders and recurring thread posts."""
    rows = [
        {
            "job": job.name,
            "trigger": str(job.trigger),
            "next run": (
                job.next_run_time.astimezone(TIMEZONE).strftime("%Y-%m-%d %H:%M")
                if job.next_run_time
                else "paused"
            ),
        }
        for job in ctx["bot"].scheduler.get_jobs()
    ]

    return page_rows(rows, query, COLUMNS)
