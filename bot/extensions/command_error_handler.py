from datetime import timedelta
from logging import warning
from discord.ext.commands import Cog, \
    MissingRequiredArgument, \
    CommandNotFound, \
    MissingPermissions, \
    CommandOnCooldown, \
    DisabledCommand, HybridCommandError, Context
from bot.helpers.error_helper import send_error
from typing import Any, Coroutine, Optional
from discord import Interaction
from lib.config_required import MissingRequiredConfigError


class CommandErrorHandler(Cog):
    """A Discord Cog that listens for command errors and sends an appropriate message to the user."""
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener("on_command_error")
    async def get_command_error(self, ctx: Context, error: Exception) -> None:
        """Event listener for command errors. It logs the error and sends an appropriate message to the user.
    
        :param ctx: The context of the command invocation.
        :type ctx: Context
        :param error: The error that was raised during command execution.
        :type error: Exception
        """
        warning(f"Error: {error}. Issued by {ctx.author}")

        if isinstance(error, CommandNotFound):
            await send_command_help(ctx)
        elif isinstance(error, MissingRequiredConfigError):
            await send_error(ctx, error)
        elif isinstance(error, MissingPermissions):
            await send_error(ctx, "You don't have the authorization to use that command.")
        elif isinstance(error, CommandOnCooldown):
            await send_error(ctx, f"You're on Cooldown, wait {timedelta(seconds=int(error.retry_after))}")
        elif isinstance(error, DisabledCommand):
            await send_error(ctx, "This command is disabled.")
        elif isinstance(error, MissingRequiredArgument):
            await send_command_help(ctx)
        elif isinstance(error, HybridCommandError):
            await self.get_app_command_error(ctx.interaction, error)

    @Cog.listener("on_app_command_error")
    async def get_app_command_error(self, interaction: Optional[Interaction], _: Exception) -> None:
        """Event listener for command errors that occurred during an interaction. 
        It sends an error message to the user.
    
        :param interaction: The interaction where the error occurred.
        :type interaction: Interaction
        :param _ : The error that was raised during command execution.
        :type _: Exception
        """
        if interaction and interaction.is_expired():
            await interaction.response.send_message("Interaction failed, please try again later!", ephemeral=True)


def send_command_help(ctx: Context) -> Coroutine[Any, Any, Any]:
    """Send the help message for the command that raised an error, or 
    the general help message if no specific command was involved.
    
    :param ctx: The context of the command invocation.
    :type ctx: The context
    :return: The help message.
    :rtype: Coroutine[Any, Any, Any]
    """
    if ctx.command:
        return ctx.send_help(ctx.command)
    return ctx.send_help()


async def setup(bot):
    await bot.add_cog(CommandErrorHandler(bot))