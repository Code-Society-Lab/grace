from logging import warning
from discord.ext.commands import Cog, \
    MissingRequiredArgument, \
    CommandNotFound, \
    MissingPermissions, \
    CommandOnCooldown, \
    DisabledCommand, HybridCommandError
from bot.helpers.error_helper import send_error


class CommandErrorHandler(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener("on_command_error")
    async def get_command_error(self, ctx, error):
        warning(f"Error: {error}. Issued by {ctx.author}")

        if isinstance(error, CommandNotFound):
            await send_command_help(ctx)
        elif isinstance(error, MissingPermissions):
            await send_error(ctx, "You don't have the authorization to use that command.")
        elif isinstance(error, CommandOnCooldown):
            await send_error(ctx, f"You're on Cooldown, wait {error.retry_after:.2f} seconds.")
        elif isinstance(error, DisabledCommand):
            await send_error(ctx, "This command is disabled.")
        elif isinstance(error, MissingRequiredArgument):
            await send_command_help(ctx)
        elif isinstance(error, HybridCommandError):
            await self.get_app_command_error(ctx.interaction, error)

    @Cog.listener("on_app_command_error")
    async def get_app_command_error(self, interaction, error):
        await interaction.response.send_message("Interaction failed, please try again later!", ephemeral=True)


def send_command_help(ctx):
    if ctx.command:
        return ctx.send_help(ctx.command)
    return ctx.send_help()


async def setup(bot):
    await bot.add_cog(CommandErrorHandler(bot))
