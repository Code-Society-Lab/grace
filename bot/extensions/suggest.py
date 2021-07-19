from discord.ext.commands import Cog, command
from discord import Embed

class suggest(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='suggest', help='give suggestion', usage='suggest')
    async def suggest(self, ctx, suggestion):
        suggestion_channel = self.bot.get_channel(841968280168300574)

        embed = Embed(
            color=self.bot.default_color,
            description=f"{suggestion} \n \n  {ctx.message.author.name}",
        )
        await suggestion_channel.send(embed=embed);

def setup(bot):
    bot.add_cog(suggest(bot))

