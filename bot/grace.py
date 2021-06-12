from logging import info, warning, error, critical
from discord import Intents, Message
from discord.ext import commands
from bot import CONFIG
from bot.help import Help
from bot.helpers.color_helper import get_color_digit
from nltk.tokenize import TweetTokenizer


class Grace(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=CONFIG.bot.prefix,
            description="Grace is the official Code Society Discord bot.",
            help_command=Help(),
            intents=Intents.all()
        )

        # I know not everyone working here is familiar with NLTK so I'll explain some of the terminology.
        # Not to be confused with Auth Tokens, tokenization just means splitting the natural language
        # into discrete meaningful chunks, usually it's words, but words like "it's" or "ain't" will be
        # split into "it is" and "are not".
        # We're using the casual tokenizer for now, but it can be changed down the line so long as you're
        # aware of any new behaviors. https://www.nltk.org/api/nltk.tokenize.html

        self.tokenizer = TweetTokenizer()

    @property
    def default_color(self):
        return get_color_digit(CONFIG.style.embed_color)

    def load_extensions(self, extensions):
        for extension in extensions:
            info(f"Loading {extension}")
            self.load_extension(extension)

    async def on_ready(self):
        info(f"{self.user.name}#{self.user.id} is online and ready to use!")

    async def penguin_react(self, message: Message):
        """
        Checks to see if a message contains a reference to Linus (torvalds only), will be made more complicated
        as needed. If a linus reference is positively identified, Grace will react with a penguin emoji.
        I know using NLTK is kinda like bringing a tomahawk missile to a knife fight, but it may come in handy for
        future tasks, so the tokenizer object will be shared across all methods.

        :param message: A discord message to check for references to our lord and savior.
        :return: None
        """
        message_tokens = self.tokenizer.tokenize(message.content)
        tokenlist = map(lambda s: s.lower(), message_tokens)
        linustarget = [i for i, x in enumerate(tokenlist) if x == 'linus']
        # Get the indices of all linuses in the message

        if linustarget:
            fail = False
            for linusindex in linustarget:
                if message_tokens[linusindex + 1] == 'tech' and message_tokens[linusindex + 2] == 'tips':
                    fail = True
                elif message_tokens[linusindex + 1] == 'and' and message_tokens[linusindex + 2] == 'lucy':
                    fail = True

            if not fail:
                await message.add_reaction('🐧')

    async def on_message(self, message):
        await self.penguin_react(message)
