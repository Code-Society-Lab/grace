import discord
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import Cog, command, cooldown
from discord import Embed
import random


class EightBall(Cog, description="Magic Eight Ball"):
    def __init__(self, bot):
        self.bot = bot

    @command(name='eightball', aliases=['8ball'], usage='eightball or 8ball' , help="Ask a question and be answered by Grace")
    @cooldown(1, 30, BucketType.user)
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
            title= f'{ctx.author.name}, Grace says: ',
            Color= self.bot.default_color,
            description=random.choice(responses),
        )

        await ctx.send(embed=answer)


def setup(bot):
    bot.add_cog(EightBall(bot))
