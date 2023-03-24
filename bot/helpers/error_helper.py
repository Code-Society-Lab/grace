from discord import Embed, Color, DiscordException


async def send_error(ctx, error_description, **kwargs):
    embed = Embed(
        title="Oops! An error occurred",
        color=Color.red(),
        description=error_description
    )

    for key, value in kwargs.items():
        embed.add_field(name=key.capitalize(), value=value)

    await ctx.send(embed=embed, ephemeral=True)


async def send_command_error(ctx, error_description, command, argument_example=None):
    await send_error(ctx, error_description, example=f"```/{command} {argument_example}```")


# This might be the right place for this function
def get_original_exception(error: DiscordException) -> Exception:
    while hasattr(error, 'original'):
        error = error.original
    return error
