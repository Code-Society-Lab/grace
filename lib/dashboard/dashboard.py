import dachshund

from bot import app
from lib.dashboard.pages.activity import activity_page
from lib.dashboard.pages.overview import overview_page
from lib.dashboard.sqlmodel_storage import SQLModelStorage

DACHSHUND_EVENT_STORE = app.config.get("dachshund", "event_store", "dachshund.db")


def init_dachshund():
    """Stop any previous run and (re)open the dashboard's storage."""
    dachshund.shutdown()
    dachshund.default(path=DACHSHUND_EVENT_STORE, storage=SQLModelStorage())


def start_dashboard(context: dict):
    dachshund.init(
        "Grace",
        description="Code Society's Discord Bot",
        host="0.0.0.0",
        context=context
    )


def build_dashboard() -> None:
    for page in (overview_page, activity_page):
        dachshund.include(page)
