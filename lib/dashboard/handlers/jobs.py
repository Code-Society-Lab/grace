from dachshund.widgets import TableQuery

from lib.dashboard.handlers.paging import Page, page_rows

COLUMNS = ["job", "trigger", "next run"]


async def load(ctx: dict, query: TableQuery) -> Page:
    """The scheduler's jobs, like pending reminders and recurring thread posts."""
    bot = ctx["bot"]
    rows = [
        {
            "job": job.name,
            "trigger": str(job.trigger),
            "next run": (
                job.next_run_time.astimezone(bot.timezone).strftime("%Y-%m-%d %H:%M")
                if job.next_run_time
                else "paused"
            ),
        }
        for job in bot.scheduler.get_jobs()
    ]

    return page_rows(rows, query, COLUMNS)
