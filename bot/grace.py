import logging

logger = logging.getLogger(__name__)

from discord import Activity, ActivityType, Colour, Intents
from grace.bot import Bot
from pretty_help import PrettyHelp

from lib.dashboard import dashboard
from bot.models.channel import Channel
from bot.models.extension import Extension
from bot.services.dashboard_metrics_service import DashboardMetrics


class Grace(Bot):
    def __init__(self, app):
        super().__init__(
            app,
            intents=Intents.all(),
            activity=Activity(type=ActivityType.playing, name="::help"),
        )

        self.help_command = PrettyHelp(color=self.default_color)
        self.metrics = DashboardMetrics()

    @property
    def default_color(self):
        return Colour.from_str(self.config.get("default_color"))

    @property
    def latency_ms(self):
        return round(self.latency * 1000)

    def get_channel_by_name(self, name):
        channel = Channel.find_by(channel_name=name)

        if channel:
            return self.get_channel(channel.channel_id)
        return None

    async def load_extensions(self):
        for module in self.app.extension_modules:
            extension = Extension.where(module_name=module).first()

            if not extension:
                logger.warning(
                    f"{module} is not registered. Registering the extension."
                )
                extension = Extension.create(module_name=module)

            if not extension.should_be_loaded():
                extension.disable()

            if extension.is_enabled():
                logger.info(f"Loading {module}")
                await self.load_extension(module)
            else:
                logger.info(f"{module} is disabled, it will not be loaded.")

    async def setup_hook(self):
        await super().setup_hook()
        dashboard.init_dachshund()
        dashboard.build_dashboard()

    async def on_ready(self):
        logger.info(f"{self.user.name}#{self.user.id} is online and ready to use!")
        # dachshund.emit(...)

    async def on_reload(self):
        await super().on_reload()
        dashboard.init_dachshund()
