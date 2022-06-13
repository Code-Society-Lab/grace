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

        super().__init__(
            command_prefix=commands.when_mentioned_or(self.config.get("prefix")),
            description=self.config.get("description"),
            help_command=PrettyHelp(color=self.default_color),
            intents=Intents.all()
        )

    @property
    def default_color(self):
        return int(self.config.get("default_color"), 16)

    def load_extensions(self):
        modules = app.extensions

        for module in modules:
            extension_name = module.name.split(".")[-1]
            extension = Extension.get_by(name=extension_name)

            if not extension:
                warning(f"{extension_name} is not registered. Registering the extension.")
                extension = Extension.create(name=extension_name)

            if extension.is_enabled():
                info(f"Loading {extension_name}")
                self.load_extension(module.name)
            else:
                info(f"{extension_name} is disabled, thus it will not be loaded.")

    def get_channel_by_name(self, name):
        return self.get_channel(Channel.get_by(channel_name=name).channel_id)

    async def on_ready(self):
        info(f"{self.user.name}#{self.user.id} is online and ready to use!")

    async def invoke(self, ctx):
        info(f"'{ctx.command}' has been invoked by {ctx.author} ({ctx.author.nick})")
        await super().invoke(ctx)


def start():
    """Starts the bot"""
    try:
        if app.token:
            grace_bot: Grace = Grace()
            grace_bot.load_extensions()
            grace_bot.run(app.token)
        else:
            critical("Unable to find the token. Make sure your current directory contains an '.env' and that "
                     "'DISCORD_TOKEN' is defined")
    except LoginFailure as e:
        critical(f"Authentication failed : {e}")
