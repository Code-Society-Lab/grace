from discord import Embed
from discord.ext.commands import Cog, has_permissions, ExtensionAlreadyLoaded, ExtensionNotLoaded, group
from bot.extensions.utils.command_error_handler import CommandErrorHandler
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
            title="Extensions status"
        )

        for extension in extensions:
            embed.add_field(
                name=f"{extension.id} | {extension.name}",
                value=f"**State**: {extension.state} | **Module**: {extension.module}",
            )

        if not extensions:
            embed.description = "No extension found"

        await ctx.send(embed=embed)

    @extension_group.command(name="enable", aliases=["e"], help="Enable a given extension", usage="{extension_id}")
    @has_permissions(administrator=True)
    async def enable_extension_command(self, ctx, extension_id):
        extension = Extension.get(extension_id)

        if extension:
            try:
                self.bot.load_extension(extension.module)
                extension.state = 1

                extension.save()
                await ctx.send(f"**{extension.name}** enabled.")
            except ExtensionAlreadyLoaded:
                await ctx.send(f"**{extension.name}** already enabled")
        else:
            await ctx.send(f"Extension no. {extension_id} not found")

    @extension_group.command(name="disable", aliases=["d"], help="Disable a given extension", usage="{extension_id}")
    @has_permissions(administrator=True)
    async def disable_extension_command(self, ctx, extension_id):
        extension = Extension.get(extension_id)

        if extension:
            try:
                self.bot.unload_extension(extension.module)
                extension.state = 0

                extension.save()
                await ctx.send(f"**{extension.name}** disabled.")
            except ExtensionNotLoaded:
                await ctx.send(f"**{extension.name}** already disabled")
        else:
            await ctx.send(f"Extension {extension_id} not found")


def setup(bot):
    bot.add_cog(ExtensionCog(bot))

