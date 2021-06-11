from discord import Embed
from discord.ext import commands

from bot import CONFIG
from bot.helpers.color_helper import get_color_digit


class Help(commands.MinimalHelpCommand):
    async def send_pages(self, ctx=None):
        help_message = Embed(
            color=get_color_digit(CONFIG.style.embed_color),
            title="Help",
            description=''
        )

        destination = ctx.channel if ctx else self.get_destination()

        for page in self.paginator.pages:
            help_message.description += page

        await destination.send(embed=help_message)

    async def send_command_help(self, command):
        help_message = Embed(
            color=get_color_digit(CONFIG.style.embed_color),
            title=f"Help for {self.clean_prefix}{command.name}",
            description=command.help
        )

        help_message.add_field(name="Usage", value=command.usage)

        help_message.set_footer(text=f"For more help enter {self.clean_prefix}help")

        await self.get_destination().send(embed=help_message)
