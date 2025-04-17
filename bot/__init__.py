from grace.application import Application
from apscheduler.schedulers.asyncio import AsyncIOScheduler


def _create_bot(app, scheduler):
    """Factory to create the Grace bot instance.

    Import is deferred to avoid circular dependency.
    """
    from bot.grace import Grace
    return Grace(app, scheduler)


app = Application()
scheduler = AsyncIOScheduler()
bot = _create_bot(app, scheduler)
