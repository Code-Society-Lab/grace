from discord.ext.commands import Cog, hybrid_command
from googletrans import Translator
from discord import Embed


class TranslatorCog(Cog, name="Translator", description="Translate sentences from any languages to English."):
    def __init__(self, bot):
        self.bot = bot

    @hybrid_command(name='translator', help='Translate a sentence/word from any languages to English',
                    usage="sentence={sentence}")
    async def translator(self, ctx, *, sentence):
        """Translate to English any user inputted sentence or word"""

        text_translator = Translator()
        translated_text = text_translator.translate(sentence, dest='en')

        embed = Embed(color=self.bot.default_color)

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

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(TranslatorCog(bot))
