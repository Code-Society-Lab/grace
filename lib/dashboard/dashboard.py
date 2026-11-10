import dachshund

from bot import app
from lib.dashboard.context import DashboardContext
from lib.dashboard.pages.activity import activity_page
from lib.dashboard.pages.admin import admin_page
from lib.dashboard.pages.overview import overview_page
from lib.dashboard.sqlmodel_storage import SQLModelStorage

DACHSHUND_EVENT_STORE = app.config.get("dachshund", "event_store", "dachshund.db")


def init_dachshund():
    """Stop any previous run and (re)open the dashboard's storage."""
    dachshund.shutdown()
    dachshund.default(path=DACHSHUND_EVENT_STORE, storage=SQLModelStorage())


def start_dashboard(context: DashboardContext, **access) -> None:
    """Start dachshund, with `access` (`host`, `port`, `authorize`, `login`) guarding its private pages."""
    dachshund.init(
        "Grace",
        description="Code Society's Discord Bot",
        timezone=context.bot.timezone.key,
        context=context,
        **access,
    )


def build_dashboard() -> None:
    for page in (overview_page, activity_page, admin_page):
        dachshund.include(page)
