from discord.ext.commands import Cog, command
from logging import info
from discord import Member
from bot.grace import Grace
from bot.models.channel import Channel


class WelcomeCog(Cog):
    WELCOME_MESSAGE = "Hi {member_name}! Welcome to the **Code Society**.\n\nBefore posting please:\n    - Take a" \
                      "moment to read the <#{info_id}> and the <#{rules_id}>.\n    - Choose some <#{roles_id}>.\n" \
                      "- Feel free to introduce yourself in <#{intro_id}>."

    def __init__(self, bot: Grace):
        self.bot: Grace = bot

    def get_welcome_message(self, member: Member):
        return self.WELCOME_MESSAGE.format(
            member_name=member.mention,
            info_id=Channel.get_by(channel_name="info").channel_id,
            rules_id=Channel.get_by(channel_name="rules").channel_id,
            roles_id=Channel.get_by(channel_name="roles").channel_id,
            intro_id=Channel.get_by(channel_name="introductions").channel_id
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
        info(f"{member.display_name} joined the server!")

    @command(name="welcome", description="Welcomes the person who issues the command")
    async def welcome_command(self, ctx):
        info(f"{ctx.author.display_name} asked to get welcomed!")

        await ctx.send(self.get_welcome_message(ctx.author))


async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))
