from discord.ext.commands import Cog, hybrid_command
from googletrans import Translator
import googletrans
from discord import Embed


class TranslatorCog(Cog, name="Translator", description="Translate sentances in any languages."):
    def __init__(self, bot):
        self.bot = bot

    @hybrid_command(name='translator', help='Translate a sentence/word in any languages. Enter /language_code to see your language code', \
                                        usage="language={language_code} sentence={sentence}")
    async def translator(self, ctx, *, sentence):
        """Translate to any languages any user inputed sentence or word"""
        
        text_translator = Translator()
        translated_text = text_translator.translate(sentence, dest='en')
        
        embed = Embed(
                    color=self.bot.default_color
                )

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
