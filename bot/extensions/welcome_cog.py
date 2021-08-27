from discord.ext.commands import Cog
from logging import info
from discord import Member
from bot.grace import Grace


class WelcomeCog(Cog):
    def __init__(self, bot: Grace):
        self.bot = bot
        self.channels = self.bot.config.channels
        self.welcome_message = self.bot.config.welcome_message

    async def print_welcome_message(self, member: Member):
        welcome_channel = self.bot.get_channel(self.channels.where(name="welcome").first())

        message = self.welcome_message.format(
            member_name=member.mention,
            info_id=self.channels.where(name="info").first(),
            rules_id=self.channels.where(name="rules").first(),
            roles_id=self.channels.where(name="roles").first(),
            intro_id=self.channels.where(name="introductions").first()
        )

        await welcome_channel.send(message)

    @Cog.listener()
    async def on_member_join(self, member):
        info(member.display_name)
        await self.print_welcome_message(member)


def setup(bot):
    bot.add_cog(WelcomeCog(bot))
