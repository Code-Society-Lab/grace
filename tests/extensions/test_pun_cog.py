from datetime import datetime
from discord import Embed
from unittest.mock import AsyncMock, MagicMock, patch, call
from bot.models.extensions.language.pun import PunWord, Pun

import pytest

from bot.extensions.pun_cog import PunCog


@pytest.fixture
def pun_cog(mock_bot):
    """Instantiate the PunCog with a mock bot."""
    return PunCog(mock_bot)


@pytest.mark.asyncio
@patch("bot.extensions.pun_cog.PunCog.pun_react", new_callable=AsyncMock)
async def test_on_message_with_message__expect_pun_react_call_with_same_message(
    mock_pun_react, pun_cog
):
    message = MagicMock()

    await pun_cog.on_message(message)

    mock_pun_react.assert_awaited_once_with(message)


@pytest.mark.asyncio
async def test_pun_react_with_bot_message__expect_message_not_tokenized_and_ignored(
    pun_cog,
):
    message = MagicMock()
    message.author = pun_cog.bot.user

    mock_tokenizer = MagicMock()
    pun_cog.tokenizer = mock_tokenizer

    await pun_cog.pun_react(message)

    mock_tokenizer.tokenize.assert_not_called()


@pytest.mark.asyncio
async def test_pun_react_with_no_pun__expect_message_tokenized_and_ignored(pun_cog):
    message = MagicMock()
    message.author = MagicMock()
    message.content = "text"
    message.add_reaction = AsyncMock()
    message.channel.send = AsyncMock()

    mock_tokenizer = MagicMock()
    mock_tokenizer.tokenize.return_value = ["text"]
    pun_cog.tokenizer = mock_tokenizer

    await pun_cog.pun_react(message)

    mock_tokenizer.tokenize.assert_called_once_with("text")
    message.add_reaction.assert_not_awaited()
    message.channel.send.assert_not_awaited()


@pytest.mark.asyncio
async def test_pun_react_with_pun__expect_reaction_and_reply(mock_bot, pun_cog):
    message = MagicMock()
    message.author = MagicMock()
    message.content = "text"
    message.add_reaction = AsyncMock()
    message.channel.send = AsyncMock()

    now = datetime.now(mock_bot.timezone)

    message.created_at.astimezone.return_value = now

    pun = Pun.create(text="texture")
    PunWord.create(word="text", pun=pun, emoji_code=1)

    mock_tokenizer = MagicMock()
    mock_tokenizer.tokenize.return_value = ["text"]
    pun_cog.tokenizer = mock_tokenizer

    await pun_cog.pun_react(message)

    mock_tokenizer.tokenize.assert_called_once_with("text")

    message.add_reaction.assert_awaited_once_with("1")

    embed = message.channel.send.call_args.kwargs["embed"]
    assert embed.color.value == mock_bot.default_color
    assert embed.title == "Gotcha"
    assert embed.description == "texture"

    message.created_at.astimezone.assert_called_once_with(pun_cog.bot.timezone)
