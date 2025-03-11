from config.application import Application
from apscheduler.schedulers.asyncio import AsyncIOScheduler


app = Application()
scheduler = AsyncIOScheduler()
