from grace.bot import Bot
from logging import info, warning, critical
from discord import Intents, Colour, Activity, ActivityType, Object as DiscordObject
from pretty_help import PrettyHelp
from bot.models.channel import Channel
from bot.models.extension import Extension


class Grace(Bot):
    def __init__(self, app, scheduler):
        self.scheduler = scheduler

        super().__init__(app,
            intents=Intents.all(),
            activity=Activity(type=ActivityType.playing, name="::help")
        )

        self.help_command = PrettyHelp(color=self.default_color)

    @property
    def default_color(self):
        return Colour.from_str(self.config.get("default_color"))

    def get_channel_by_name(self, name):
        channel = Channel.get_by(channel_name=name)

        if channel:
            return self.get_channel(channel.channel_id)
        return None

    async def load_extensions(self):
        for module in self.app.extension_modules:
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
        self.scheduler.start()


    async def invoke(self, ctx):
        if ctx.command:
            info(f"'{ctx.command}' has been invoked by {ctx.author} ({ctx.author.display_name})") 
        await super().invoke(ctx)

    async def setup_hook(self):
        await self.load_extensions()

        if self.app.command_sync:
            warning("Syncing application commands. This may take some time.")
            guild = DiscordObject(id=self.app.config.get("client", "guild_id"))

            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)