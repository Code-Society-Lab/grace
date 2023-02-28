from discord.ext.commands import Cog, hybrid_command
from googletrans import Translator, LANGUAGES as language_code
from discord import Embed, Interaction
from discord.app_commands import Choice, autocomplete


def get_languages_available() -> list:
    """Return a list of all available language names, sorted in alphabetical order.

    :return: A list of language names.
    :rtype: list
    """
    return [language_code[lang] for lang in language_code]


class TranslatorCog(Cog, name="Translator", description="Translate a sentence/word from any languages into any languages."):
    def __init__(self, bot):
        self.bot = bot

    async def language_autocomplete(self, _: Interaction, current: str) -> list[Choice[str]]:
        """Provide autocomplete suggestions for language names.

        :param _: The interaction object.
        :type _: Interaction
        :param current: The current value of the input field.
        :type current: str
        :return: A list of `Choice` objects containing language names.
        :rtype: list[Choice[str]]
        """
        LANGUAGES = get_languages_available()

        return [
            Choice(name=lang.capitalize(), value=lang.capitalize())
            for lang in LANGUAGES[:25] if current.lower() in lang.lower()
        ]

    @hybrid_command(
        name='translator',
        help='Translate a sentence/word from any languages into any languages',
        usage="sentence={sentence}"
        )
    @autocomplete(translate_into=language_autocomplete)
    async def translator(self, ctx, *, sentence: str, translate_into: str):
        """Translate a sentence or word from any language into any languages.

        :param ctx: The context object.
        :type ctx: Context
        :param sentence: The sentence or word to be translated.
        :type sentence: str
        :param translate_into: The language code for the target language.
        :type translate_into: str
        :return: Embed with original input and its translation
        """
        if ctx.interaction:
            await ctx.interaction.response.defer()

        text_translator = Translator()
        translated_text = text_translator.translate(sentence, dest=translate_into)

        embed = Embed(color=self.bot.default_color)

        embed.add_field(
            name=f"{language_code[translated_text.src].capitalize()} Original",
            value=sentence.capitalize(),
            inline=False
        )
        embed.add_field(
            name=f"{translate_into} Translation",
            value=translated_text.text,
            inline=False
        )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(TranslatorCog(bot))
