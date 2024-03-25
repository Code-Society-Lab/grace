from discord.ext.commands import Cog, hybrid_command
from logging import info
from bot.models.channel import Channel
from discord import Embed


class WelcomeCog(Cog, name="Welcome", description="Welcomes new members"):
    """A cog that sends a welcome message to new members when they join the server."""

    BASE_WELCOME_MESSAGE = "Hi **{member}!** Welcome to the **Code Society**."

    def __init__(self, bot):
        self.bot = bot

    def get_welcome_message(self, member):
        """Return the welcome message for the given member.

        :param member: The member to welcome.
        :type member: discord.Member

        :return: The welcome message for the given member.
        :rtype: str
        """
        return "\n\n".join([
            self.BASE_WELCOME_MESSAGE.format(member=member.mention), 
            self.__get_help_section(),
            self.__get_posting_section()
        ]).strip()

    def __get_help_section(self):
        """Return the help section of the welcome message.

        :return: The help section of the welcome message.
        :rtype: str
        """
        help_channel = Channel.get_by(channel_name="help")
        guidelines_channel = Channel.get_by(channel_name="posting_guidelines")

        help_id = getattr(help_channel, "channel_id", "")
        guidelines_id = getattr(guidelines_channel, "channel_id", "")

        if help_id and guidelines_channel:
            return f"If you need help, read the <#{guidelines_id}> and open a post in <#{help_id}>"
        return ""

    def __get_posting_section(self):
        """Return the posting section of the welcome message.

        :return: The posting section of the welcome message.
        :rtype: str
        """
        channels = ["info", "rules", "roles", "introductions"]
        channel_ids = [getattr(Channel.get_by(channel_name=n), "channel_id", "") for n in channels]

        print(channel_ids)
        print(all(channel_ids))

        if all(channel_ids):
            return "\n".join([
                f"Before posting please:",
                f"- Take a moment to read the <#{channel_ids[0]}> and the <#{channel_ids[1]}>.",
                f"- Choose some <#{channel_ids[2]}>.",
                f"- Introduce yourself in <#{channel_ids[3]}>.",
             ])
        return ""

    @Cog.listener()
    async def on_member_update(self, before, after):
        """Send a welcome message to the member when their status is changed from "pending" to any other status.

        :param before: The member before the update.
        :type before: discord.Member
        :param after: The member after the update.
        :type after: discord.Member
        """
        if not before.bot and (before.pending and not after.pending):
            info(f"{after.display_name} accepted the rules!")

            welcome_channel = self.bot.get_channel_by_name("welcome")
            if not welcome_channel:
                welcome_channel = before.bot.system_channel

            embed = Embed(color=self.bot.default_color)
            embed.add_field(
                name="The Code Society Server",
                value=self.get_welcome_message(after),
                inline=False
            )

            await welcome_channel.send(embed=embed)

    @Cog.listener()
    async def on_member_join(self, member):
        """Log a message when a member joins the server.

        :param member: The member who joined the server.
        :type member: discord.Member
        """
        info(f"{member.display_name} joined the server!")

    @hybrid_command(name="welcome", description="Welcomes the person who issues the command")
    async def welcome_command(self, ctx):
        """Send a welcome message to the person who issued the command.

        :param ctx: The context in which the command was invoked.
        :type ctx: Context
        """
        info(f"{ctx.author.display_name} asked to get welcomed!")

        embed = Embed(
            color=self.bot.default_color,
            title="The Code Society Server",
            description=self.get_welcome_message(ctx.author),
        )

        await ctx.send(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))
