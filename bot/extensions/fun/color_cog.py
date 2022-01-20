import os
from PIL import Image
from discord.ext.commands import Cog, command, group
from bot.extensions.utils.command_error_handler import CommandErrorHandler
from discord import Embed, File


class ColorCog(Cog, name="Color", description="Collection of commands to display colors."):
    def __init__(self, bot):
        self.bot = bot

    @group(name="show color", aliases=["color"], help="Commands to display colors.")
    async def color_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await CommandErrorHandler.send_command_help(ctx)

    async def display_color(self, color_img, ctx):
        color_img.save('color.png')

        embed = Embed(
            color=self.bot.default_color,
            description='Here goes your color!'
        )
        file = File('color.png')
        await ctx.send(embed=embed, file=file)

        os.remove('color.png')

    @color_group.command(name='rgb', help="Displays the RGB color entered by the user.")
    async def rgb_command(self, ctx, r: int, g: int, b: int):
        img = Image.new('RGB', (200, 200), (r, g, b))

        await self.display_color(img, ctx)

    @color_group.command(name='hex', help="Displays the color of the hexcode entered by the user.")
    async def hex_command(self, ctx, hex: str):
        if not hex.startswith('#'):
            hex = '#' + hex

        img = Image.new('RGB', (200, 200), hex)

        await self.display_color(img, ctx)


def setup(bot):
    bot.add_cog(ColorCog(bot))
