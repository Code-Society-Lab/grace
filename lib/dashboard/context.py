from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.grace import Grace


@dataclass(frozen=True)
class DashboardContext:
    """Passed as `ctx` to the dashboard's table loaders and actions."""

    bot: "Grace"
