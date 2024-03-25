from discord.ext.commands import Cog, hybrid_command
from logging import info
from bot.models.channel import Channel
from discord import Embed


class WelcomeCog(Cog, name="Welcome", description="Welcomes new members"):
    """A cog that sends a welcome message to new members when they join the server."""

    BASE_WELCOME_MESSAGE = "Hi **{member}!** Welcome to the **Code Society**."

    def __init__(self, bot):
        self.bot = bot

    @property
    def help_section(self):
        return self.__build_section(
            ["help", "posting_guidelines"],
            "If you need help, read the <#{}> and open a post in <#{}>"
        )

    @property
    def info_section(self):
        return self.__build_section(
            ["info", "rules", "roles", "introductions"],
            "Before posting please:\n"
            "- Take a moment to read the <#{}> and the <#{}>.\n"
            "- Choose some <#{}>.\n"
            "- Introduce yourself in <#{}>."
        )

    def get_welcome_message(self, member):
        """Return the welcome message for the given member.

        :param member: The member to welcome.
        :type member: discord.Member

        :return: The welcome message for the given member.
        :rtype: str
        """
        return "\n\n".join(filter(None, [
            self.BASE_WELCOME_MESSAGE, 
            self.help_section,
            self.info_section,
        ])).strip().format(member=member.mention)

    def __build_section(self, channel_names, message):
        """Build a section of the welcome message.

        :param channel_names: The names of the channels to include in the section.
        :type channel_names: List[str]

        :param message: The message to include in the section.
        :type channel_names: str

        :return: The section of the welcome message.
        :rtype: str
        """
        channel_ids = [getattr(Channel.get_by(channel_name=n), "channel_id", "") for n in channel_names]
        return message.format(*channel_ids) if all(channel_ids) else ""

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
