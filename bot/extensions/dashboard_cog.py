from datetime import datetime, tzinfo

import dachshund
from apscheduler.job import Job
from discord import Member, Message
from discord.ext.commands import Cog, Context
from pytz import timezone

from bot.grace import Grace

SUMMARY = """
# Welcome!
### This dashboard contain various monitoring information about **Grace**, our awesome bot!
Hopefully, you will find something useful here.

- [Website](https://codesociety.xyz)
- [Discord](https://discord.gg/FzgwHD7Am3)
- [Source](https://github.com/Code-Society-Lab/grace)
"""


class DashboardCog(
    Cog, name="Dashboard", description="Feeds bot telemetry to the live dashboard"
):
    """Feeds bot telemetry to the live dashboard"""

    def __init__(self, bot: Grace):
        self.bot: Grace = bot
        self.jobs: list[Job] = []
        self.timezone: tzinfo = timezone("US/Eastern")

    def cog_load(self) -> None:
        dachshund.emit("summary", value=SUMMARY)

        self.jobs.append(
            self.bot.scheduler.add_job(self._report_latency, "interval", minutes=1)
        )

    def cog_unload(self) -> None:
        for job in self.jobs:
            self.bot.scheduler.remove_job(job.id)

    def _report_latency(self) -> None:
        self.bot.metrics.record_latency(self.bot.latency_ms)

    def _report_member_count(self) -> None:
        guild_id = self.bot.app.config.get("client", "guild_id")

        if guild := self.bot.get_guild(guild_id):
            dachshund.emit("member_count", value=guild.member_count)

    @Cog.listener()
    async def on_ready(self) -> None:
        self._report_member_count()
        dachshund.emit("members")

    @Cog.listener()
    async def on_member_join(self, _member: Member) -> None:
        self._report_member_count()
        dachshund.emit("members")

    @Cog.listener()
    async def on_member_remove(self, _member: Member) -> None:
        self._report_member_count()
        dachshund.emit("members")

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        dachshund.emit(
            "message",
            date=datetime.now(self.timezone).date().isoformat(),
            author=None if message.author.bot else str(message.author.id),
            value=1,
        )

    @Cog.listener()
    async def on_command(self, ctx: Context) -> None:
        if ctx.command:
            dachshund.emit("on_command", name=ctx.command.qualified_name, value=1)

    @Cog.listener()
    async def on_command_error(self, ctx: Context, error: Exception) -> None:
        name = ctx.command.qualified_name if ctx.command else "unknown"
        dachshund.emit("command_error", name=name, value=1)

    @Cog.listener()
    async def on_disconnect(self) -> None:
        dachshund.emit("connection_event", type="disconnect", value=1)

    @Cog.listener()
    async def on_resumed(self) -> None:
        dachshund.emit("connection_event", type="resume", value=1)


async def setup(bot: Grace) -> None:
    await bot.add_cog(DashboardCog(bot))
