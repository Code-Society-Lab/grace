import re
import emoji
from discord.ext.commands import Cog, has_permissions, hybrid_group
from discord import Message, Embed
from nltk.tokenize import TweetTokenizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from bot.models.extensions.language.trigger import Trigger
from bot.models.extensions.language.pun import Pun
from bot.models.extensions.language.pun_word import PunWord


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

    async def name_react(self, message: Message):
        grace_trigger = Trigger.get_by(name="Grace")
        if self.bot.user.mentioned_in(message) and not message.content.startswith('<@!'):
            await message.add_reaction(grace_trigger.positive_emoji)

    async def penguin_react(self, message: Message):
        """
        Checks to see if a message contains a reference to Linus (torvalds only), will be made more complicated
        as needed. If a linus reference is positively identified, Grace will react with a penguin emoji.
        I know using NLTK is kinda like bringing a tomahawk missile to a knife fight, but it may come in handy for
        future tasks, so the tokenizer object will be shared across all methods.

        :param message: A discord message to check for references to our lord and savior.
        :return: None
        """
        linus_trigger = Trigger.get_by(name="Linus")

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

    async def pun_react(self, message: Message):
        message_tokens = self.tokenizer.tokenize(message.content)
        tokenlist = set(map(str.lower, message_tokens))

        pun_words = PunWord.all()
        word_set = set(map(lambda pun_word: pun_word.word, pun_words))

        matches = tokenlist.intersection(word_set)

        if len(matches) > 0:
            matched_pun_words = set(
                filter(lambda pun_word: pun_word.word in matches, pun_words))
            puns = set(map(lambda pun_word: Pun.get(
                pun_word.pun_id), matched_pun_words))

            for pun_word in matched_pun_words:
                await message.add_reaction(pun_word.emoji())

            for pun in puns:
                embed = Embed(
                    color=self.bot.default_color,
                    title=f"Gotcha",
                    description=pun.text
                )

                await message.channel.send(embed=embed)

    @Cog.listener()
    async def on_message(self, message):
        await self.penguin_react(message)
        await self.name_react(message)
        await self.pun_react(message)

    @hybrid_group(name="triggers", help="Commands to manage triggers")
    @has_permissions(administrator=True)
    async def triggers_group(self, ctx):
        if ctx.invoked_subcommand is None:
            trigger = Trigger.get_by(name="Linus")

            embed = Embed(
                color=self.bot.default_color,
                title=f"Triggers",
                description="\n".join(trigger.words)
            )

            await ctx.send(embed=embed)

    @triggers_group.command(name="add", help="Add a trigger word", usage="{new_word}")
    async def add_trigger_word(self, ctx, new_word):
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
    async def remove_trigger_word(self, ctx, old_word):
        trigger = Trigger.get_by(name="Linus")

        if trigger:
            if old_word not in trigger.words:
                await ctx.send(f"**{old_word}** is not a trigger")
            else:
                trigger.remove_trigger_word(old_word)

                await ctx.send(f"Trigger **{old_word}** removed successfully")
        else:
            await ctx.send(f"Unable to remove **{old_word}**")

    @hybrid_group(name="puns", help="Commands to manage puns")
    @has_permissions(administrator=True)
    async def puns_group(self, ctx):
        if ctx.invoked_subcommand is None:
            pun_texts_with_ids = map(lambda pun: '{}.\t{}'.format(
                pun.id, pun.text), Pun.all())

            embed = Embed(
                color=self.bot.default_color,
                title=f"Puns",
                description="\n".join(pun_texts_with_ids)
            )

            await ctx.send(embed=embed)

    @puns_group.command(name="add", help="Add a pun", usage="{pun_text}")
    async def add_pun(self, ctx, pun_text):
        # underlined words are pun words
        pun_word_matches = re.findall("__\S*__", pun_text)
        pun_words = list(map(lambda s: s.replace('__', ''), pun_word_matches))

        emojis = list(filter(emoji.is_emoji, pun_text))

        if len(pun_words) == 0:
            await ctx.send('No pun words provided!')
        elif len(emojis) == 0:
            await ctx.send('No emojis provided!')
        elif len(pun_words) != len(emojis):
            await ctx.send('Pun words not the same number as emojis!')
        else:
            pun_text_clean = pun_text.replace('_', '')
            pun_text_clean = ''.join(
                list(filter(lambda x: not emoji.is_emoji(x), pun_text_clean)))

            pun = Pun.create(text=pun_text_clean)

            for i, pun_word in enumerate(pun_words):
                PunWord.create(
                    pun_id=pun.id,
                    word=pun_word.lower(),
                    emoji_code=emoji.demojize(emojis[i])
                )

            await ctx.send("Pun added.")

    @puns_group.command(name="remove", help="Remove a pun", usage="{pun_id}")
    async def remove_pun(self, ctx, pun_id: int):
        pun = Pun.get_by(id=pun_id)

        if pun:
            for pun_word in pun.pun_words:
                pun_word.delete()

            pun.delete()

            await ctx.send("Pun removed.")
        else:
            await ctx.send("Could not remove pun.")


async def setup(bot):
    await bot.add_cog(LanguageCog(bot))
