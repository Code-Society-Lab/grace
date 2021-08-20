from logging import info, warning, critical
from discord import Intents, LoginFailure
from discord.ext import commands
from pretty_help import PrettyHelp
from bot import CONFIG, app
from bot.helpers.color_helper import get_color_digit
from bot.models.extension import Extension
from bot.utils.extensions import get_extensions
from bot.utils.models import load_models


class Grace(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(CONFIG.bot.prefix),
            description="Grace is the official Code Society Discord bot.",
            help_command=PrettyHelp(color=self.default_color),
            intents=Intents.all()
        )

    @property
    def default_color(self):
        return get_color_digit(CONFIG.style.embed_color)

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
    load_models()
    extensions = get_extensions()

    try:
        if app.token:
            grace_bot = Grace()
            grace_bot.load_extensions(extensions)
            grace_bot.run(app.token)
        else:
            critical("Token not defined. Add your token in '.env'")
    except LoginFailure as e:
        critical(f"{e}")
        exit()
