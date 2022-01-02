from discord.ext.commands import Cog, command, group, has_permissions
from discord import Message, Embed
from nltk.tokenize import TweetTokenizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
from bot.models.extensions.fun.language.trigger import Trigger


class LanguageCog(Cog):
    def __init__(self, bot):
        self.bot = bot
        # I know not everyone working here is familiar with NLTK so I'll explain some of the terminology.
        # Not to be confused with Auth Tokens, tokenization just means splitting the natural language
        # into discrete meaningful chunks, usually it's words, but words like "it's" or "ain't" will be
        # split into "it is" and "are not".
        # We're using the casual tokenizer for now, but it can be changed down the line so long as you're
        # aware of any new behaviors. https://www.nltk.org/api/nltk.tokenize.html

        self.tokenizer = TweetTokenizer()
        self.sid = SentimentIntensityAnalyzer()

    async def penguin_react(self, message: Message):
        """
        Checks to see if a message contains a reference to Linus (torvalds only), will be made more complicated
        as needed. If a linus reference is positively identified, Grace will react with a penguin emoji.
        I know using NLTK is kinda like bringing a tomahawk missile to a knife fight, but it may come in handy for
        future tasks, so the tokenizer object will be shared across all methods.

        :param message: A discord message to check for references to our lord and savior.
        :return: None
        """
        linus_trigger = Trigger.where(name="Linus").first()

        message_tokens = self.tokenizer.tokenize(message.content)
        tokenlist = list(map(lambda s: s.lower(), message_tokens))
        linustarget = [i for i, x in enumerate(tokenlist) if x in linus_trigger.words]
        # Get the indices of all linuses in the message

        if linustarget:
            fail = False
            for linusindex in linustarget:
                try:
                    if tokenlist[linusindex + 1] == 'tech' and tokenlist[linusindex + 2] == 'tips':
                        fail = True
                    elif tokenlist[linusindex + 1] == 'and' and tokenlist[linusindex + 2] == 'lucy':
                        fail = True
                except IndexError:
                    pass

                # Here we're using the VADER algorithm to prevent Grace from reacting to messages that
                # speak negatively about linus. We run whole message through vader and if the aggregated
                # score is less than 0, then we throw it out.

                sv = self.sid.polarity_scores(message.content)
                if sv['neu'] + sv['pos'] < sv['neg'] or sv['pos'] == 0.0:
                    fail = True
                    if sv['neg'] > sv['pos']:
                        await message.add_reaction(linus_trigger.negative_emoji)
                        return
                overrideset = linus_trigger.words
                if set(overrideset) & set(tokenlist):
                    fail = False

            if not fail:
                await message.add_reaction(linus_trigger.positive_emoji)

    @Cog.listener()
    async def on_message(self, message):
        await self.penguin_react(message)

    @group(name="triggers", help="Commands to manage triggers")
    @has_permissions(administrator=True)
    async def triggers_group(self, ctx):
        if ctx.invoked_subcommand is None:
            trigger = Trigger.where(name="Linus").first()

            embed = Embed(
                color=self.bot.default_color,
                title=f"Triggers",
                description="\n".join(trigger.words)
            )

            await ctx.send(embed=embed)

    @triggers_group.command(name="add", help="Add a trigger word", usage="{new_word}")
    async def add_trigger_word(self, ctx, new_word):
        trigger = Trigger.where(name="Linus").first()

        if trigger:
            if new_word in trigger.words:
                await ctx.send(f"**{new_word}** is already a trigger")
            else:
                trigger.add_trigger_word(new_word)

                await ctx.send(f"Trigger **{new_word}** added successfully")
        else:
            await ctx.send(f"Unable to add **{new_word}**")

    @triggers_group.command(name="remove", help="Remove a trigger word", usage="{old_word}")
    async def remove_trigger_word(self, ctx, old_word):
        trigger = Trigger.where(name="Linus").first()

        if trigger:
            if old_word not in trigger.words:
                await ctx.send(f"**{old_word}** is not a trigger")
            else:
                trigger.remove_trigger_word(old_word)

                await ctx.send(f"Trigger **{old_word}** removed successfully")
        else:
            await ctx.send(f"Unable to remove **{old_word}**")


def setup(bot):

    bot.add_cog(LanguageCog(bot))
