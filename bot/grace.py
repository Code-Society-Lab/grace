from logging import info, warning

from discord import Activity, ActivityType, Colour, Intents
from pretty_help import PrettyHelp

from bot.models.channel import Channel
from bot.models.extension import Extension
from grace.bot import Bot


class Grace(Bot):
    def __init__(self, app):
        super().__init__(
            app,
            intents=Intents.all(),
            activity=Activity(type=ActivityType.playing, name="::help"),
        )

        self.help_command = PrettyHelp(color=self.default_color)

    @property
    def default_color(self):
        return Colour.from_str(self.config.get('default_color'))

    def get_channel_by_name(self, name):
        channel = Channel.find_by(channel_name=name)

        if channel:
            return self.get_channel(channel.channel_id)
        return None

    async def load_extensions(self):
        for module in self.app.extension_modules:
            extension = Extension.where(module_name=module).first()

            if not extension:
                warning(f"{module} is not registered. Registering the extension.")
                extension = Extension.create(module_name=module)

            if not extension.should_be_loaded():
                extension.disable()

            if extension.is_enabled():
                info(f'Loading {module}')
                await self.load_extension(module)
            else:
                info(f'{module} is disabled, it will not be loaded.')

    async def on_ready(self):
        info(f'{self.user.name}#{self.user.id} is online and ready to use!')
