from discord.ext.commands import Cog, has_permissions, hybrid_group, Context
from discord import Message, Embed
from logging import warning
from nltk.tokenize import TweetTokenizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from bot.models.extensions.language.trigger import Trigger


class LanguageCog(Cog, name="Language", description="Analyze and reacts to messages"):
    def __init__(self, bot):
        """
        I know not everyone working here is familiar with NLTK, so I'll explain some terminology.
        Not to be confused with Auth Tokens, tokenization just means splitting the natural language
        into discrete meaningful chunks, usually it's words, but words like "it's" or "ain't" will be
        split into "it is" and "are not".
        We're using the casual tokenizer for now, but it can be changed down the line so long as you're
        aware of any new behaviors. https://www.nltk.org/api/nltk.tokenize.html
        """
        self.bot = bot

        self.tokenizer = TweetTokenizer()
        self.sid = SentimentIntensityAnalyzer()

    def get_message_sentiment_polarity(self, message: Message) -> int:
        """
        Checks sentiment of a given message
        :param message: A discord message to anlyze the sentiment of
        :type message: discord.Message
        :returns:
            -1 iff the message is more negative than positive
             0 iff the message is neutral
             1 iff the message is more positive than negative
        """
        # Here we're using the VADER algorithm to determine if the message sentiment is speaking
        # negatively about something. We run the while message through vader and if the aggregated
        # score is ultimately negative, neutral, or positive
        sv = self.sid.polarity_scores(message.content)
        if sv['neu'] + sv['pos'] < sv['neg'] or sv['pos'] == 0.0:
            if sv['neg'] > sv['pos']:
                return -1
            return 0
        return 1;

    async def name_react(self, message: Message) -> None:
        """
        Checks message sentiment and if the sentiment is neutral or positive,
        react with a positive_emoji, otherwise react with negative_emoji
        """
        grace_trigger = Trigger.get_by(name="Grace")
        if grace_trigger is None:
            warning("Missing trigger entry for \"Grace\"")
            return

        if self.bot.user.mentioned_in(message) and not message.content.startswith('<@!'):
            # Note: the trigger needs to have a None-condition now that it's generic
            if self.get_message_sentiment_polarity(message) >= 0:
                await message.add_reaction(grace_trigger.positive_emoji)
                return
            await message.add_reaction(grace_trigger.negative_emoji)

    async def penguin_react(self, message: Message) -> None:
        """Checks to see if a message contains a reference to Linus (torvalds only), will be made more complicated
        as needed. If a linus reference is positively identified, Grace will react with a penguin emoji.
        I know using NLTK is kinda like bringing a tomahawk missile to a knife fight, but it may come in handy for
        future tasks, so the tokenizer object will be shared across all methods.

        :param message: A discord message to check for references to our lord and savior.
        :type message: discord.Message
        """
        linus_trigger = Trigger.get_by(name="Linus")
        if linus_trigger is None:
            warning("Missing trigger entry for \"Linus\"")
            return

        message_tokens = self.tokenizer.tokenize(message.content)
        tokenlist = list(map(lambda s: s.lower(), message_tokens))
        linustarget = [i for i, x in enumerate(
            tokenlist) if x in linus_trigger.words]
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

                determined_sentiment_polarity = self.get_message_sentiment_polarity(message)

                if not fail and determined_sentiment_polarity < 0:
                    await message.add_reaction(linus_trigger.negative_emoji)
                    return

                fail = (determined_sentiment_polarity < 1)

            if not fail:
                await message.add_reaction(linus_trigger.positive_emoji)

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        """A listener function that calls the `penguin_react`, `name_react`, and `pun_react` functions when a message
        is received.
         
         :param message: The message that was received.
         :type message: discord.Message
         """
        await self.penguin_react(message)
        await self.name_react(message)

    @hybrid_group(name="triggers", help="Commands to manage triggers")
    @has_permissions(administrator=True)
    async def triggers_group(self, ctx) -> None:
        """A command group that allows administrators to manage trigger words.

        :param ctx: The context in which the command was called.
        :type ctx: discord.ext.commands.Context
        """
        if ctx.invoked_subcommand is None:
            trigger = Trigger.get_by(name="Linus")
            if trigger is None:
                warning("Missing trigger entry for \"Linus\"")
                return

            embed = Embed(
                color=self.bot.default_color,
                title=f"Triggers",
                description="\n".join(trigger.words)
            )

            await ctx.send(embed=embed)

    @triggers_group.command(name="add", help="Add a trigger word", usage="{new_word}")
    @has_permissions(administrator=True)
    async def add_trigger_word(self, ctx: Context, new_word: str) -> None:
        """Add a new trigger word.

        :param ctx: The context in which the command was called.
        :type ctx: discord.ext.commands.Context
        :param new_word: The new trigger word to be added.
        :type new_word: str
        """
        trigger = Trigger.get_by(name="Linus")

        if trigger:
            if new_word in trigger.words:
                await ctx.send(f"**{new_word}** is already a trigger")
            else:
                trigger.add_trigger_word(new_word)

                await ctx.send(f"Trigger **{new_word}** added successfully")
        else:
            await ctx.send(f"Unable to add **{new_word}**")

    @triggers_group.command(name="remove", help="Remove a trigger word", usage="{old_word}")
    @has_permissions(administrator=True)
    async def remove_trigger_word(self, ctx: Context, old_word: str) -> None:
        """Remove an existing trigger word.

        :param ctx: The context in which the command was called.
        :type ctx: discord.ext.commands.Context
        :param old_word: The trigger word to be removed.
        :type old_word: str
        """
        trigger = Trigger.get_by(name="Linus")

        if trigger:
            if old_word not in trigger.words:
                await ctx.send(f"**{old_word}** is not a trigger")
            else:
                trigger.remove_trigger_word(old_word)

                await ctx.send(f"Trigger **{old_word}** removed successfully")
        else:
            await ctx.send(f"Unable to remove **{old_word}**")


async def setup(bot):
    await bot.add_cog(LanguageCog(bot))
