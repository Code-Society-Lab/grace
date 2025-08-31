from discord.ext.commands import Cog
from discord import Message, Embed
from bot import app
from bot.helpers.log_helper import danger
import re


class RedditCog(Cog, name="Reddit", description="Reddit related stuff"):
    def __init__(self, bot):
        self.bot = bot

    @property
    def moderation_channel(self):
        """ Returns the moderation channel """
        return self.bot.get_channel_by_name("moderation_logs")

    @property
    def blacklisted_keywords(self):
        """ Parses blacklisted keywords from config """
        blacklist = app.config.get('reddit', 'blacklist', [])

        if isinstance(blacklist, str):
            return blacklist.split(';')

        return []


    def is_blacklisted_subreddit(self, subreddit: str):
        """ Checks if subreddit contains a blacklisted keyword """
        for keyword in self.blacklisted_keywords:
            if keyword in subreddit.lower():
                return True
        return False

    async def extract_subreddits(self, message: Message):
        """ Extracts and filters all mentioned subreddits from a message """
        subreddit_matches = re.findall(r"\br/([A-Za-z0-9_]+)", message.content)
        mods_notified = False
        subreddits = []

        for subreddit in subreddit_matches:
            if self.is_blacklisted_subreddit(subreddit) and not mods_notified:
                if self.moderation_channel:
                    log = danger("BLACKLISTED SUBREDDIT", f"{message.author.mention} has mentioned a blacklisted subreddit.")
                    await log.send(self.moderation_channel)
                mods_notified = True
            else:
                subreddits.append(subreddit)

        return subreddits

    @Cog.listener()
    async def on_message(self, message: Message):
        """ Listens for messages and replies with links to subreddits if any were mentioned """
        subreddits = await self.extract_subreddits(message)
        if len(subreddits) > 0:
            ctx = await self.bot.get_context(message)
            subreddit_links = [f'https://www.reddit.com/r/{subreddit}' for subreddit in subreddits]

            answer_embed = Embed(
                title='Here\'re the subreddits you mentioned',
                color=self.bot.default_color,
                description='\n'.join(subreddit_links),
            )

            await ctx.reply(embed=answer_embed)

async def setup(bot):
    await bot.add_cog(RedditCog(bot))
