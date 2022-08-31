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
            description=f"Hi, {ctx.author.mention}. I'm the official **Code Society** Discord Bot.\n",
        )

        embed.add_field(
            name="Fun fact about me",
            value=f"I'm named after [Grace Hopper](https://en.wikipedia.org/wiki/Grace_Hopper) {emojize(':rabbit:')}",
            inline=False
        )

        embed.add_field(
            name=f"{emojize(':test_tube:')} Code Society Lab",
            value=f"Contribute to our [projects](https://github.com/Code-Society-Lab/grace)\n",
            inline=True
        )

        embed.add_field(
            name=f"{emojize(':crossed_swords:')} Codewars",
            value=f"Set your clan to **CodeSoc**\n",
            inline=True
        )

        embed.add_field(
            name="Need help?",
            value=f"Send '{ctx.prefix}help'",
            inline=False
        )

        await ctx.send(embed=embed)

    @command(name='ping', help='shows the bot latency')
    async def ping_command(self, ctx):
        embed = Embed(
            color=self.bot.default_color,
            description=f"pong :ping_pong:  {round(self.bot.latency * 1000)}ms",
        )

        await ctx.send(embed=embed)

    @command(name='hopper', help='The legend of Grace Hopper')
    async def hopper_command(self, ctx):
        await ctx.send("https://www.smbc-comics.com/?id=2516")


async def setup(bot):
    await bot.add_cog(GraceCog(bot))
