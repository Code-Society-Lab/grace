from grace.application import Application
from apscheduler.schedulers.asyncio import AsyncIOScheduler


try:
    from nltk.downloader import Downloader
    from nltk import download, download_shell

    download("vader_lexicon", quiet=True)
except ModuleNotFoundError:
    print("nltk module not properly installed")


def _create_bot(app):
    """Factory to create the Grace bot instance.

    Import is deferred to avoid circular dependency.
    """
    from bot.grace import Grace

    return Grace(app)


app = Application()
bot = _create_bot(app)
