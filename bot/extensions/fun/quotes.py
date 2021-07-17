from discord.ext.commands import Cog, command
from discord import Embed
from json import loads
from requests import get
from bot import CONFIG


class Quote(Cog, description="Quotes API"):
    def __init__(self, bot):
        self.bot = bot

    @command(name='quote', help='Sends an inspirational quote', usage='::quote get')
    async def quote_command(self, ctx):
        response = get(CONFIG.extensions.quote.api_url)
        quote = '{quoteText} \n-- {quoteAuthor}'.format(**loads(response.text))

        embed = Embed(
            color=self.bot.default_color,
            description=quote,
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Quote(bot))
