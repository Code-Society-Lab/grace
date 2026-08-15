import dachshund

from discord.ext.commands import Cog


class DashboardCog(
    Cog, name="Dashboard", description="Feeds bot telemetry to the live dashboard"
):
    """Schedules periodic latency checks and emits the events the dachshund
    dashboard charts (latency, highest latency, messages, commands) watch."""

    def __init__(self, bot):
        self.bot = bot
        self.jobs = []

    def cog_load(self):
        self.jobs.append(
            self.bot.scheduler.add_job(self._report_latency, "cron", minute="*/1")
        )

    def cog_unload(self):
        for job in self.jobs:
            self.bot.scheduler.remove_job(job.id)

    def _report_latency(self) -> None:
        self.bot.metrics.record_latency(self.bot.latency_ms)

    @Cog.listener()
    async def on_message(self, message) -> None:
        dachshund.emit("on_message")

    @Cog.listener()
    async def on_command(self, ctx):
        dachshund.emit("on_command", name=ctx.command.qualified_name, value=1)


async def setup(bot):
    await bot.add_cog(DashboardCog(bot))
