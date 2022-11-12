from discord.ext.commands import Cog, hybrid_command
from googletrans import Translator
import googletrans
from discord import Embed


class TranslatorCog(Cog, name="Translator", description="Translate sentances in any languages."):
    def __init__(self, bot):
        self.bot = bot

    @hybrid_command(name='language_code', help='Languages Codes for Grace\'s Translator', usage="lang={your_language}")
    async def available_languages(self, ctx, *, lang):
        languages_available = googletrans.LANGCODES
        embed = Embed(
                    color=self.bot.default_color,
                )

        if lang in languages_available:
            embed.add_field(
                    name="Languages Code",
                    value=f"Language code for {lang.capitalize()} is -> {languages_available[lang]}",
                    inline=False
            )

        else:
            embed.add_field(
                    name="Languages Code",
                    value="No Found!",
                    inline=False
            )
        await ctx.send(embed=embed)

    @staticmethod
    def language_code(language):
        """Check if the input language code exist in the API database"""

        languages_available = googletrans.LANGCODES
        for languages in languages_available:
            if language == languages_available[languages]:
                return True
        return False

    @hybrid_command(name='translator', help='Translate a sentence/word in any languages. Enter /language_code to see your language code', \
                                        usage="language={language_code} sentence={sentence}")
    async def translator(self, ctx, *, language, sentence):
        """Translate to any languages any user inputed sentence or word"""

        is_available = self.language_code(language)
        embed = Embed(
                    color=self.bot.default_color
                )
        if is_available:
            text_translator = Translator()
            translated_text = text_translator.translate(sentence, dest=language)

            embed.add_field(
                    name="Original",
                    value=sentence,
                    inline=False
            )
            embed.add_field(
                    name="Translated",
                    value=translated_text.text,
                    inline=False
            )

        else:
            embed.add_field(
                    name="Error",
                    value="Wrong Language Code!",
                    inline=False
            )
        
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(TranslatorCog(bot))
