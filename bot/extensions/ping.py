from discord.ext.commands import Cog, command
from bot import CONFIG


class Ping(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='ping', help='Send pong', usage=f'{CONFIG.bot.prefix}pong')
    async def ping_command(self, ctx):
        await ctx.send(f"Pong! {round(self.bot.latency * 1000)}ms")

def setup(bot):
    bot.add_cog(Ping(bot))
