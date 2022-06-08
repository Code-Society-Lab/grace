from discord import Embed
from discord.ext.commands import Cog, has_permissions, ExtensionAlreadyLoaded, ExtensionNotLoaded, group
from emoji import emojize
from bot.classes.state import State
from bot.extensions.command_error_handler import CommandErrorHandler
from bot.models.extension import Extension


class ExtensionCog(Cog, name="Extensions", description="Extensions managing cog"):
    def __init__(self, bot):
        self.bot = bot

    @group(name="extension", aliases=["ext", "e"], help="Commands to manage extensions")
    @has_permissions(administrator=True)
    async def extension_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await CommandErrorHandler.send_command_help(ctx)

    @extension_group.command(name="list", aliases=["l"], help="Display the list of extensions")
    @has_permissions(administrator=True)
    async def list_extensions_command(self, ctx):
        extensions = Extension.all()

        embed = Embed(
            color=self.bot.default_color,
            title="Extensions"
        )

        for extension in extensions:
            state_emoji = emojize(':green_circle:') if extension.is_enabled() else emojize(':red_circle:')

            embed.add_field(
                name=f"{state_emoji} {extension.name}",
                value=f"**State**: {extension.state}",
                inline=False
            )

        if not extensions:
            embed.description = "No extension found"

        await ctx.send(embed=embed)

    @extension_group.command(name="enable", aliases=["e"], help="Enable a given extension", usage="{extension_id}")
    @has_permissions(administrator=True)
    async def enable_extension_command(self, ctx, extension_name):
        extension = Extension.where(name=extension_name).first()

        if extension:
            try:
                self.bot.load_extension(extension.module)
                extension.state = State.ENABLED

                extension.save()
                await ctx.send(f"**{extension.name}** enabled.")
            except ExtensionAlreadyLoaded:
                await ctx.send(f"**{extension.name}** already enabled")
        else:
            await ctx.send(f"Extension **{extension_name}** not found")

    @extension_group.command(name="disable", aliases=["d"], help="Disable a given extension", usage="{extension_id}")
    @has_permissions(administrator=True)
    async def disable_extension_command(self, ctx, extension_name):
        extension = Extension.where(name=extension_name).first()

        if extension:
            try:
                self.bot.unload_extension(extension.module)
                extension.state = State.DISABLED

                extension.save()
                await ctx.send(f"**{extension.name}** disabled.")
            except ExtensionNotLoaded:
                await ctx.send(f"**{extension.name}** already disabled")
        else:
            await ctx.send(f"Extension **{extension_name}** not found")


def setup(bot):
    bot.add_cog(ExtensionCog(bot))

