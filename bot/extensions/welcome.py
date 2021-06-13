from discord.ext.commands import Cog
from logging import info
from discord import Member, Client
from bot import CONFIG


class WelcomeCog(Cog):
    def __init__(self, bot: Client):
        self.bot = bot

    async def print_welcome_message(self, member: Member):
        welcome = self.bot.get_channel(CONFIG.server.channels.welcome)
        message = CONFIG.bot.welcome_message.format(
            member_name=member.display_name,
            info_id=CONFIG.server.channels.info,
            rules_id=CONFIG.server.channels.rules,
            roles_id=CONFIG.server.channels.roles,
            intro_id=CONFIG.server.channels.introductions
        )
        await welcome.send(message)

    @Cog.listener()
    async def on_member_join(self, member):
        info(member.display_name)
        await self.print_welcome_message(member)


def setup(bot):
    bot.add_cog(WelcomeCog(bot))
