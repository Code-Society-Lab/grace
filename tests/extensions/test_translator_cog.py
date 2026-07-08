from unittest.mock import AsyncMock, MagicMock

import pytest
from discord import Embed
from discord.app_commands import Choice
from discord.ext.commands import CommandInvokeError

from bot.extensions.translator_cog import TranslatorCog, language_autocomplete


@pytest.fixture
def translator_cog(mock_bot):
    """Instantiate the TranslatorCog with a mock bot."""

    return TranslatorCog(mock_bot)


@pytest.mark.asyncio
async def test_translator__expect_translation_with_embed(translator_cog, mock_bot):
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
async def test_translator__with_invalid_input__expect_error(translator_cog):
    ctx = MagicMock()
    ctx.defer = AsyncMock()
    ctx.send = AsyncMock()

    with pytest.raises(ValueError):
        await translator_cog.translator(
            translator_cog,
            ctx,
            sentence="Funny",
            translate_from="1234",
            translate_into="1234",
        )

    ctx.send.assert_not_called()


@pytest.mark.asyncio
async def test_translator_error_handler__expect_error(translator_cog):
    ctx = MagicMock()
    ctx.defer = AsyncMock()
    ctx.send = AsyncMock()

    error = CommandInvokeError(ValueError("Error"))

    await translator_cog.translator_error(ctx, error)

    ctx.send.assert_called_once_with(
        "Please enter a valid language code.", ephemeral=True
    )


@pytest.mark.asyncio
async def test_language_autocomplete__with_no_input__expect_first_25_languages():
    empty = await language_autocomplete(None, "")
    assert len(empty) == 25


@pytest.mark.asyncio
async def test_language_autocomplete__with_invalid_input__expect_empty_list():
    invalid = await language_autocomplete(None, "1232")
    assert invalid == []


@pytest.mark.asyncio
async def test_language_autocomplete__with_partial_input__expect_matching_output():
    ara = await language_autocomplete(None, "ara")
    zu = await language_autocomplete(None, "zu")

    assert ara == [
        Choice(name="Arabic", value="arabic"),
        Choice(name="Gujarati", value="gujarati"),
        Choice(name="Marathi", value="marathi"),
    ]
    assert zu == [Choice(name="Zulu", value="zulu")]


@pytest.mark.asyncio
async def test_language_autocomplete__with_partial_input__expect_last_language():
    zu = await language_autocomplete(None, "zu")

    assert zu == [Choice(name="Zulu", value="zulu")]
