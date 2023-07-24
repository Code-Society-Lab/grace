from discord.ext.commands import Cog, hybrid_group, Context
from bot.extensions.command_error_handler import CommandErrorHandler
        
# A cog for creating full truth tables from a given expression
class TruthTableCog(Cog):
    # Constructor
    def __init__(self, bot):
        self.bot = bot
    
    # Create a group of commands
    @hybrid_group(name="truthtable", help='Truth Table commands')
    async def truth_table_group(self, ctx: Context) -> None:
        if ctx.invoked_subcommand is None:
            await CommandErrorHandler.send_command_help(ctx)
    
    # Main command
    @truth_table_group.command(name="table", help="Input a proposition and get a truth table.")
    async def truth_table_command(self, ctx: Context) -> None:
        await ctx.send(f"Hello {ctx.author.name}!")


async def setup(bot):
    await bot.add_cog(TruthTableCog(bot))