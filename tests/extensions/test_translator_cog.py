from unittest.mock import AsyncMock, MagicMock, patch
from types import SimpleNamespace

import pytest
from discord import Embed
from discord.app_commands import Choice
from discord.ext.commands import CommandInvokeError

from bot.extensions.translator_cog import TranslatorCog, language_autocomplete


@pytest.fixture
def translator_cog(mock_bot):
    """Instantiate the TranslatorCog with a mock bot."""

    return TranslatorCog(mock_bot)


@pytest.fixture
def mock_ctx():
    """Create a mock command context."""
    ctx = MagicMock()
    ctx.defer = AsyncMock()
    ctx.send = AsyncMock()
    return ctx


@pytest.fixture
def embed_factory(mock_bot):
    def _make_embed(*, sentence, translate_from, translate_into, translated_text):
        embed = Embed(color=mock_bot.default_color)

        embed.add_field(
            name=f"{translate_from.capitalize()} Original",
            value=sentence,
            inline=False,
        )
        embed.add_field(
            name=f"{translate_into.capitalize()} Translation",
            value=translated_text,
            inline=False,
        )

        return embed

    return _make_embed


@pytest.mark.asyncio
@patch("bot.extensions.translator_cog.Translator")
async def test_translator__with_all_input__expect_translation_with_embed(
    mock_translator, translator_cog, mock_ctx, embed_factory
):
    instance = mock_translator.return_value
    instance.translate.return_value = SimpleNamespace(
        text="مضحك", src="en"
    )  # translated text

    await translator_cog.translator(
        translator_cog,
        mock_ctx,
        sentence="funny",
        translate_from="english",
        translate_into="arabic",
    )

    result = embed_factory(
        sentence="funny",
        translate_from="english",
        translate_into="arabic",
        translated_text="مضحك",
    )

    instance.translate.assert_called_once_with("funny", src="english", dest="arabic")
    mock_ctx.defer.assert_awaited_once()
    mock_ctx.send.assert_awaited_once_with(embed=result)


@pytest.mark.asyncio
@patch("bot.extensions.translator_cog.Translator")
async def test_translator__with_translate_into_input__expect_translation_with_embed(
    mock_translator, translator_cog, mock_ctx, embed_factory
):
    instance = mock_translator.return_value
    instance.translate.return_value = SimpleNamespace(text="مضحك", src="en")

    await translator_cog.translator(
        translator_cog,
        mock_ctx,
        sentence="funny",
        translate_into="arabic",
    )

    result = embed_factory(
        sentence="funny",
        translate_from="english",
        translate_into="arabic",
        translated_text="مضحك",
    )

    instance.translate.assert_called_once_with("funny", src="auto", dest="arabic")
    mock_ctx.defer.assert_awaited_once()
    mock_ctx.send.assert_awaited_once_with(embed=result)


@pytest.mark.asyncio
@patch("bot.extensions.translator_cog.Translator")
async def test_translator__with_translate_from_input__expect_translation_with_embed(
    mock_translator, translator_cog, mock_ctx, embed_factory
):
    instance = mock_translator.return_value
    instance.translate.return_value = SimpleNamespace(text="funny", src="ar")

    await translator_cog.translator(
        translator_cog,
        mock_ctx,
        sentence="مضحك",
        translate_from="arabic",
    )

    result = embed_factory(
        sentence="مضحك",
        translate_from="arabic",
        translate_into="english",
        translated_text="funny",
    )

    instance.translate.assert_called_once_with("مضحك", src="arabic", dest="english")
    mock_ctx.defer.assert_awaited_once()
    mock_ctx.send.assert_awaited_once_with(embed=result)


@pytest.mark.asyncio
@patch("bot.extensions.translator_cog.Translator")
async def test_translator__with_no_langugae_input__expect_translation_with_embed(
    mock_translator, translator_cog, mock_ctx, embed_factory
):
    instance = mock_translator.return_value
    instance.translate.return_value = SimpleNamespace(text="funny", src="ar")

    await translator_cog.translator(
        translator_cog,
        mock_ctx,
        sentence="مضحك",
    )

    result = embed_factory(
        sentence="مضحك",
        translate_from="arabic",
        translate_into="english",
        translated_text="funny",
    )

    instance.translate.assert_called_once_with("مضحك", src="auto", dest="english")
    mock_ctx.defer.assert_awaited_once()
    mock_ctx.send.assert_awaited_once_with(embed=result)


@pytest.mark.asyncio
@patch("bot.extensions.translator_cog.Translator")
async def test_translator__with_invalid_input__expect_error(
    mock_translator, translator_cog, mock_ctx
):
    instance = mock_translator.return_value
    instance.translate.side_effect = ValueError("invalid language code")

    with pytest.raises(ValueError, match="invalid language code"):
        await translator_cog.translator(
            translator_cog,
            mock_ctx,
            sentence="Funny",
            translate_from="1234",
            translate_into="1234",
        )

    mock_ctx.defer.assert_awaited_once()
    mock_ctx.send.assert_not_called()


@pytest.mark.asyncio
async def test_translator_error_handler__expect_error(translator_cog, mock_ctx):
    error = CommandInvokeError(ValueError("Error"))

    await translator_cog.translator_error(mock_ctx, error)

    mock_ctx.defer.assert_not_called()
    mock_ctx.send.assert_called_once_with(
        "Please enter a valid language code.", ephemeral=True
    )


@pytest.mark.asyncio
async def test_language_autocomplete__with_invalid_input__expect_empty_list():
    invalid = await language_autocomplete(None, "1232")
    assert invalid == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input_str",
    ["ara", "Ara", "ARA"],
)
async def test_language_autocomplete__with_partial_input__expect_matching_output(
    input_str,
):
    ara = await language_autocomplete(None, input_str)

    assert ara == [
        Choice(name="Arabic", value="arabic"),
        Choice(name="Gujarati", value="gujarati"),
        Choice(name="Marathi", value="marathi"),
    ]


@pytest.mark.asyncio
async def test_language_autocomplete__with_partial_input__expect_last_language():
    zu = await language_autocomplete(None, "zu")

    assert zu == [Choice(name="Zulu", value="zulu")]


@pytest.mark.asyncio
async def test_language_autocomplete__with_no_input__expect_first_25_languages():
    empty = await language_autocomplete(None, "")
    assert len(empty) == 25
    assert empty == [
        Choice(name="Afrikaans", value="afrikaans"),
        Choice(name="Albanian", value="albanian"),
        Choice(name="Amharic", value="amharic"),
        Choice(name="Arabic", value="arabic"),
        Choice(name="Armenian", value="armenian"),
        Choice(name="Azerbaijani", value="azerbaijani"),
        Choice(name="Basque", value="basque"),
        Choice(name="Belarusian", value="belarusian"),
        Choice(name="Bengali", value="bengali"),
        Choice(name="Bosnian", value="bosnian"),
        Choice(name="Bulgarian", value="bulgarian"),
        Choice(name="Catalan", value="catalan"),
        Choice(name="Cebuano", value="cebuano"),
        Choice(name="Chichewa", value="chichewa"),
        Choice(name="Chinese (simplified)", value="chinese (simplified)"),
        Choice(name="Chinese (traditional)", value="chinese (traditional)"),
        Choice(name="Corsican", value="corsican"),
        Choice(name="Croatian", value="croatian"),
        Choice(name="Czech", value="czech"),
        Choice(name="Danish", value="danish"),
        Choice(name="Dutch", value="dutch"),
        Choice(name="English", value="english"),
        Choice(name="Esperanto", value="esperanto"),
        Choice(name="Estonian", value="estonian"),
        Choice(name="Filipino", value="filipino"),
    ]
