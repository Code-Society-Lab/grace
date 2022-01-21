import os
from PIL import Image
from discord.ext.commands import Cog, command, group
from bot.extensions.utils.command_error_handler import CommandErrorHandler
from discord import Embed, File


class ColorCog(Cog, name="Color", description="Collection of commands to for colors."):
    def __init__(self, bot):
        self.bot = bot

    @group(name="color", help="Commands to bring color in your life")
    async def color_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await CommandErrorHandler.send_command_help(ctx)

    @color_group.group(name="show", help="Commands to display colors.")
    async def show_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await CommandErrorHandler.send_command_help(ctx)

    async def display_color(self, ctx, color):
        colored_image = Image.new('RGB', (200, 200), color)
        colored_image.save('color.png')
        file = File('color.png')

        embed = Embed(
            color=self.bot.default_color,
            title='Here goes your color!',
            description=f"{color}"
        )
        embed.set_image(url="attachment://color.png")

        await ctx.send(embed=embed, file=file)
        os.remove('color.png')

    @show_group.command(
        name='rgb',
        help="Displays the RGB color entered by the user.",
        usage="color show rgb {red integer} {green integer} {blue integer}"
    )
    async def rgb_command(self, ctx, r: int, g: int, b: int):
        await self.display_color(ctx, (r, g, b))

    @show_group.command(
        name='hex',
        help="Displays the color of the hexcode entered by the user.",
        usage="color hex {hexadecimal string}"
    )
    async def hex_command(self, ctx, hex: str):
        if not hex.startswith('#'):
            hex = f'#{hex}'

        await self.display_color(ctx, hex)


def setup(bot):
    bot.add_cog(ColorCog(bot))
