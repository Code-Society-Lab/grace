from logging import info, warning, error, critical
from discord.ext import commands
from bot.help import Help


class Grace(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=":",
            description="Grace is the community bot of the Code Society server.",
            help_command=Help()
        )

    def load_extensions(self, extensions):
        for extension in extensions:
            info(f"Loading {extension}")
            self.load_extension(extension)

    async def on_ready(self):
        info(f"{self.user.name}#{self.user.id} is online and ready to use")

    async def on_command_error(self, ctx, command_error):
        warning(f"Error: {command_error}. Issued by {ctx.author}")

        if isinstance(command_error, commands.MissingRequiredArgument):
            await self.help_command.send_command_help(ctx, ctx.command)
        elif isinstance(command_error, commands.CommandNotFound):
            await ctx.send(f"Command not found. Enter '{self.command_prefix[0]}help' to get help")
        elif isinstance(command_error, commands.MissingPermissions):
            await ctx.send("You don't have the authorization to use that command.")
        elif ctx.command:
            await self.help_command.send_command_help(ctx, ctx.command)
        else:
            await ctx.send("An error occurred. Contact the the administrators")
