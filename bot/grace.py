from logging import info, warning, critical
from discord import Intents, LoginFailure, ActivityType, Activity
from discord.ext.commands import Bot, when_mentioned_or
from pretty_help import PrettyHelp
from bot import app
from bot.helpers.bot_helper import default_color
from bot.models.channel import Channel
from bot.models.extension import Extension


class Grace(Bot):
    def __init__(self):
        self.config = app.bot
        self.default_color = default_color()

        super().__init__(
            command_prefix=when_mentioned_or(self.config.get("prefix")),
            description=self.config.get("description"),
            help_command=PrettyHelp(color=self.default_color),
            intents=Intents.all(),
            activity=Activity(type=ActivityType.playing, name="::help")
        )

    def get_channel_by_name(self, name):
        """Gets the channel from the database and returns the discord channel with the associated id.

        :param name: The name of the channel.
        :return: The discord channel.
        """
        channel = Channel.get_by(channel_name=name)

        if channel:
            return self.get_channel(channel.channel_id)
        return None

    async def load_extensions(self):
        for module in app.extension_modules:
            extension = Extension.get_by(module_name=module)

            if not extension:
                warning(f"{module} is not registered. Registering the extension.")
                extension = Extension.create(module_name=module)

            if extension.is_enabled():
                info(f"Loading {module}")
                await self.load_extension(module)
            else:
                info(f"{module} is disabled, it will not be loaded.")

    async def on_ready(self):
        info(f"{self.user.name}#{self.user.id} is online and ready to use!")

    async def invoke(self, ctx):
        if ctx.command:
            info(f"'{ctx.command}' has been invoked by {ctx.author} ({ctx.author.display_name})") 
        await super().invoke(ctx)

    async def setup_hook(self):
        await self.load_extensions()

        if app.command_sync:
            warning("Syncing application commands. This may take some time.")
            guild = self.get_guild(app.config.get("client", "guild"))

            await self.tree.sync(guild=guild)


def start():
    """Starts the bot"""
    try:
        if app.token:
            grace_bot = Grace()
            grace_bot.run(app.token)
        else:
            critical("Unable to find the token. Make sure your current directory contains an '.env' and that "
                     "'DISCORD_TOKEN' is defined")
    except LoginFailure as e:
        critical(f"Authentication failed : {e}")
