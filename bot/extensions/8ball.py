import discord
from discord.colour import Color
from discord.ext.commands import Cog, command
from discord import Embed
import random


class eightball(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='eightball', help="Ask a question and be answered by Grace", aliases=['8ball'])
    async def eightball(self, ctx):

        responses = ['Hell no.', 'Prolly not.', 'Idk bro.',
                     'Prolly.', 'Hell yeah my dude.',
                     'It is certain.', 'It is decidedly so.',
                     'Without a Doubt.', 'Definitely.',
                     'You may rely on it.', 'As i see it, Yes.',
                     'Most Likely.', 'Outlook Good.',
                     'Yes!', 'No!', 'Signs a point to Yes!',
                     'Reply Hazy, Try again.', 'IDK m8 try again.',
                     'Better not tell you know.', 'Cannot predict now.',
                     'Concentrate and ask again.', "Don't Count on it.",
                     'My reply is No.', 'My sources say No.',
                     'Outlook not so good.', 'Very Doubtful']

        answer = Embed(
            title="Grace says: ",
            Color=0x00ff00,
            description=random.choice(responses)
        )

        await ctx.send(embed=answer)


def setup(bot):
    bot.add_cog(eightball(bot))
