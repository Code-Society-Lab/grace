from discord import Color, Embed
from discord.ext import commands


class Help(commands.MinimalHelpCommand):
    async def send_pages(self):
        help_message = Embed(color=Color.blurple(), description='')
        destination = self.get_destination()

        for page in self.paginator.pages:
            help_message.description += page

        await destination.send(embed=help_message)

    async def send_command_help(self, ctx, command):
        help_message = Embed(color=Color.blurple(), description='')
        destination = ctx.channel

        help_message.description += f"{ctx.prefix}{command.name} {command.usage}\n\n{command.help}"

        await destination.send(embed=help_message)
