from dachshund.widgets import TableQuery

from lib.dashboard.context import DashboardContext
from lib.dashboard.handlers.paging import Page, page_rows

COLUMNS = ["job", "trigger", "next run"]


async def load(ctx: DashboardContext, query: TableQuery) -> Page:
    """The scheduler's jobs, like pending reminders and recurring thread posts."""
    rows = [
        {
            "job": job.name,
            "trigger": str(job.trigger),
            "next run": (
                job.next_run_time.astimezone(ctx.bot.timezone).strftime(
                    "%Y-%m-%d %H:%M"
                )
                if job.next_run_time
                else "paused"
            ),
        }
        for job in ctx.bot.scheduler.get_jobs()
    ]

    return page_rows(rows, query, COLUMNS)
