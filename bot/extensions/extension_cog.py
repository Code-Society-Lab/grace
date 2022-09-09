from discord import Embed
from discord.app_commands import Choice, autocomplete
from discord.ext.commands import Cog, has_permissions, ExtensionAlreadyLoaded, ExtensionNotLoaded, hybrid_group
from emoji import emojize
from bot.classes.state import State
from bot.extensions.command_error_handler import CommandErrorHandler
from bot.models.extension import Extension


def extension_autocomplete(state):
    async def inner_autocomplete(_, current):
        def create_choice(extension):
            state_emoji = emojize(':green_circle:') if extension.is_enabled() else emojize(':red_circle:')
            return Choice(name=f"{state_emoji} {extension.name}", value=extension.module_name)
        return list(map(create_choice, Extension.by_state(state).filter(Extension.module_name.ilike(f"%{current}%"))))
    return inner_autocomplete


class ExtensionCog(Cog, name="Extensions", description="Extensions managing cog"):
    def __init__(self, bot):
        self.bot = bot

    @hybrid_group(name="extension", aliases=["ext", "e"], help="Commands to manage extensions")
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

        await ctx.send(embed=embed, ephemeral=True)

    @extension_group.command(name="enable", aliases=["e"], help="Enable a given extension", usage="{extension_id}")
    @has_permissions(administrator=True)
    @autocomplete(extension_name=extension_autocomplete(State.DISABLED))
    async def enable_extension_command(self, ctx, extension_name):
        extension = Extension.get_by(module_name=extension_name)

        if extension:
            try:
                await self.bot.load_extension(extension.module.name)
                extension.state = State.ENABLED

                extension.save()
                await ctx.send(f"**{extension.name}** enabled.", ephemeral=True)
            except ExtensionAlreadyLoaded:
                await ctx.send(f"**{extension.name}** already enabled", ephemeral=True)
        else:
            await ctx.send(f"Extension **{extension_name}** not found", ephemeral=True)

    @extension_group.command(name="disable", aliases=["d"], help="Disable a given extension", usage="{extension_id}")
    @has_permissions(administrator=True)
    @autocomplete(extension_name=extension_autocomplete(State.ENABLED))
    async def disable_extension_command(self, ctx, extension_name):
        extension = Extension.get_by(module_name=extension_name)

        if extension:
            try:
                await self.bot.unload_extension(extension.module.name)
                extension.state = State.DISABLED

                extension.save()
                await ctx.send(f"**{extension.name}** disabled.", ephemeral=True)
            except ExtensionNotLoaded:
                await ctx.send(f"**{extension.name}** already disabled", ephemeral=True)
        else:
            await ctx.send(f"Extension **{extension_name}** not found", ephemeral=True)


async def setup(bot):
    await bot.add_cog(ExtensionCog(bot))

