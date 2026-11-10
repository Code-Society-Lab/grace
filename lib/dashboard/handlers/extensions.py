"""The extension tables and the actions moving an extension between them.

Async, so they run on the bot's loop, like the database queries of its cogs.
"""

from typing import Any

import dachshund
from dachshund.widgets import TableQuery
from discord.ext.commands import ExtensionAlreadyLoaded, ExtensionNotLoaded

from bot.classes.state import State
from bot.models.extension import Extension
from lib.dashboard.context import DashboardContext
from lib.dashboard.handlers.paging import Page, page_rows

COLUMNS = ["extension", "module", "loaded"]

# Both tables watch this source, so either action refreshes them.
SOURCE = "extensions"


def _rows(bot: Any, state: State) -> list[dict[str, Any]]:
    loaded = bot.extensions

    return [
        {
            "extension": extension.name,
            "module": extension.short_module_name,
            "loaded": "yes" if extension.module_name in loaded else "no",
            # Reaches the actions as `module_name`.
            "_module_name": extension.module_name,
        }
        for extension in Extension.by_state(state).all()
    ]


async def load_enabled(ctx: DashboardContext, query: TableQuery) -> Page:
    """The enabled extensions, with whether each is actually loaded."""
    return page_rows(_rows(ctx.bot, State.ENABLED), query, COLUMNS)


async def load_disabled(ctx: DashboardContext, query: TableQuery) -> Page:
    """The disabled extensions, with whether each is actually loaded."""
    return page_rows(_rows(ctx.bot, State.DISABLED), query, COLUMNS)


def _extension(module_name: str) -> Extension:
    extension = Extension.find_by(module_name=module_name)

    if extension is None:
        raise ValueError(f"No extension {module_name!r}.")

    return extension


async def enable(ctx: DashboardContext, module_name: str) -> str:
    """Load an extension and keep it enabled across restarts."""
    extension = _extension(module_name)

    try:
        await ctx.bot.load_extension(extension.module_name)
    except ExtensionAlreadyLoaded:
        pass

    extension.enable()
    dachshund.emit(SOURCE)

    return f"{extension.name} enabled."


async def disable(ctx: DashboardContext, module_name: str) -> str:
    """Unload an extension and keep it disabled across restarts."""
    extension = _extension(module_name)

    try:
        await ctx.bot.unload_extension(extension.module_name)
    except ExtensionNotLoaded:
        pass

    extension.disable()
    dachshund.emit(SOURCE)

    return f"{extension.name} disabled."
