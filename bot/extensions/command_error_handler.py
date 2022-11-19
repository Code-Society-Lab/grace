from logging import warning
from discord.ext.commands import Cog, \
    MissingRequiredArgument, \
    CommandNotFound, \
    MissingPermissions, \
    CommandOnCooldown, \
    DisabledCommand
from bot.helpers.error_helper import send_error
from requests.exceptions import ConnectionError as RequestConnectionError


class CommandErrorHandler(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_command_error(self, ctx, command_error):
        warning(f"Error: {command_error}. Issued by {ctx.author}")

        warning(type(command_error.original.original))

        if isinstance(command_error, CommandNotFound):
            await send_command_help(ctx)
        elif isinstance(command_error, MissingPermissions):
            await send_error(ctx, "You don't have the authorization to use that command.")
        elif isinstance(command_error, CommandOnCooldown):
            await send_error(ctx, f"You're on Cooldown, wait {command_error.retry_after:.2f} seconds.")
        elif isinstance(command_error, DisabledCommand):
            await send_error(ctx, "This command is disabled.")
        elif isinstance(command_error, MissingRequiredArgument):
            await send_command_help(ctx)
        elif RequestConnectionError:
            await ctx.send("Unable to make the connection, please try again later!", ephemeral=True)


def send_command_help(ctx):
    if ctx.command:
        return ctx.send_help(ctx.command)
    return ctx.send_help()


async def setup(bot):
    await bot.add_cog(CommandErrorHandler(bot))
