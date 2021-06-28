from discord.ext.commands import Cog, command
from discord import Embed
from json import loads
from requests import get

class Quote(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='quote', help='sends a inspirational quote', usage='quote')
    async def quote_command(self, ctx):
        response = get('http://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=en')
        quote = '{quoteText} \n-- {quoteAuthor}'.format(**loads(response.text))
        embed = Embed(
            color=self.bot.default_color,
            description=quote,
        )
        await ctx.send(embed=embed);


def setup(bot):
    bot.add_cog(Quote(bot))
