from discord import Embed, Color
from discord.ext.commands import Cog, command
from bot import CONFIG
from bot.helpers.color_helper import get_color_digit


class GraceCog(Cog, name="Grace"):
    def __init__(self, bot):
        self.bot = bot

    @command(name='info', help='Show information about the bot', usage=f'{CONFIG.bot.prefix}info')
    async def info_command(self, ctx):
        embed = Embed(
            color=self.bot.default_color,
            title=f"My name is Grace.",
            description=f"Hi, {ctx.author.mention}. I'm the official Code Society Discord Bot."
        )

        embed.set_footer(text=f"Need help? Send {self.bot.command_prefix}help")

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(GraceCog(bot))
