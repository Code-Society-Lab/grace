from datetime import datetime

from discord import Message, Member
from discord.ext.commands import Cog, hybrid_command, Context, cooldown, BucketType
from bot.grace import Grace
from bot.models.extensions.thank.thank import Thank


class ThankCog(Cog):
    # TODO: Find all the users of the server and add them to Thank database
    # TODO: Each time new user joins add him to the Thank database
    # TODO: Each time user leaves remove him from database
    def __init__(self, bot: Grace):
        self.bot = bot
        self.thank_list = [
            'thanks',
            'thank you',
            'ty',
            'thnx',
        ]

    @Cog.listener()
    @cooldown(1, 1200, BucketType.user)
    async def on_message(self, message: Message):
        if not message.mentions or \
               message.author in message.mentions or \
               message.author.id == self.bot.user.id:
            return

        thanked = False
        for thank in self.thank_list:
            if thank in message.content.lower():
                thanked = True
                break

        if not thanked:
            return

        for member in message.mentions:
            member_id = str(member.id)
            author_id = str(message.author.id)

            if Thank.does_member_exist(author_id):
                Thank.set_last_thank_date(member_id=author_id, last_thank=datetime.now())
            else:
                Thank.add_member(member_id=author_id, thank_count=0, last_thank=datetime.now())

            if Thank.does_member_exist(member_id):
                Thank.increment_member_thank_count(member_id=member_id)
            else:
                Thank.add_member(member_id=member_id, thank_count=1, last_thank=None)

            await message.channel.send(f'<@{member_id}> thanks for helping <@{message.author.id}>!')

    @hybrid_command(name='thank_stats', description='Shows your current thank level.')
    async def thank_stats(self, ctx: Context, *, member: Member = None):
        # TODO: Check here if user is in the database, if not, send him a message saying that
        # TODO: he wasn't thanked before thus he's not yet a helper.
        # Command can be executed as: /thank_stats => It will output the thank stats of the member who called the command
        # If as: /thank_stats member=@MrNesli => Will output stats of the respective member
        """
        range(0, 10) => "Beginner helper"
        range(10, 20) => "Helper"
        range(20, 30) => "Vetted Helper"
        range(30, 40) => "Professional"
        """
        pass


async def setup(bot: Grace):
    await bot.add_cog(ThankCog(bot))