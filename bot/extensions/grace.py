from discord import Embed
from discord.ext.commands import Cog, command
from emoji import emojize
from bot import CONFIG


class GraceCog(Cog, name="Grace"):
    def __init__(self, bot):
        self.bot = bot

    @command(name='info', help='Show information about the bot', usage=f'{CONFIG.bot.prefix}info')
    async def info_command(self, ctx):
        embed = Embed(
            color=self.bot.default_color,
            title=f"My name is Grace",
            description=f"Hi, {ctx.author.mention}. I'm the official **Code Society** Discord Bot. ",
            inline=True
        )

        embed.add_field(
            name="Fun fact about me",
            value=f"I'm named after [Grace Hopper](https://en.wikipedia.org/wiki/Grace_Hopper) {emojize(':rabbit:')}",
            inline=True
        )

        embed.set_footer(text=f"Need help? Send {self.bot.command_prefix}help")

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(GraceCog(bot))
