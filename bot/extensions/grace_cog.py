from discord import Embed
from discord.ext.commands import Cog, command, group, has_permissions
from emoji import emojize
from bot import app
from bot.extensions.utils.command_error_handler import CommandErrorHandler
from bot.models.extension import Extension


class GraceCog(Cog, name="Grace", description="Default grace commands"):
    def __init__(self, bot):
        self.bot = bot

    @command(name='info', help='Show information about the bot', usage=f'info')
    async def info_command(self, ctx):
        embed = Embed(
            color=self.bot.default_color,
            title=f"My name is Grace",
            description=f"Hi, {ctx.author.mention}. I'm the official **Code Society** Discord Bot.\n\u200b",
        )

        embed.add_field(
            name="Fun fact about me",
            value=f"I'm named after [Grace Hopper](https://en.wikipedia.org/wiki/Grace_Hopper) {emojize(':rabbit:')}"
                  "\n\u200b",
            inline=False
        )

        embed.add_field(
            name=f"{emojize(':test_tube:')} Code Society Lab",
            value=f"Contribute to our [projects](https://github.com/Code-Society-Lab/grace)\n\u200b",
            inline=True
        )

        embed.add_field(
            name=f"{emojize(':crossed_swords:')} Codewars",
            value=f"Set your clan to **CodeSoc**\n\u200b",
            inline=True
        )

        embed.set_footer(text=f"Need help? Send {self.bot.command_prefix}help")

        await ctx.send(embed=embed)

    @group(name="extension", aliases=["ext", "e"], help="Commands to manage extensions")
    @has_permissions(administrator=True)
    async def extension_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await CommandErrorHandler.send_command_help(ctx)

    @extension_group.command(name="list", aliases=["l"], help="Display the list of extensions")
    @has_permissions(administrator=True)
    async def list_extensions_command(self, ctx):
        extensions = app.session.query(Extension).all()

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
        extension = app.session.query(Extension).get(extension_id)

        if extension:
            self.bot.load_extension(extension.module)
            extension.state = 1

            extension.save()
            await ctx.send(f"**{extension.name}** enabled.")
        else:
            await ctx.send(f"Extension no. {extension_id} not found")

    @extension_group.command(name="disable", aliases=["d"], help="Disable a given extension", usage="{extension_id}")
    @has_permissions(administrator=True)
    async def disable_extension_command(self, ctx, extension_id):
        extension = app.session.query(Extension).get(extension_id)

        if extension:
            self.bot.remove_cog(extension.module)
            extension.state = 0

            extension.save()

            await ctx.send(f"**{extension.name} {extension.module}** disabled.")
        else:
            await ctx.send(f"Extension no. {extension_id} not found")


def setup(bot):
    bot.add_cog(GraceCog(bot))
