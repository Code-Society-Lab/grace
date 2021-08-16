from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import Cog, command, cooldown
from discord import Embed
from bot import CONFIG
import random


class Fun(Cog, description="Collection of fun commands"):
    def __init__(self, bot):
        self.bot = bot

    @command(name='eightball', aliases=['8ball'], usage='eightball or 8ball', help="Ask a question and be answered.")
    @cooldown(4, 30, BucketType.user)
    async def eightball(self, ctx, *args):
        if args:
            answer = random.choice(CONFIG.extensions.eight_ball.responses)
        else:
            answer = "You need to ask me a question!"

        answer_embed = Embed(
            title=f'{ctx.author.name}, Grace says: ',
            Color=self.bot.default_color,
            description=answer,
        )

        await ctx.send(embed=answer_embed)

    @command(name='quote', help='Sends an inspirational quote', usage='::quote get')
    async def quote_command(self, ctx):
        response = get(CONFIG.extensions.quote.api_url)
        quote = '{quoteText} \n-- {quoteAuthor}'.format(**loads(response.text))

        embed = Embed(
            color=self.bot.default_color,
            description=quote,
        )

        await ctx.send(embed=embed)
