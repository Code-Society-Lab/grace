import os
from PIL import Image
from discord.ext.commands import Cog, hybrid_group
from discord import Embed, File, Color
from bot.helpers.error_helper import send_command_error


def get_embed_color(color):
    if isinstance(color, tuple):
        return Color.from_rgb(*color)
    return Color.from_str(color)


class ColorCog(Cog, name="Color", description="Collection of commands to bring color in your life."):
    def __init__(self, bot):
        self.bot = bot

    @hybrid_group(name="color", help="Commands to bring color in your life")
    async def color_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @color_group.group(name="show", help="Commands to display colors.")
    async def show_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    async def display_color(self, ctx, color):
        colored_image = Image.new('RGB', (200, 200), color)
        colored_image.save('color.png')
        file = File('color.png')

        embed = Embed(
            color=get_embed_color(color),
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

    @rgb_command.error
    async def rgb_command_error(self, ctx, error):
        if isinstance(error.original, ValueError):
            await send_command_error(ctx, "Expected rgb color", ctx.command, "244 195 8")

    @show_group.command(
        name='hex',
        help="Displays the color of the hexcode entered by the user.",
        usage="color show hex {hexadecimal string}"
    )
    async def hex_command(self, ctx, hex_code: str):
        if not hex_code.startswith('#'):
            hex_code = f'#{hex_code}'
        await self.display_color(ctx, hex_code)

    @hex_command.error
    async def hex_command_error(self, ctx, error):
        if isinstance(error.original, ValueError):
            await send_command_error(ctx, "Expected hexadecimal color", ctx.command, "#F4C308")


async def setup(bot):
    await bot.add_cog(ColorCog(bot))
