from discord.ext.commands import Cog, hybrid_command
from logging import info
from discord import Member
from bot.models.channel import Channel


class WelcomeCog(Cog, name="Welcome", description="Welcomes new members"):
    """
    A cog that sends a welcome message to new members when they join the server.
    """
    WELCOME_MESSAGE = "Hi {member_name}! Welcome to the **Code Society**.\n\nBefore posting please:\n    - Take a " \
                      "moment to read the <#{info_id}> and the <#{rules_id}>.\n    - Choose some <#{roles_id}>.\n" \
                      "- Feel free to introduce yourself in <#{intro_id}>."

    def __init__(self, bot):
        self.bot = bot

    def get_welcome_message(self, member: Member):
        """
        Return the welcome message for the given member.

        Parameters
        ----------
        member : discord.Member
            The member to welcome.

        Returns
        -------
        str
            The welcome message for the given member.
        """
        return self.WELCOME_MESSAGE.format(
            member_name=member.mention,
            info_id=Channel.get_by(channel_name="info").channel_id,
            rules_id=Channel.get_by(channel_name="rules").channel_id,
            roles_id=Channel.get_by(channel_name="roles").channel_id,
            intro_id=Channel.get_by(channel_name="introductions").channel_id
        )

    @Cog.listener()
    async def on_member_update(self, before, after):
        """
        Send a welcome message to the member when their status is changed from "pending" to any other status.

        Parameters
        ----------
        before : discord.Member
            The member before the update.
        after : discord.Member
            The member after the update.
        """
        if not before.bot and (before.pending and not after.pending):
            info(f"{after.display_name} accepted the rules!")

            welcome_channel = self.bot.get_channel_by_name("welcome")
            if not welcome_channel:
                welcome_channel = before.bot.system_channel

            await welcome_channel.send(self.get_welcome_message(after))

    @Cog.listener()
    async def on_member_join(self, member):
        """
        Log a message when a member joins the server.

        Parameters
        ----------
        member : discord.Member
            The member who joined the server.
        """
        info(f"{member.display_name} joined the server!")

    @hybrid_command(name="welcome", description="Welcomes the person who issues the command")
    async def welcome_command(self, ctx):
        """
        Send a welcome message to the person who issued the command.

        Parameters
        ----------
        ctx : discord.ext.commands.Context
            The context in which the command was invoked.
        """
        info(f"{ctx.author.display_name} asked to get welcomed!")

        await ctx.send(self.get_welcome_message(ctx.author), ephemeral=True)


async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))
