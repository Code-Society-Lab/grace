from discord.ext.commands import Cog, has_permissions, hybrid_command, hybrid_group, Context
from discord import Message, Embed
from bot.models.bot import BotSettings
from bot.models.extensions.language.pun import Pun
from bot.models.extensions.language.pun_word import PunWord
from nltk.tokenize import TweetTokenizer
from emoji import demojize


class PunCog(Cog, name="Puns", description="Automatically intrude with puns when triggered"):
    def __init__(self, bot):
        self.bot = bot

        self.tokenizer = TweetTokenizer()
    
    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        """A listener function that calls the `pun_react` functions when a message is received.
         
         :param message: The message that was received.
         :type message: discord.Message
         """
        await self.pun_react(message)
   
    async def pun_react(self, message: Message) -> None:
        """Add reactions and send a message in the channel if the message content contains any pun words.

        :param message: The message to be checked for pun words.
        :type message: discord.Message
        """
        if message.author == self.bot.user:
            return

        message_tokens = self.tokenizer.tokenize(message.content)
        tokenlist = set(map(str.lower, message_tokens))

        pun_words = PunWord.all()
        word_set = set(map(lambda pun_word: pun_word.word, pun_words))

        matches = tokenlist.intersection(word_set)
        invoked_at = message.created_at.replace(tzinfo=None)

        if matches:
            matched_pun_words = set(filter(lambda pun_word: pun_word.word in matches, pun_words))
            puns = map(lambda pun_word: Pun.get(pun_word.pun_id), matched_pun_words)
            puns = filter(lambda pun: pun.can_invoke_at_time(invoked_at), puns)
            puns = set(puns) # remove duplicate puns

            for pun_word in matched_pun_words:
                await message.add_reaction(pun_word.emoji())

            for pun in puns:
                embed = Embed(
                    color=self.bot.default_color,
                    title=f"Gotcha",
                    description=pun.text
                )

                await message.channel.send(embed=embed)
                pun.save_last_invoked(invoked_at)

    @hybrid_group(name="puns", help="Commands to manage puns")
    @has_permissions(administrator=True)
    async def puns_group(self, ctx: Context) -> None:
        """A command group that allows administrators to manage puns words.

        :param ctx: The context in which the command was called.
        :type ctx: discord.ext.commands.Context
        """

    @puns_group.command(name="list", help="List all puns")
    @has_permissions(administrator=True)
    async def list_puns(self, ctx: Context) -> None:
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
    @has_permissions(administrator=True)
    async def add_pun(self, ctx: Context, pun_text: str) -> None:
        """Add a new pun word.

        :param ctx: The context in which the command was called.
        :type ctx: discord.ext.commands.Context
        :param pun_text: The new pun word to be added.
        :type pun_text: str
        """
        Pun.create(text=pun_text)

        await ctx.send("Pun added.")

    @puns_group.command(name="remove", help="Remove a pun", usage="{pun_id}")
    @has_permissions(administrator=True)
    async def remove_pun(self, ctx: Context, pun_id: int) -> None:
        """Remove an old pun word.

        :param ctx: The context in which the command was called.
        :type ctx: discord.ext.commands.Context
        :param pun_id: The ID of the pun to which the word will be removed.
        :type pun_id: str
        """
        pun = Pun.get(pun_id)

        if pun:
            await ctx.send("Pun removed.")
        else:
            await ctx.send(f"Pun with id **{pun.id}** does not exist.")

    @puns_group.command(name="add-word", help="Add a pun word to a pun")
    @has_permissions(administrator=True)
    async def add_pun_word(self, ctx: Context, pun_id: int, pun_word: str, emoji: str) -> None:
        """Add a new pun word.

        :param ctx: The context in which the command was called.
        :type ctx: discord.ext.commands.Context
        :param pun_id: The ID of the pun to which the word will be added.
        :type pun_id: int
        :param pun_word: The new pun word to be added.
        :type pun_word: str
        :param emoji: An emoji to be associated with the pun word.
        :type emoji: str
        """
        pun = Pun.get(pun_id)

        if pun:
            if pun.has_word(pun_word):
                await ctx.send(f"Pun word **{pun_word}** already exists.")
            else:
                pun.add_pun_word(pun_word, demojize(emoji))
                await ctx.send("Pun word added.")
        else:
            await ctx.send(f"Pun with id {pun.id} does not exist.")

    @puns_group.command(name="remove-word", help="Remove a pun from a pun word")
    @has_permissions(administrator=True)
    async def remove_pun_word(self, ctx: Context, id: int, pun_word: str) -> None:
        """Remove a new pun word.

        :param ctx: The context in which the command was called.
        :type ctx: discord.ext.commands.Context
        :param id: The ID of the pun to which the word will be removed.
        :type id: int
        :param pun_word: The old pun word to be removed.
        :type pun_word: str
        """
        pun = Pun.get(id)

        if pun:
            if not pun.has_word(pun_word):
                await ctx.send(f"Pun word **{pun_word}** does not exist.")
            else:
                pun.remove_pun_word(pun_word)
                await ctx.send("Pun word removed.")
        else:
            await ctx.send(f"Pun with id **{pun.id}** does not exist.")

    @hybrid_command(name="cooldown", help="Set cooldown for puns feature in minutes.")
    async def set_puns_cooldown_command(self, ctx: Context, cooldown_minutes: int) -> None:
        settings = BotSettings.settings()
        settings.puns_cooldown = cooldown_minutes
        settings.save()

        await ctx.send(f"Updated cooldown to {cooldown_minutes} minutes.")


async def setup(bot):
    await bot.add_cog(PunCog(bot))