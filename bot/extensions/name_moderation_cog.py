import logging

from discord import Member
from discord.errors import Forbidden
from discord.ext.commands import Cog

from bot import app
from bot.grace import Grace
from bot.helpers.log_helper import notice
from bot.services.random_name_service import make_random_name

logger = logging.getLogger(__name__)


class NameModerationCog(
    Cog, name="Names", description="Checks and changes user's nickname."
):
    """A cog that checks when a member joins if they have a bad word in their name, and changes their name in case they do."""

    def __init__(self, bot: Grace):
        self.bot: Grace = bot
        self.BAD_WORDS = set(app.config.get("name_moderation", "blacklist", ""))

    @property
    def moderation_channel(self):
        return self.bot.get_channel_by_name("moderation_logs")

    @Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        """Chnage a user's nickname if it contains a bad word.

        :param member: The member to check their username or display name.
        :type member: discord.Member
        """

        name = member.display_name

        if not self.contains_bad_word(name):
            return

        try:
            good_name = make_random_name()
            await member.edit(nick=good_name)

            log = notice("NAME", f"Username of {name} was changed.")
            log.add_field(
                "Reason: ",
                f"User {name} joined with an inappropriate name, thus it was changed to {good_name}.",
            )

            if self.moderation_channel:
                await log.send(self.moderation_channel)

            await member.send(
                f"Your name has an inappropriate word in it, thus it was changed from {name} to {good_name}."
            )

        except Forbidden:
            logger.info("User left before we could send them a message.")

    def contains_bad_word(self, name: str) -> bool:
        """Checks if a name has a bad word in it.

        :param name: The name to check.
        :type name: str

        :return: True if the name has a bad word, otherwise false.
        :rtype: bool
        """
        lowered = name.lower()

        return any(bad_word in lowered for bad_word in self.BAD_WORDS)


async def setup(bot: Grace):
    await bot.add_cog(NameModerationCog(bot))
