from json import loads
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import Cog, command, cooldown
from discord import Embed
from requests import get
import random
from bot.models.extensions.fun.eightball.answer import Answer


class FunCog(Cog, name="Fun", description="Collection of fun commands"):
    def __init__(self, bot):
        self.bot = bot

    @command(name='eightball', aliases=['8ball'], help="Ask a question and be answered.", usage="{question}")
    @cooldown(4, 30, BucketType.user)
    async def eightball(self, ctx, *args):
        if args:
            answer = random.choice(Answer.all())
        else:
            answer = "You need to ask me a question!"

        answer_embed = Embed(
            title=f'{ctx.author.name}, Grace says: ',
            Color=self.bot.default_color,
            description=answer.answer,
        )

        await ctx.send(embed=answer_embed)

    @command(name='quote', help='Sends an inspirational quote')
    async def quote_command(self, ctx):
        response = get(
            'https://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=en')
        quote = '{quoteText} \n-- {quoteAuthor}'.format(**loads(response.text))

        embed = Embed(
            color=self.bot.default_color,
            description=quote,
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(FunCog(bot))
