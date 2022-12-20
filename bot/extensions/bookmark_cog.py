from enum import Enum
from typing import Dict, Union
from discord import (
    Member,
    Embed,
    RawReactionActionEvent,
    GroupChannel,
    DMChannel,
    Thread,
    TextChannel,
    Message
)
from discord.ext.commands import Cog, hybrid_group, Context
from bot.extensions.command_error_handler import send_command_help
from bot.grace import Grace

ChannelType = Union[TextChannel, Thread, DMChannel, GroupChannel]


class Mode(Enum):
    NORMAL = 0
    SAVE = 1


class BookmarkCog(Cog):
    def __init__(self, bot: Grace) -> None:
        self.bot = bot
        self.mode_by_user: Dict[Member, Mode] = {}

    @Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        if payload.member not in self.mode_by_user:
            return

        if self.mode_by_user[payload.member] == Mode.SAVE:
            if payload.emoji.name == '📖':
                channel: ChannelType = await self.bot.fetch_channel(payload.channel_id)
                message: Message = await channel.fetch_message(payload.message_id)

                print(message.content)
                save_embed: Embed = Embed(
                    color=self.bot.default_color,
                    title='Saved message',
                    description="Message sent by: **{author}**\nSent at: **{sent_at}**\nMessage: **{content}**".format(
                        author=message.author,
                        sent_at=message.created_at.strftime("%m/%d/%Y %H:%M:%S"),
                        content=message.content
                    )
                )
                await message.remove_reaction(payload.emoji, payload.member)
                await payload.member.send(embed=save_embed)

    @hybrid_group(name='bookmark')
    async def bookmark(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await send_command_help(ctx)

    @bookmark.command(name='save', description='Enters into a save mode where you can start saving messages')
    async def save_mode(self, ctx: Context):
        save_mode_embed: Embed = Embed(
            title='SAVE MODE',
            description='You have entered the **Save Mode**.\n'
                        'You can save messages by reacting with 📖 **emoji** on them\n'
                        'To **exit** the save mode, use this command: _/bookmark exit_',
            color=self.bot.default_color
        )

        self.mode_by_user[ctx.author] = Mode.SAVE

        await ctx.reply(embed=save_mode_embed, ephemeral=True)

    @bookmark.command(name='exit', description='Enters into a normal mode')
    async def save_mode(self, ctx: Context):
        normal_mode_embed: Embed = Embed(
            title='NORMAL MODE',
            description='You are back in the **Normal Mode**.',
            color=self.bot.default_color
        )
        self.mode_by_user[ctx.author] = Mode.NORMAL

        await ctx.reply(embed=normal_mode_embed, ephemeral=True)


async def setup(bot: Grace):
    await bot.add_cog(BookmarkCog(bot))
