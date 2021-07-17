from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import Cog, command, cooldown
from discord import Embed
from bot import CONFIG
import random


class EightBall(Cog, description="Magic Eight Ball"):
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


def setup(bot):
    bot.add_cog(EightBall(bot))
