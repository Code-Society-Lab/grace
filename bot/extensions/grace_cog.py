from discord import Embed
from discord.ext.commands import Cog, command
from emoji import emojize


class GraceCog(Cog, name="Grace", description="Default grace commands"):
    def __init__(self, bot):
        self.bot = bot

    @command(name='info', help='Show information about the bot')
    async def info_command(self, ctx):
        embed = Embed(
            color=self.bot.default_color,
            title=f"My name is Grace",
            description=f"Hi, {ctx.author.mention}. I'm the official **Code Society** Discord Bot.\n\u200b",
        )

        embed.add_field(
            name="Fun fact about me",
            value=f"I'm named after [Grace Hopper](https://en.wikipedia.org/wiki/Grace_Hopper) {emojize(':rabbit:')}"
                  "\n\u200b",
            inline=False
        )

        embed.add_field(
            name=f"{emojize(':test_tube:')} Code Society Lab",
            value=f"Contribute to our [projects](https://github.com/Code-Society-Lab/grace)\n\u200b",
            inline=True
        )

        embed.add_field(
            name=f"{emojize(':crossed_swords:')} Codewars",
            value=f"Set your clan to **CodeSoc**\n\u200b",
            inline=True
        )

        embed.add_field(
            name="Need help?",
            value=f"Send '{ctx.prefix}help'",
            inline=False
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(GraceCog(bot))
