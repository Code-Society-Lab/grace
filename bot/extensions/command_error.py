from logging import warning
from discord.ext.commands import Cog, MissingRequiredArgument, CommandNotFound, MissingPermissions


class CommandError(Cog, name="Grace"):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_command_error(self, ctx, command_error):
        warning(f"Error: {command_error}. Issued by {ctx.author}")

        if isinstance(command_error, MissingRequiredArgument):
            await self.bot.help_command.send_command_help(ctx.command)
        elif isinstance(command_error, CommandNotFound):
            await self.bot.help_command.send_pages(ctx)
        elif isinstance(command_error, MissingPermissions):
            await ctx.send("You don't have the authorization to use that command.")
        elif ctx.command:
            await self.bot.help_command.send_command_help(ctx.command)
        else:
            await ctx.send("An error occurred. Contact the the administrators")


def setup(bot):
    bot.add_cog(CommandError(bot))
