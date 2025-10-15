from apscheduler.schedulers.asyncio import AsyncIOScheduler

from grace.application import Application

try:
    from nltk import download, download_shell
    from nltk.downloader import Downloader

    download("vader_lexicon", quiet=True)
except ModuleNotFoundError:
    print('nltk module not properly installed')


def _create_bot(app):
    """Factory to create the Grace bot instance.

    Import is deferred to avoid circular dependency.
    """
    from bot.grace import Grace

    return Grace(app)


app = Application()
bot = _create_bot(app)
