import logging

logger = logging.getLogger(__name__)

from bot import app
from bot.grace import Grace
from discord import Member, Embed
from discord.ext.commands import Cog, Context, hybrid_command
from bot.services.random_name_service import make_random_name
from bot.helpers.log_helper import notice


def slice_name(name: str) -> list[str]:
    """Makes all possible slices of a string, excluding ones shorter than 2 chars.

    :param name: The name or string to get sliced.
    :type name: str

    :return: The list of all possible slices longer than 2 chars of the name.
    :rtype: list[str]
    """

    # There's no inappropriate word of two characters,
    # that's why we discard slices of length 2 or 1
    return [
        name[i:j].lower()
        for i in range(len(name))
        for j in range(len(name) + 1)
        if len(name[i:j]) > 2
    ]


class NameModerationCog(
    Cog, name="Names", description="Checks and changes user's nickname."
):
    """A cog that checks when a member joins if they have a bad word in their name, and changes their name in case they do."""

    BAD_WORDS = set(app.config.get("reddit", "blacklist", "").split(";"))

    def __init__(self, bot: Grace):
        self.bot: Grace = bot

    @property
    def moderation_channel(self):
        return self.bot.get_channel_by_name("moderation_logs")

    @Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        """Chnage a user's nickname if it contains a bad word.

        :param member: The member to check their username or display name.
        :type member: discord.Member
        """

        NAME = member.display_name

        name_slices = slice_name(NAME)

        if not self.check_slices_against_bad_words(name_slices):
            return

        good_name = make_random_name()
        await member.edit(nick=good_name)

        log = notice("NAME", f"Username of {NAME} was changed.")
        log.add_field(
            "Reason: ",
            f"User {NAME} joined with an inappropriate name, thus it was changed to {good_name}.",
        )

        if self.moderation_channel:
            await log.send(self.moderation_channel)

        await member.send(
            f"Your name has an inappropriate word in it, thus it was changed from {NAME} to {good_name}."
        )

    @hybrid_command(
        name="random-name",
        description="Changes the name of the user who issued the command to a random name.",
    )
    async def give_random_name(self, ctx: Context) -> None:
        """Gives the user who invoked the command a new random two words name.

        :param ctx: The context in which the command was invoked.
        :type ctx: Context
        """

        old_name = ctx.author.display_name
        new_name = make_random_name()

        await ctx.author.edit(nick=new_name)

        logger.info(f"User {old_name} requested a new random name, got {new_name}!")

        name_message: Embed = Embed(title="Name Changed!", color=self.bot.default_color)
        name_message.description = (
            f"Your name was changed from {old_name} to {new_name}!"
        )

        await ctx.send(embed=name_message)

    def check_slices_against_bad_words(self, slices: list[str]) -> bool:
        """Checks if a name has a bad word in it.

        :param slices: Slices of the name to check.
        :type slices: list[str]

        :return: True if the name has a bad word, otherwise false.
        :rtype: bool
        """
        slices_set = set(slices)

        return not slices_set.isdisjoint(self.BAD_WORDS)


async def setup(bot: Grace):
    await bot.add_cog(NameModerationCog(bot))
