from discord.ext.commands import Cog, command
from logging import info
from discord import Member
from bot.grace import Grace
from bot.models.bot_channel import BotChannel


class WelcomeCog(Cog):
    WELCOME_MESSAGE = "Hi {member_name}! Welcome to the **Code Society**.\n\nBefore posting please:\n    - Take a" \
                      "moment to read the <#{info_id}> and the <#{rules_id}>.\n    - Choose some <#{roles_id}>.\n" \
                      "- Feel free to introduce yourself in <#{intro_id}>."

    def __init__(self, bot: Grace):
        self.bot: Grace = bot

    def get_welcome_message(self, member: Member):
        return self.WELCOME_MESSAGE.format(
            member_name=member.mention,
            info_id=BotChannel.get_by_name(name="info").channel_id,
            rules_id=BotChannel.get_by_name(name="rules").channel_id,
            roles_id=BotChannel.get_by_name(name="roles").channel_id,
            intro_id=BotChannel.get_by_name(name="introductions").channel_id
        )

    @Cog.listener()
    async def on_member_update(self, before, after):
        if not before.bot and (before.pending and not after.pending):
            info(f"{after.display_name} accepted the rules!")

            welcome_channel = self.bot.get_channel_by_name("welcome")
            if not welcome_channel:
                welcome_channel = before.bot.system_channel

            await welcome_channel.send(self.get_welcome_message(after))

    @Cog.listener()
    async def on_member_join(self, member):
        """Will most probably be used to save the info a future log file"""
        info(f"{member.display_name} joined the server!")

    @command(name="welcome", description="")
    async def welcome_command(self, ctx):
        info(f"{ctx.author.display_name} asked to get welcomed!")

        await ctx.send(self.get_welcome_message(ctx.author))


def setup(bot):
    bot.add_cog(WelcomeCog(bot))
