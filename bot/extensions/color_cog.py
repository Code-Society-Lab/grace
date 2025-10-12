import os
from PIL import Image
from discord.ext.commands import (
    Cog,
    hybrid_group,
    HybridCommandError,
    CommandInvokeError,
    Context,
)
from discord import Embed, File, Color
from bot.helpers.error_helper import send_command_error
from typing import Union, Tuple


def get_embed_color(color: Union[Tuple[int, int, int], str]) -> Color:
    """Convert a color to an Embed Color object.

    :param color: A tuple of 3 integers in the range 0-255 representing an RGB
                  color, or a string in the format '#RRGGBB' representing a
                  hexadecimal color.
    :type color: Union[Tuple[int, int, int], str]
    :return: An Embed Color object representing the input color.
    :rtype: Color
    """
    if isinstance(color, tuple):
        return Color.from_rgb(*color)
    return Color.from_str(color)


class ColorCog(
    Cog, name="Color", description="Collection of commands to bring color in your life."
):
    """A Discord Cog that provides a set of commands to display colors."""

    def __init__(self, bot):
        self.bot = bot

    @hybrid_group(name="color", help="Commands to bring color in your life")
    async def color_group(self, ctx: Context) -> None:
        """Group command for the color commands. If called without a subcommand,
        it sends the help message.

        :param ctx: The context of the command invocation.
        :type ctx: Context
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @color_group.group(name="show", help="Commands to display colors.")
    async def show_group(self, ctx: Context) -> None:
        """Group command for the show subcommands. If called without a subcommand,
        it sends the help message.

        :param ctx: The context of the command invocation.
        :type ctx: Context
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    async def display_color(
        self, ctx: Context, color: Union[Tuple[int, int, int], str]
    ) -> None:
        """Display a color in an embed message.

        :param ctx: The context of the command invocation.
        :type ctx: Context
        :param color: A tuple of 3 integers in the range 0-255 representing an
                      RGB color, or a string in the format '#RRGGBB' representing
                      a hexadecimal color.
        :type color: Union[Tuple[int, int, int], str]
        """
        colored_image = Image.new("RGB", (200, 200), color)
        colored_image.save("color.png")
        file = File("color.png")

        embed = Embed(
            color=get_embed_color(color),
            title="Here goes your color!",
            description=f"{color}",
        )
        embed.set_image(url="attachment://color.png")

        await ctx.send(embed=embed, file=file)
        os.remove("color.png")

    @show_group.command(
        name="rgb",
        help="Displays the RGB color entered by the user.",
        usage="color show rgb {red integer} {green integer} {blue integer}",
    )
    async def rgb_command(self, ctx: Context, r: int, g: int, b: int) -> None:
        """Display an RGB color in an embed message.

        :param ctx: The context of the command invocation.
        :type ctx: Context
        :param r: The red component of the color (0-255).
        :type r: int
        :param g: The green component of the color (0-255).
        :type g: int
        :param b: The blue component of the color (0-255).
        :type b: int
        """
        await self.display_color(ctx, (r, g, b))

    @rgb_command.error
    async def rgb_command_error(self, ctx: Context, error: Exception) -> None:
        """Event listener for errors that occurred during the execution of the
        'rgb' command. It sends an error message to the user.

        :param ctx: The context of the command invocation.
        :type ctx: Context
        :param error: The error that was raised during command execution.
        :type error: Exception
        """
        if isinstance(error, HybridCommandError) or isinstance(
            error, CommandInvokeError
        ):
            await send_command_error(
                ctx, "Expected rgb color", ctx.command, "244 195 8"
            )

    @show_group.command(
        name="hex",
        help="Displays the color of the hexcode entered by the user.",
        usage="color show hex {hexadecimal string}",
    )
    async def hex_command(self, ctx: Context, hex_code: str) -> None:
        """Display a color in an embed message using a hexadecimal color code.

        :param ctx: The context of the command invocation.
        :type ctx: Context
        :param hex_code: A string in the format '#RRGGBB' representing a hexadecimal color.
        :type hex_code: str
        """
        if not hex_code.startswith("#"):
            hex_code = f"#{hex_code}"
        await self.display_color(ctx, hex_code)

    @hex_command.error
    async def hex_command_error(self, ctx: Context, error: Exception) -> None:
        """Event listener for errors that occurred during the execution of the
        'hex' command. It sends an error message to the user.

        :param ctx: The context of the command invocation.
        :type ctx: Context
        :param error: The error that was raised during command execution.
        :type error: Exception
        """
        if isinstance(error, HybridCommandError) or isinstance(
            error, CommandInvokeError
        ):
            await send_command_error(
                ctx, "Expected hexadecimal color", ctx.command, "#F4C308"
            )


async def setup(bot):
    await bot.add_cog(ColorCog(bot))
