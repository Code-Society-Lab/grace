"""Rows for the dashboard's recent commands and moderation tables."""

from datetime import datetime

import dachshund
from pytz import timezone

TIMEZONE = timezone("US/Eastern")

MODERATION_SOURCE = "recent_moderation"


def today() -> str:
    """Today's date, the day starting at midnight Eastern."""
    return datetime.now(TIMEZONE).date().isoformat()


def timestamp() -> str:
    """Now, as the dashboard's tables show it."""
    return datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")


def record_moderation(
    action: str, *, member: str = "", by: str = "auto", details: str = ""
) -> None:
    """A row of the recent moderation table: `by` a moderator, or "auto" for Grace's own."""
    dachshund.emit(
        MODERATION_SOURCE,
        time=timestamp(),
        action=action,
        member=member,
        by=by,
        details=details,
    )
