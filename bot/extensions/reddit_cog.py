from discord.ext.commands import Cog
from discord import Message, Embed
from bot import app
from bot.helpers.log_helper import danger
from typing import List
import re


class RedditCog(Cog, name='Reddit', description='Reddit utilities'):
    def __init__(self, bot):
        self.bot = bot
        self.blacklisted_subreddits = app.config.get('reddit', 'blacklist', '').split(
            ';'
        )

    @property
    def moderation_channel(self):
        """Returns the moderation channel"""
        return self.bot.get_channel_by_name('moderation_logs')

    async def notify_moderation(self, message: Message, blacklisted: List[str]):
        """Notifies moderators about a blacklisted subreddit mention

        :param message: Message that contained blacklisted subreddits
        :type message: Message
        :param blacklisted: List of blacklisted subreddits
        :type blacklisted: List[str]
        """
        if self.moderation_channel:
            log = danger(
                'BLACKLISTED SUBREDDIT',
                f'{message.author.mention} mentioned blacklisted subreddits:'
                f'{", ".join(blacklisted)}\n\nMessage: {message.jump_url}',
            )
            await log.send(self.moderation_channel)

    async def extract_subreddits(self, message: Message) -> List[List]:
        """Extracts and filters all mentioned subreddits from a message

        :param message: Message from which to extract subreddits
        :type message: Message

        :returns: List containing both valid and blacklisted subreddits
        :rtype: List[List]
        """
        subreddit_matches = re.findall(
            r'(?<![/.])\br/([A-Za-z0-9_]{3,21})', message.content
        )

        subreddits = []
        blacklisted = []

        for subreddit in set(subreddit_matches):
            if subreddit in self.blacklisted_subreddits:
                blacklisted.append(subreddit)
            else:
                subreddits.append(subreddit)

        return [subreddits, blacklisted]

    @Cog.listener()
    async def on_message(self, message: Message):
        """Listens for messages and replies with links to subreddits
        if any were mentioned

        :param message: Message a user has sent
        :type message: Message
        """

        # Make sure that the message recieved is not sent by Grace
        if message.author.id != self.bot.user.id:
            subreddits, blacklisted = await self.extract_subreddits(message)

            if blacklisted:
                await self.notify_moderation(message, blacklisted)

            if subreddits:
                ctx = await self.bot.get_context(message)
                subreddit_links = [
                    f'https://www.reddit.com/r/{subreddit}' for subreddit in subreddits
                ]

                answer_embed = Embed(
                    title="Here're the subreddits you mentioned",
                    color=self.bot.default_color,
                    description='\n'.join(subreddit_links),
                )

                await ctx.reply(embed=answer_embed)


async def setup(bot):
    await bot.add_cog(RedditCog(bot))
