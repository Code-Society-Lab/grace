from discord.ext.commands import Cog, hybrid_command, Context
from discord.ui import Button, View
from emoji import emojize
from bot.helpers import send_error
from bot.helpers.github_helper import create_contributors_embeds, create_repository_button, available_project_names
from bot.services.github_service import GithubService
from lib.config_required import command_config_required
from lib.paged_embeds import PagedEmbedView
from discord.app_commands import Choice, autocomplete
from discord import Embed, Interaction


async def project_autocomplete(_: Interaction, current: str) -> list[Choice[str]]:
    """Provide autocomplete suggestions for the Code Society Lab Projects.

    :param _: The interaction object.
    :type _: Interaction
    :param current: The current value of the input field.
    :type current: str
    :return: A list of `Choice` objects containing project name.
    :rtype: list[Choice[str]]
    """
    return [
        Choice(name=project, value=project)
        for project in available_project_names() if current.lower() in project.lower()
    ]


class GraceCog(Cog, name="Grace", description="Default grace commands"):
    """A cog that contains default commands for the Grace bot."""
    __CODE_SOCIETY_WEBSITE_BUTTON = Button(
        emoji=emojize(":globe_with_meridians:"),
        label="Website",
        url="https://codesociety.xyz"
    )

    def __init__(self, bot):
        self.bot = bot

    @hybrid_command(name='info', help='Show information about the bot')
    async def info_command(self, ctx: Context, ephemeral=True) -> None:
        """Show information about the bot.
        
        :param ctx: The context in which the command was called.
        :type ctx: Context
        :param ephemeral: A flag indicating whether the message should be sent as an ephemeral message. Default is True.
        :type ephemeral: bool, optional
        """
        if ctx.interaction:
            await ctx.interaction.response.defer()

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

        view = PagedEmbedView([info_embed])
        view.add_item(self.__CODE_SOCIETY_WEBSITE_BUTTON)

        if GithubService.can_connect():
            repository = GithubService().get_code_society_lab_repo("grace")
            view.add_item(create_repository_button(repository))

            for embed in create_contributors_embeds(repository):
                view.add_embed(embed)

        await view.send(ctx, ephemeral=ephemeral)

    @hybrid_command(name='ping', help='Shows the bot latency')
    async def ping_command(self, ctx: Context) -> None:
        """Show the bot latency.
        
        :param ctx: The context in which the command was called.
        :type ctx: Context
        """
        embed = Embed(
            color=self.bot.default_color,
            description=f"pong :ping_pong:  {round(self.bot.latency * 1000)}ms",
        )

        await ctx.send(embed=embed)

    @hybrid_command(name='hopper', help='The legend of Grace Hopper')
    async def hopper_command(self, ctx: Context) -> None:
        """Show a link to a comic about Grace Hopper.
        
        :param ctx: The context in which the command was called.
        :type ctx: Context
        :return: None
        """
        await ctx.send("https://www.smbc-comics.com/?id=2516")

    @command_config_required("github", "api_key")
    @hybrid_command(name="contributors", description="Show a list of Code Society Lab's contributors")
    @autocomplete(project=project_autocomplete)
    async def contributors(self, ctx: Context, project: str) -> None:
        """Show a list of contributors for the Code Society Lab repositories.
        
        :param ctx: The context in which the command was called.
        :type ctx: Context
        :param project: The project's name to get contributors.
        :type project: str
        """
        if ctx.interaction:
            await ctx.interaction.response.defer()

        if project not in available_project_names():
            return await send_error(ctx, f"Project '_{project}_' not found.")

        repository = GithubService().get_code_society_lab_repo(project)
        embeds = create_contributors_embeds(repository)
        view = PagedEmbedView(embeds)

        view.add_item(self.__CODE_SOCIETY_WEBSITE_BUTTON)
        view.add_item(create_repository_button(repository))

        await view.send(ctx)


async def setup(bot):
    await bot.add_cog(GraceCog(bot))
