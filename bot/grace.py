from logging import info, warning, critical
from discord import Intents, LoginFailure
from discord.ext import commands
from pretty_help import PrettyHelp
from bot import app
from bot.models.channel import Channel
from bot.models.extension import Extension


class Grace(commands.Bot):
    def __init__(self):
        self.config = app.bot
        self.default_color = int(self.config.get("default_color"), 16)

        super().__init__(
            command_prefix=commands.when_mentioned_or(self.config.get("prefix")),
            description=self.config.get("description"),
            help_command=PrettyHelp(color=self.default_color),
            intents=Intents.all()
        )

    def get_channel_by_name(self, name):
        return self.get_channel(Channel.get_by(channel_name=name).channel_id)

    async def load_extensions(self):
        for module in app.extension_modules:
            extension = Extension.get_by(module_name=module.name)

            if not extension:
                warning(f"{module.name} is not registered. Registering the extension.")
                extension = Extension.create(module_name=module.name)

            if extension.is_enabled():
                info(f"Loading {module.name}")
                await self.load_extension(module.name)
            else:
                info(f"{module.name} is disabled, it will not be loaded.")

    async def on_ready(self):
        info(f"{self.user.name}#{self.user.id} is online and ready to use!")

    async def invoke(self, ctx):
        if ctx.command:
            info(f"'{ctx.command}' has been invoked by {ctx.author} ({ctx.author.nick})")
        await super().invoke(ctx)

    async def setup_hook(self):
        await self.load_extensions()

        if app.command_sync:
            await self.tree.sync()


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
