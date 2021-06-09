from logging import info, warning, error, critical
from discord.ext import commands
from bot.help import Help


class Grace(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="::",
            description="Grace is the official Code Society Discord bot.",
            help_command=Help()
        )

    def load_extensions(self, extensions):
        for extension in extensions:
            info(f"Loading {extension}")
            self.load_extension(extension)

    async def on_ready(self):
        info(f"{self.user.name}#{self.user.id} is online and ready to use")
