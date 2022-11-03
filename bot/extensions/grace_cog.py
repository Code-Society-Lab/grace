from discord import Embed
from discord.ext.commands import Cog, hybrid_command
from discord.ui import Button, View
from emoji import emojize
from bot.services.github_service import GithubService
from lib.config_required import command_config_required
from lib.paged_embeds import PagedEmbedView


class GraceCog(Cog, name="Grace", description="Default grace commands"):
    __DEFAULT_INFO_BUTTONS = [
        Button(
            emoji=emojize(":globe_with_meridians:"),
            label="Website",
            url="https://codesociety.xyz"
        ),
        Button(
            emoji=emojize(":file_folder:"),
            label="Repository",
            url="https://github.com/Code-Society-Lab/grace"
        )
    ]

    def __init__(self, bot):
        self.bot = bot

    async def get_contributors_embed(self):
        grace_repo = GithubService().get_grace()

        embed = Embed(
            color=self.bot.default_color,
            title="Grace's contributors",
        )

        for contributor in grace_repo.get_contributors():
            embed.add_field(
                name=contributor.login,
                value=f"{contributor.contributions} contributions",
                inline=True
            )

        return embed

    @hybrid_command(name='info', help='Show information about the bot')
    async def info_command(self, ctx, ephemeral=True):
        contributors_embed = await self.get_contributors_embed()

        info_embed = Embed(
            color=self.bot.default_color,
            title=f"My name is Grace",
            description=f"Hi, {ctx.author.mention}. I'm the official **Code Society** Discord Bot.\n",
        )

        info_embed.add_field(
            name="Fun fact about me",
            value=f"I'm named after [Grace Hopper](https://en.wikipedia.org/wiki/Grace_Hopper) {emojize(':rabbit:')}",
            inline=False
        )

        info_embed.add_field(
            name=f"{emojize(':test_tube:')} Code Society Lab",
            value=f"Contribute to our [projects](https://github.com/Code-Society-Lab/grace)\n",
            inline=True
        )

        info_embed.add_field(
            name=f"{emojize(':crossed_swords:')} Codewars",
            value=f"Set your clan to **CodeSoc**\n",
            inline=True
        )

        info_embed.add_field(
            name="Need help?",
            value=f"Send '{ctx.prefix}help'",
            inline=False
        )

        view = PagedEmbedView([info_embed, contributors_embed])

        for button in self.__DEFAULT_INFO_BUTTONS:
            view.add_item(button)

        await view.send(ctx, ephemeral=ephemeral)

    @hybrid_command(name='ping', help='Shows the bot latency')
    async def ping_command(self, ctx):
        embed = Embed(
            color=self.bot.default_color,
            description=f"pong :ping_pong:  {round(self.bot.latency * 1000)}ms",
        )

        await ctx.send(embed=embed)

    @hybrid_command(name='hopper', help='The legend of Grace Hopper')
    async def hopper_command(self, ctx):
        await ctx.send("https://www.smbc-comics.com/?id=2516")

    @command_config_required("github", "api_key")
    @hybrid_command(name="contributors", description="Show a list of Grace's contributors")
    async def contributors(self, ctx):
        embed = await self.get_contributors_embed()
        view = View()

        for button in self.__DEFAULT_INFO_BUTTONS:
            view.add_item(button)

        await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(GraceCog(bot))
