from datetime import datetime, tzinfo

import dachshund
from apscheduler.job import Job
from discord import Member, Message
from discord.ext.commands import Cog, Context
from pytz import timezone

from bot.grace import Grace
from bot.models.extensions.widget_state import WidgetState


class DashboardCog(
    Cog, name="Dashboard", description="Feeds bot telemetry to the live dashboard"
):
    """Feeds bot telemetry to the live dashboard"""

    def __init__(self, bot: Grace):
        self.bot: Grace = bot
        self.jobs: list[Job] = []
        self.timezone: tzinfo = timezone("US/Eastern")

        self._daily_message_count: int = 0
        self._minutely_message_count: int = 0
        self._minutely_command_count: int = 0

    def cog_load(self) -> None:
        self._load_counts()

        self.jobs.append(
            self.bot.scheduler.add_job(
                self._report_latency, "cron", minute="*/1", timezone=self.timezone
            )
        )
        self.jobs.append(
            self.bot.scheduler.add_job(
                self._save_counts, "cron", minute="*/1", timezone=self.timezone
            )
        )
        self.jobs.append(
            self.bot.scheduler.add_job(
                self._reset_daily_count,
                "cron",
                hour=0,
                minute=0,
                second=0,
                timezone=self.timezone,
            )
        )

    def cog_unload(self) -> None:
        for job in self.jobs:
            self.bot.scheduler.remove_job(job.id)

    def _report_latency(self) -> None:
        self.bot.metrics.record_latency(self.bot.latency_ms)

    def _load_counts(self) -> None:
        self._daily_message_count = self._load_count("daily_message_rate")
        self._minutely_message_count = self._load_count("minutely_message_rate")
        self._minutely_command_count = self._load_count("minutely_command_rate")

        dachshund.emit("daily_message_rate", value=self._daily_message_count)
        dachshund.emit("minutely_message_rate", value=self._minutely_message_count)
        dachshund.emit("minutely_command_rate", value=self._minutely_command_count)

    def _load_count(self, key: str) -> int:
        record = WidgetState.find(key)
        return int(record.value) if record else 0

    def _save_counts(self) -> None:
        for key, value in (
            ("daily_message_rate", self._daily_message_count),
            ("minutely_message_rate", self._minutely_message_count),
            ("minutely_command_rate", self._minutely_command_count),
        ):
            record = WidgetState.find(key)
            if record is None:
                WidgetState.create(key=key, value=str(value))
            else:
                record.update(value=str(value))

    def _reset_daily_count(self) -> None:
        self._daily_message_count = 0
        dachshund.emit("daily_message_rate", value=self._daily_message_count)

        self._save_counts()

    def _report_member_count(self) -> None:
        dachshund.emit(
            "member_count",
            value=sum(guild.member_count or 0 for guild in self.bot.guilds),
        )

    @Cog.listener()
    async def on_ready(self) -> None:
        self._report_member_count()

    @Cog.listener()
    async def on_member_join(self, _member: Member) -> None:
        self._report_member_count()

    @Cog.listener()
    async def on_member_remove(self, _member: Member) -> None:
        self._report_member_count()

    @Cog.listener()
    async def on_message(self, _message: Message) -> None:
        self._minutely_message_count += 1
        dachshund.emit("minutely_message_rate", value=self._minutely_message_count)

        self._daily_message_count += 1
        dachshund.emit("daily_message_rate", value=self._daily_message_count)
        dachshund.emit(
            "weekly_message_counts",
            date=datetime.now(self.timezone).date().isoformat(),
            value=1,
        )

    @Cog.listener()
    async def on_command(self, ctx: Context) -> None:
        if ctx.command:
            dachshund.emit("on_command", name=ctx.command.qualified_name, value=1)

        self._minutely_command_count += 1
        dachshund.emit("minutely_command_rate", value=self._minutely_command_count)

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
