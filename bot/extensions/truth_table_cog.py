from discord.ext.commands import Cog, hybrid_group, Context
from bot.extensions.command_error_handler import CommandErrorHandler
        
# A cog for creating full truth tables from a given expression
class TruthTableCog(Cog, name="Truth Table", description="Create truth tables from expressions"):
    # Constructor
    def __init__(self, bot):
        self.bot = bot
    
    # Create a group of commands
    @hybrid_group(name="ttc", help="Truth Table commands")
    async def truth_table_group(self, ctx: Context) -> None:
        if ctx.invoked_subcommand is None:
            await CommandErrorHandler.send_command_help(ctx)
    
    # Main command
    @truth_table_group.command(name="evaluate", aliases=['eval'], help="Input a proposition and get a truth table.", usage="\"{proposition}\"")
    async def truth_table_command(self, ctx: Context, proposition: str) -> None:
        # Check if the proposition is valid
        if not self.is_valid_proposition(proposition):
            await ctx.send("Invalid proposition.")
            return
        
        # Create a truth table
        truth_table = self.create_truth_table(proposition)
        
        await ctx.send(f"Truth table: ```{truth_table}```")
    
    # Check if a proposition is valid
    def is_valid_proposition(self, proposition: str) -> bool:
        # Check if the proposition is empty
        if not proposition:
            print("Failed: Empty proposition")
            return False
        
        # Check if the proposition is valid - ~ == not, v == or, ^ == and, > == implies, = == iff
        for char in proposition:
            if char not in ['~', '(', ')', 'v', '^', '>', '=', ' ']:
                if not char.isalpha():
                    print(f"Failed: Invalid character {char}")
                    return False
        
        # Check if the proposition is balanced
        if not self.is_balanced_proposition(proposition):
            print("Failed: Unbalanced proposition")
            return False
        
        # Check if the proposition is well-formed
        if not self.is_well_formed_proposition(proposition):
            print("Failed: Proposition is not well-formed")
            return False
        
        # Return true if the proposition is valid
        return True

    # Check if a proposition is balanced
    def is_balanced_proposition(self, proposition: str) -> bool:
        # Check if the proposition is balanced
        balance = 0
        for char in proposition:
            if char == '(':
                balance += 1
            elif char == ')':
                balance -= 1
            if balance < 0:
                return False
        
        # Return true if the proposition is balanced
        return balance == 0
    
    # Check if a proposition is well-formed - Might need to be extended
    def is_well_formed_proposition(self, proposition: str) -> bool:
        # Check if the proposition is well-formed (i.e. there are no 2 consecutive operators)
        for i in range(len(proposition) - 1):
            if proposition[i] in ['v', '^', '>', '='] and proposition[i + 1] in ['v', '^', '>', '=']:
                return False
            
        # Return true if the proposition is well-formed
        return True

    def negation(p): # Not
        return not p
    
    def conjunction(p, q): # And
        return p and q
    
    def disjunction(p, q): # Or
        return p or q
    
    def conditional(p, q): # Implies
        return not p or q
    
    def biconditional(p, q): # Iff
        return p == q

    # Create a truth table from a proposition
    def create_truth_table(self, proposition: str) -> str:
        # TODO: Create a truth table from a proposition
        return "Truth table"




    
# Setup the cog
async def setup(bot):
    await bot.add_cog(TruthTableCog(bot))