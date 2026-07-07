from unittest.mock import AsyncMock, MagicMock

import pytest
from discord import Embed
from discord.app_commands import Choice

from bot.extensions.translator_cog import TranslatorCog, language_autocomplete


@pytest.fixture
def translator_cog(mock_bot):
    """Instantiate the TranslatorCog with a mock bot."""

    return TranslatorCog(mock_bot)


@pytest.mark.asyncio
async def test_translator(translator_cog, mock_bot):
    ctx = MagicMock()
    ctx.defer = AsyncMock()
    ctx.send = AsyncMock()

    translate_from = "English"
    translate_into = "Arabic"
    sentence = "Funny"
    translated_text = "مضحك"

    await translator_cog.translator(
        translator_cog,
        ctx,
        sentence="Funny",
        translate_from="English",
        translate_into="Arabic",
    )

    result = Embed(color=mock_bot.default_color)

    result.add_field(
        name=f"{translate_from} Original",
        value=sentence,
        inline=False,
    )
    result.add_field(
        name=f"{translate_into} Translation",
        value=translated_text,
        inline=False,
    )

    ctx.send.assert_awaited_once_with(embed=result)


@pytest.mark.asyncio
async def test_language_autocomplete_empty_input():
    empty = await language_autocomplete(None, "")
    assert len(empty) == 25


@pytest.mark.asyncio
async def test_language_autocomplete_invalid_input():
    invalid = await language_autocomplete(None, "1232")
    assert invalid == []


@pytest.mark.asyncio
async def test_language_autocomplete_ara_input():
    ara = await language_autocomplete(None, "ara")
    assert ara == [
        Choice(name="Arabic", value="arabic"),
        Choice(name="Gujarati", value="gujarati"),
        Choice(name="Marathi", value="marathi"),
    ]


@pytest.mark.asyncio
async def test_language_autocomplete_zu_input():
    zu = await language_autocomplete(None, "zu")
    assert zu == [Choice(name="Zulu", value="zulu")]
