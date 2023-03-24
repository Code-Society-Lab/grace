from discord.ext.commands import Cog, hybrid_command, Context, CommandError
from googletrans import Translator, LANGUAGES
from discord import Embed, Interaction
from discord.app_commands import Choice, autocomplete

from bot.helpers.error_helper import get_original_exception


async def language_autocomplete(_: Interaction, current: str) -> list[Choice[str]]:
    """Provide autocomplete suggestions for language names.

    :param _: The interaction object.
    :type _: Interaction
    :param current: The current value of the input field.
    :type current: str
    :return: A list of `Choice` objects containing language names.
    :rtype: list[Choice[str]]
    """
    languages = list(LANGUAGES.values())

    return [
        Choice(name=language.capitalize(), value=language)
        for language in languages[:25] if current.lower() in language.lower()
    ]


class TranslatorCog(
    Cog,
    name="Translator",
    description="Translate a sentence/word from any languages into any languages."
):
    @hybrid_command(
        name='translator',
        help='Translate a sentence/word from any languages into any languages',
        usage="sentence={sentence}"
    )
    @autocomplete(translate_into=language_autocomplete)
    async def translator(self, ctx: Context, *, sentence: str, translate_into: str):
        """Translate a sentence or word from any language into any languages.

        :param ctx: The context object.
        :type ctx: Context
        :param sentence: The sentence or word to be translated.
        :type sentence: str
        :param translate_into: The language code for the target language.
        :type translate_into: str
        :return: Embed with original input and its translation
        """
        await ctx.defer()

        text_translator = Translator()
        translated_text = text_translator.translate(sentence, dest=translate_into)

        embed = Embed(color=self.bot.default_color)

        embed.add_field(
            name=f"{LANGUAGES[translated_text.src].capitalize()} Original",
            value=sentence.capitalize(),
            inline=False
        )
        embed.add_field(
            name=f"{translate_into} Translation",
            value=translated_text.text,
            inline=False
        )

        await ctx.send(embed=embed)

    def __init__(self, bot):
        self.bot = bot

    @translator.error
    async def translator_error(self, ctx: Context, error: CommandError):
        """Error handler for the `translator` command.

        :param ctx: The context object.
        :type ctx: Context
        :param error: The error object.
        :type error: Exception
        :return: This function sends an embed message to the Discord channel
        """
        original_error = get_original_exception(error)

        if isinstance(original_error, ValueError):
            await ctx.send("Please enter a valid language code.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(TranslatorCog(bot))
