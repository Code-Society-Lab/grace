from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from dachshund.widgets import TableQuery
from discord.ext.commands import ExtensionAlreadyLoaded, ExtensionNotLoaded

from bot.classes.state import State
from lib.dashboard.handlers import extensions


def _extension(module, state=State.ENABLED):
    extension = MagicMock()
    extension.module_name = f"bot.extensions.{module}"
    extension.short_module_name = module
    extension.name = module.replace("_", " ").title()
    extension.state = state
    return extension


def _query(**kwargs):
    return TableQuery(**{"offset": 0, "limit": 10, **kwargs})


def _bot(*loaded):
    return SimpleNamespace(extensions={module: object() for module in loaded})


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "loader, state",
    [
        (extensions.load_enabled, State.ENABLED),
        (extensions.load_disabled, State.DISABLED),
    ],
)
@patch("lib.dashboard.handlers.extensions.Extension")
async def test_load__expect_that_state_only(model, loader, state):
    model.by_state.return_value.all.return_value = [_extension("pun_cog")]

    rows, total = await loader({"bot": _bot("bot.extensions.pun_cog")}, _query())

    model.by_state.assert_called_once_with(state)
    assert total == 1
    assert rows == [
        {
            "extension": "Pun Cog",
            "module": "pun_cog",
            "loaded": "yes",
            "_module_name": "bot.extensions.pun_cog",
        }
    ]


@pytest.mark.asyncio
@patch("lib.dashboard.handlers.extensions.Extension")
async def test_load__expect_buttons_get_the_full_module_name(model):
    """The hidden field reaches the actions without its underscore, so it must
    not collide with the shown `module` column."""
    from dachshund.widgets.table.table import _fields

    model.by_state.return_value.all.return_value = [_extension("pun_cog")]
    rows, _ = await extensions.load_enabled({"bot": _bot()}, _query())

    fields = _fields(rows[0])
    assert fields["module"] == "pun_cog"
    assert fields["module_name"] == "bot.extensions.pun_cog"


@pytest.mark.asyncio
@patch("lib.dashboard.handlers.extensions.Extension")
async def test_load__sorted_and_searched__expect_matching_rows(model):
    model.by_state.return_value.all.return_value = [
        _extension("pun_cog"),
        _extension("fun_cog"),
        _extension("time_cog"),
    ]

    rows, total = await extensions.load_enabled(
        {"bot": _bot()}, _query(search="UN", sort_by="extension")
    )

    assert total == 2
    assert [row["module"] for row in rows] == ["fun_cog", "pun_cog"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "action, bot_method, already, saved",
    [
        (extensions.enable, "load_extension", ExtensionAlreadyLoaded, "enable"),
        (extensions.disable, "unload_extension", ExtensionNotLoaded, "disable"),
    ],
)
@pytest.mark.parametrize("was_already", [False, True])
@patch("lib.dashboard.handlers.extensions.dachshund.emit")
@patch("lib.dashboard.handlers.extensions.Extension")
async def test_actions__expect_bot_updated_state_saved_and_table_refreshed(
    model, mock_emit, action, bot_method, already, saved, was_already
):
    extension = _extension("pun_cog")
    model.find_by.return_value = extension
    side_effect = already("bot.extensions.pun_cog") if was_already else None
    bot = MagicMock(**{bot_method: AsyncMock(side_effect=side_effect)})

    result = await action({"bot": bot}, module_name="bot.extensions.pun_cog")

    getattr(bot, bot_method).assert_awaited_once_with("bot.extensions.pun_cog")
    getattr(extension, saved).assert_called_once()
    mock_emit.assert_called_once_with("extensions")
    assert result == f"Pun Cog {saved}d."


@pytest.mark.asyncio
@pytest.mark.parametrize("action", [extensions.enable, extensions.disable])
@patch("lib.dashboard.handlers.extensions.Extension")
async def test_actions__with_unknown_module__expect_error(model, action):
    model.find_by.return_value = None

    with pytest.raises(ValueError, match="nope"):
        await action({"bot": MagicMock()}, module_name="nope")
