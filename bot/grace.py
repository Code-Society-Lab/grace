from logging import info, warning, critical
from discord import Intents, LoginFailure
from discord.ext import commands
from pretty_help import PrettyHelp
from bot import app
from bot.helpers.color_helper import get_color_digit
from bot.models.bot import Bot
from bot.models.extension import Extension
from utils.extensions import get_extensions
from utils.models import load_models


class Grace(commands.Bot):
    def __init__(self):
        self.bot_config = Bot.where(name="Grace").first()

        super().__init__(
            command_prefix=commands.when_mentioned_or(self.bot_config.prefix),
            description=self.bot_config.description,
            help_command=PrettyHelp(color=self.default_color),
            intents=Intents.all()
        )

    @property
    def config(self):
        return self.bot_config

    @property
    def default_color(self):
        return get_color_digit(self.bot_config.default_color_code)

    def load_extensions(self, modules):
        for module in modules:
            extension_name = module.split(".")[-1]
            extension = Extension.where(name=extension_name).first()

            if not extension:
                warning(f"{extension_name} is not registered. Registering the extension.")
                extension = Extension(name=extension_name)
                extension.save()

            if extension.is_enabled():
                info(f"Loading {extension.name}")
                self.load_extension(extension.module)
            else:
                info(f"{module} is disabled, thus it will not be loaded.")

    async def on_ready(self):
        info(f"{self.user.name}#{self.user.id} is online and ready to use!")


def start():
    """Starts the bot"""

    load_models()
    extensions = get_extensions()

    try:
        if app.token:
            grace_bot = Grace()
            grace_bot.load_extensions(extensions)
            grace_bot.run(app.token)
        else:
            critical("Unable to find the token. Make sure your current directory contains an '.env' and that 'DISCORD_TOKEN' is defined")
    except LoginFailure as e:
        critical(f"{e}")
