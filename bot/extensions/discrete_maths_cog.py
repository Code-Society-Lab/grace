# Discrete maths cog for Grace
# Author: Parker Cranfield

from discord.ext.commands import Cog, hybrid_group, Context
from bot.extensions.command_error_handler import CommandErrorHandler

from lib.discrete_maths import DiscreteMaths

# A cog for discrete maths commands
class DiscreteMathsCog(Cog, name="Discrete Maths", description="Run discrete maths commands."):
    # Constructor
    def __init__(self, bot):
        self.bot = bot
    
    # Create a group of commands
    @hybrid_group(name="dm", help="Discrete Maths commands")
    async def discrete_maths_group(self, ctx: Context) -> None:
        if ctx.invoked_subcommand is None:
            await CommandErrorHandler.send_command_help(ctx)
    
    # Main command
    @discrete_maths_group.command(name="truth_table", aliases=['tt'], help="Input a proposition and get a truth table. example: \"(~A v B) ^ S\"", usage="\"{proposition}\"")
    async def truth_table_command(self, ctx: Context, proposition: str) -> None:
        await ctx.send(f"Truth table: ```{DiscreteMaths().create_truth_table(proposition)}```")
    
    
    
# Setup the cog
async def setup(bot):
    await bot.add_cog(DiscreteMathsCog(bot))