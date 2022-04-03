from discord.ext.commands import Cog, command
from logging import info
from discord import Member
from bot.grace import Grace


class WelcomeCog(Cog):
    def __init__(self, bot: Grace):
        self.bot = bot
        self.channels = self.bot.config.channels
        self.welcome_message = self.bot.config.welcome_message

    async def print_welcome_message(self, member: Member):
        welcome_message = self.bot.config.welcome_message
        welcome_channel = self.bot.get_channel(self.bot.config.get_channel(name="welcome").channel_id)

        message = welcome_message.format(
            member_name=member.mention,
            info_id=self.bot.config.get_channel(name="info").channel_id,
            rules_id=self.bot.config.get_channel(name="rules").channel_id,
            roles_id=self.bot.config.get_channel(name="roles").channel_id,
            intro_id=self.bot.config.get_channel(name="introductions").channel_id
        )

        await welcome_channel.send(message)

    @Cog.listener()
    async def on_member_update(self, before, after):
        if not before.bot and (before.pending and not after.pending):
            info(f"{after.display_name} accepted the rules!")
            await self.print_welcome_message(after)

    @Cog.listener()
    async def on_member_join(self, member):
        """Will most probably be used to save the info a future log file"""
        info(f"{member.display_name} joined the server!")


def setup(bot):
    bot.add_cog(WelcomeCog(bot))
