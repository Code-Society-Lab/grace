from json import loads
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import Cog, cooldown, hybrid_group, Context
from discord import Embed, Colour
from requests import get
from random import choice as random_choice
from bot.extensions.command_error_handler import CommandErrorHandler
from bot.models.extensions.fun.answer import Answer


class FunCog(Cog, name="Fun", description="Collection of fun commands"):
    """A cog containing fun commands."""
    def __init__(self, bot):
        self.bot = bot
        self.goosed_gif_links = [
            'https://media.tenor.com/XG_ZOTYukysAAAAC/goose.gif',
            'https://media.tenor.com/pSnSQRfiIP8AAAAd/birds-kid.gif',
            'https://media.tenor.com/GDkgAup55_0AAAAC/duck-bite.gif'
        ]

    @hybrid_group(name="fun", help="Fun commands")
    async def fun_group(self, ctx: Context) -> None:
        """Group of fun commands.
        
        :param ctx: The context in which the command was called.
        :type ctx: Context
        """
        if ctx.invoked_subcommand is None:
            await CommandErrorHandler.send_command_help(ctx)

    @fun_group.command(name='eightball', aliases=['8ball'], help="Ask a question and be answered.", usage="{question}")
    @cooldown(4, 30, BucketType.user)
    async def eightball_command(self, ctx: Context, question: str) -> None:
        """Ask a question and get an answer.
        
        :param ctx: The context in which the command was called.
        :type ctx: Context
        :param question: The question asked by the user.
        :type question: str
        """
        if question:
            answer = random_choice(Answer.all())
        else:
            answer = "You need to ask me a question!"

        answer_embed = Embed(
            title=f'{ctx.author.name}, Grace says: ',
            color=self.bot.default_color,
            description=answer.answer,
        )

        await ctx.send(embed=answer_embed)

    @fun_group.command(name='goosed', help='Go goose yourself')
    async def goose_command(self, ctx: Context) -> None:
        """Send a Goose image.
        
        :param ctx: The context in which the command was called.
        :type ctx: Context
        """
        goosed_embed = Embed(
            color=self.bot.default_color,
            title='**GET GOOSED**',
        )
        goosed_embed.set_image(url=random_choice(self.goosed_gif_links))
        await ctx.send(embed=goosed_embed)

    @fun_group.command(name='quote', help='Sends an inspirational quote')
    async def quote_command(self, ctx: Context) -> None:
        """Generate a random inspirational quote.
        
        :param ctx: The context in which the command was called.
        :type ctx: Context
        """
        response = get('https://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=en')

        if response.ok:
            quote = '{quoteText} \n-- {quoteAuthor}'.format(**loads(response.text))

            embed = Embed(
                color=self.bot.default_color,
                description=quote,
            )

            await ctx.send(embed=embed)
        else:
            await ctx.send("Unable to fetch a quote! Try again later.")


async def setup(bot):
    await bot.add_cog(FunCog(bot))
