import traceback
from typing import Optional
from logging import info
from pytz import timezone
from discord import Interaction, Embed, TextStyle
from discord.app_commands import Choice, autocomplete
from discord.ui import Modal, TextInput
from discord.ext.commands import Cog, has_permissions, hybrid_command, hybrid_group, Context 
from bot.models.extensions.thread import Thread
from bot.classes.recurrence import Recurrence
from bot.extensions.command_error_handler import send_command_help
from lib.config_required import cog_config_required


class ThreadModal(Modal, title="Thread"):
    thread_title = TextInput(
        label="Title",
        placeholder="The title of the thread...",
        min_length=5,
        max_length=100,
    )

    thread_content = TextInput(
        label="Content",
        placeholder="The content of the thread...",
        min_length=10,
        style=TextStyle.paragraph
    )

    def __init__(self, recurrence: Recurrence, thread: Thread = None):
        super().__init__()

        if thread:
            self.thread_title.default = thread.title
            self.thread_content.default = thread.content

        self.thread = thread
        self.thread_recurrence = recurrence

    async def on_submit(self, interaction: Interaction):
        if self.thread:
            await self.update_thread(interaction)
        else:
            await self.create_thread(interaction)

    async def create_thread(self, interaction: Interaction):
        thread = Thread.create(
            title=self.thread_title.value,
            content=self.thread_content.value,
            recurrence=self.thread_recurrence
        )
        await interaction.response.send_message(
            f'Thread __**{thread.id}**__ created!',
            ephemeral=True
        )

    async def update_thread(self, interaction: Interaction):
        self.thread.title = self.thread_title.value,
        self.thread.content = self.thread_content.value,
        self.thread.recurrence = self.thread_recurrence

        self.thread.save()

        await interaction.response.send_message(
            f'Thread __**{self.thread.id}**__ updated!',
            ephemeral=True
        )

    async def on_error(self, interaction: Interaction, error: Exception):
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)
        traceback.print_exception(type(error), error, error.__traceback__)


async def thread_autocomplete(_: Interaction, current: str) -> list[Choice[str]]:
    return [
        Choice(name=t.title, value=str(t.id))
        for t in Thread.all() if current.lower() in t.title
    ]


@cog_config_required("threads", "channel_id")
class ThreadsCog(Cog, name="Threads"):
    def __init__(self, bot):
        self.bot = bot
        self.jobs = []
        self.threads_channel_id = self.required_config
        self.timezone = timezone("US/Eastern")


    def cog_load(self):
        # Runs everyday at 18:30
        self.jobs.append(self.bot.scheduler.add_job(
            self.daily_post,
            'cron',
            hour=18,
            minute=30,
            timezone=self.timezone
        ))

        # Runs every monday at 18:30
        self.jobs.append(self.bot.scheduler.add_job(
            self.weekly_post,
            'cron',
            day_of_week='mon',
            hour=18,
            minute=30,
            timezone=self.timezone
        ))

        # Runs on the 1st of every month at 18:30
        self.jobs.append(self.bot.scheduler.add_job(
            self.monthly_post,
            'cron',
            day=1,
            hour=18,
            minute=30,
            timezone=self.timezone
        ))

    def cog_unload(self):
        for job in self.jobs:
            self.bot.scheduler.remove_job(job.id)

    async def daily_post(self):
        info("Posting daily threads")

        for thread in Thread.find_by_recurrence(Recurrence.DAILY):
            await self.post_thread(thread)

    async def weekly_post(self):
        info("Posting weekly threads")

        for thread in Thread.find_by_recurrence(Recurrence.WEEKLY):
            await self.post_thread(thread)

    async def monthly_post(self):
        info("Posting monthly threads")

        for thread in Thread.find_by_recurrence(Recurrence.MONTHLY):
            await self.post_thread(thread)

    async def post_thread(self, thread: Thread):
        channel = self.bot.get_channel(self.threads_channel_id)
        role_id = self.bot.app.config.get("threads", "role_id")
        content = f"<@&{role_id}>" if role_id else None

        embed = Embed(
            color=self.bot.default_color,
            title=thread.title,
            description=thread.content
        )

        if channel:
            message = await channel.send(content=content, embed=embed)
            await message.create_thread(name=thread.title)

    @hybrid_group(name="threads", help="Commands to manage threads")
    @has_permissions(administrator=True)
    async def threads_group(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await send_command_help(ctx)

    @threads_group.command(help="List all threads")
    @has_permissions(administrator=True)
    async def list(self, ctx: Context):
        embed = Embed(
            color=self.bot.default_color,
            title="Threads"
        )

        if threads := Thread.all():
            for thread in threads:
                embed.add_field(
                    name=f"[{thread.id}] {thread.title}",
                    value=f"**Recurrence**: {thread.recurrence}",
                    inline=False
                )
        else:
            embed.add_field(name="No threads", value="")

        await ctx.send(embed=embed, ephemeral=True)

    @threads_group.command(help="Creates a new thread")
    @has_permissions(administrator=True)
    async def create(self, ctx: Context, recurrence: Recurrence):
        modal = ThreadModal(recurrence)
        await ctx.interaction.response.send_modal(modal)

    @threads_group.command(help="Deletes a given thread")
    @has_permissions(administrator=True)
    @autocomplete(thread=thread_autocomplete)
    async def delete(self, ctx: Context, thread: int):
        if thread := Thread.get(thread):
            thread.delete()
            await ctx.send("Thread successfully deleted!", ephemeral=True)
        else:
            await ctx.send("Thread not found!", ephemeral=True)

    @threads_group.command(help="Update a thread")
    @has_permissions(administrator=True)
    @autocomplete(thread=thread_autocomplete)
    async def update(self, ctx: Context, thread: int, recurrence: Recurrence):
        if thread := Thread.get(thread):
            modal = ThreadModal(recurrence, thread=thread)
            await ctx.interaction.response.send_modal(modal)
        else:
            await ctx.send("Thread not found!", ephemeral=True)


    @threads_group.command(help="Post a given thread")
    @has_permissions(administrator=True)
    @autocomplete(thread=thread_autocomplete)
    async def post(self, ctx: Context, thread: int):
        if ctx.interaction:
            await ctx.interaction.response.send_message(
                content="Opening thread!",
                delete_after=0,
                ephemeral=True
            )

        if thread := Thread.get(thread):
            await self.post_thread(thread)
        else:
            await self.send("Thread not found!")


async def setup(bot):
    await bot.add_cog(ThreadsCog(bot))
