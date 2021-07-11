from discord.ext.commands import Cog, command
from discord import Embed


class Ping(Cog, description="Latency test"):
    def __init__(self, bot):
        self.bot = bot

    @command(name='ping', help='shows the bot latency', usage='ping')
    async def ping_command(self, ctx):
        embed = Embed(
            color=self.bot.default_color,
            description=f"pong :ping_pong:  {round(self.bot.latency * 1000)}ms",
        )
        await ctx.send(embed=embed);


def setup(bot):
    bot.add_cog(Ping(bot))
