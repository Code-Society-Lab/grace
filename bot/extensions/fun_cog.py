from json import loads
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import Cog, cooldown, hybrid_group
from discord import Embed
from requests import get
import random
from bot.extensions.command_error_handler import CommandErrorHandler
from bot.models.extensions.fun.answer import Answer
from discord.colour import Colour


class FunCog(Cog, name="Fun", description="Collection of fun commands"):
    def __init__(self, bot):
        self.bot = bot

    @hybrid_group(name="fun", help="Fun commands")
    async def fun_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await CommandErrorHandler.send_command_help(ctx)

    @fun_group.command(name='eightball', aliases=['8ball'], help="Ask a question and be answered.", usage="{question}")
    @cooldown(4, 30, BucketType.user)
    async def eightball_command(self, ctx, question):
        if question:
            answer = random.choice(Answer.all())
        else:
            answer = "You need to ask me a question!"

        answer_embed = Embed(
            title=f'{ctx.author.name}, Grace says: ',
            color=self.bot.default_color,
            description=answer.answer,
        )

        await ctx.send(embed=answer_embed)

    @fun_group.command(name='quote', help='Sends an inspirational quote')
    async def quote_command(self, ctx):
        response = get('https://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=en')
        quote = '{quoteText} \n-- {quoteAuthor}'.format(**loads(response.text))

        embed = Embed(
            color=self.bot.default_color,
            description=quote,
        )

        await ctx.send(embed=embed)

    @fun_group.command(name='bisonquote', help='Sends a quote from SoyBison\'s quote server.')
    async def bisonquote_command(self, ctx):
        response = get('https://quotes.needell.co/quote')
        
        quote = response.text[1:-2].replace("\\n", "\n").replace("\\t", "    ").split('~')
        name = quote[1].strip().split('(')[0].strip()
        urlname = name.replace(" ", "_")
        
        true_author = None
        if '(' in quote[1]:
            true_author = quote[1].strip().split('(')[-1][:-1]

        embed = Embed(
            color=Colour.random(),
            description=quote[0],
        )
        embed.set_author(name=name, icon_url=f'https://quotes.needell.co/get_image?name={urlname}')
        if true_author:
            embed.set_footer(text=true_author)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(FunCog(bot))
