from logging import info, warning, critical
from typing import List
from discord import Intents, LoginFailure
from discord.ext import commands
from pretty_help import PrettyHelp
from bot import app
from bot.models.bot import Bot
from bot.models.extension import Extension
from utils.extensions import get_extensions
from utils.models import load_models


class Grace(commands.Bot):
    def __init__(self):
        self.config: Bot = Bot.get_current()

        super().__init__(
            command_prefix=commands.when_mentioned_or(self.config.prefix),
            description=self.config.description,
            help_command=PrettyHelp(color=self.default_color),
            intents=Intents.all()
        )

    @property
    def default_color(self):
        return int(self.config.default_color_code, 16)

    def load_extensions(self, modules: List):
        for module in modules:
            extension_name: str = module.split(".")[-1]
            extension: Extension = Extension.where(name=extension_name).first()

            if not extension:
                warning(f"{extension_name} is not registered. Registering the extension.")
                extension = Extension(name=extension_name)
                extension.save()

            if extension.is_enabled():
                info(f"Loading {extension.name}")
                self.load_extension(extension.module)
            else:
                info(f"{module} is disabled, thus it will not be loaded.")

    def get_channel_by_name(self, name: str):
        return self.get_channel(self.config.get_channel(name=name).channel_id)

    async def on_ready(self):
        info(f"{self.user.name}#{self.user.id} is online and ready to use!")

    async def invoke(self, ctx):
        info(f"'{ctx.command}' has been invoked by {ctx.author} ({ctx.author.nick})")
        await super().invoke(ctx)


def start():
    """Starts the bot"""

    load_models()
    extensions: List[str] = get_extensions()

    try:
        if app.token:
            grace_bot: Grace = Grace()
            grace_bot.load_extensions(extensions)
            grace_bot.run(app.token)
        else:
            critical("Unable to find the token. Make sure your current directory contains an '.env' and that "
                     "'DISCORD_TOKEN' is defined")
    except LoginFailure as e:
        critical(f"Impossible to login in. Err. {e}")
