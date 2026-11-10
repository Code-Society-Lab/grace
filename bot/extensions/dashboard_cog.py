import os
import platform
import subprocess
import time
from datetime import date, datetime, timedelta, tzinfo

import dachshund
import discord
from apscheduler.job import Job
from discord import AuditLogEntry, Member, Message, RawReactionActionEvent
from discord.ext.commands import (
    CommandInvokeError,
    CommandNotFound,
    Cog,
    Context,
    HybridCommandError,
)

from bot.grace import Grace
from bot.services.process_stats_service import ProcessStats

STARTED_AT = "_dashboard_started_at"
# Bar charts with a bar per date, which keep only the last DAILY_DAYS days.
DAILY_SOURCES = ("commands_per_day", "reactions_per_day")
DAILY_DAYS = 30
# Dates trimmed each run, so a week of downtime still gets cleaned up.
TRIM_SPAN = 7

# Their commands go to the recent moderation table instead of recent commands.
MODERATION_COGS = {"Moderation"}
ERROR_LENGTH = 300

SUMMARY = """
# Welcome!
### This dashboard contain various monitoring information about **Grace**, our awesome bot!
Hopefully, you will find something useful here.

- [Website](https://codesociety.xyz)
- [Discord](https://discord.gg/FzgwHD7Am3)
- [Source](https://github.com/Code-Society-Lab/grace)
"""


def _channel_name(message: Message) -> str:
    """The channel a message counts toward, as shown publicly.

    A thread counts toward its parent, a DM toward "DM", and a channel
    @everyone can't see toward "private", so its name stays hidden.
    """
    channel = getattr(message.channel, "parent", None) or message.channel
    guild = getattr(channel, "guild", None)

    if guild is None:
        return "DM"

    if not channel.permissions_for(guild.default_role).view_channel:
        return "private"

    return channel.name


def _commit() -> str:
    """The deployed commit: Railway's, or the local checkout's."""
    if sha := os.environ.get("RAILWAY_GIT_COMMIT_SHA"):
        return sha[:7]

    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def _emoji_name(payload: RawReactionActionEvent) -> str:
    """A unicode emoji as is, a custom one as `:name:`."""
    emoji = payload.emoji

    if emoji.is_custom_emoji():
        return f":{emoji.name or 'custom'}:"

    return str(emoji)


def _stayed(member: Member) -> str:
    """Time on the server, like "3d 4h" or "12m"."""
    if member.joined_at is None:
        return "unknown"

    stayed = datetime.now(member.joined_at.tzinfo) - member.joined_at
    hours, seconds = divmod(stayed.seconds, 3600)
    minutes = seconds // 60

    if stayed.days:
        return f"{stayed.days}d {hours}h"

    return f"{hours}h {minutes}m" if hours else f"{minutes}m"


def _audit_target(entry: AuditLogEntry) -> str:
    target = entry.target

    if target is None:
        return ""

    return str(getattr(target, "name", None) or f"id {target.id}")


def _audit_changes(entry: AuditLogEntry) -> str:
    changed = {attribute for attribute, _ in entry.changes.after}
    changed |= {attribute for attribute, _ in entry.changes.before}

    return ", ".join(sorted(changed))


def _is_moderation(ctx: Context) -> bool:
    """Whether `ctx`'s command belongs to a moderation cog."""
    cog = getattr(ctx, "cog", None)

    return cog is not None and cog.qualified_name in MODERATION_COGS


def _elapsed_ms(ctx: Context) -> float | None:
    """Time since `on_command` saw `ctx`, `None` if it didn't."""
    started_at = getattr(ctx, STARTED_AT, None)

    if started_at is None:
        return None

    return round((time.perf_counter() - started_at) * 1000, 1)


def _describe(error: Exception) -> str:
    """`error`'s type and message, unwrapped from discord.py's wrappers."""
    while isinstance(error, (CommandInvokeError, HybridCommandError)):
        error = error.original

    return f"{type(error).__name__}: {error}"[:ERROR_LENGTH]


class DashboardCog(
    Cog, name="Dashboard", description="Feeds bot telemetry to the live dashboard"
):
    """Feeds bot telemetry to the live dashboard"""

    def __init__(self, bot: Grace):
        self.bot: Grace = bot
        self.jobs: list[Job] = []
        self.timezone: tzinfo = bot.timezone
        self.process = ProcessStats()
        self.commit = _commit()
        self.gateway_events = 0

    def cog_load(self) -> None:
        dachshund.emit("summary", value=SUMMARY)
        self._report_process()

        self.jobs.append(
            self.bot.scheduler.add_job(self._report_latency, "interval", minutes=1)
        )
        self.jobs.append(
            self.bot.scheduler.add_job(self._report_process, "interval", minutes=1)
        )

        self._trim_daily_charts()
        self.jobs.append(
            self.bot.scheduler.add_job(
                self._trim_daily_charts,
                "cron",
                hour=0,
                minute=5,
                timezone=self.timezone,
            )
        )

    def cog_unload(self) -> None:
        for job in self.jobs:
            self.bot.scheduler.remove_job(job.id)

    def _report_latency(self) -> None:
        self.bot.metrics.record_latency(self.bot.latency_ms)

    def _report_process(self) -> None:
        dachshund.emit("process", **self.process.sample())
        dachshund.emit("deployment", **self._deployment())

        dachshund.emit("gateway_events", value=self.gateway_events)
        self.gateway_events = 0

    def _today(self) -> str:
        """Today's date, the day starting at midnight in the bot's timezone."""
        return datetime.now(self.timezone).date().isoformat()

    def _trim_daily_charts(self, now: date | None = None) -> None:
        """Remove the bars older than DAILY_DAYS from the per-day charts."""
        now = now or date.fromisoformat(self._today())

        for days_ago in range(DAILY_DAYS + 1, DAILY_DAYS + 1 + TRIM_SPAN):
            old = (now - timedelta(days=days_ago)).isoformat()

            for source in DAILY_SOURCES:
                dachshund.emit(source, date=old, _delete=True)

    def _deployment(self) -> dict[str, str]:
        started = datetime.fromtimestamp(self.process.started_at, self.timezone)

        return {
            "environment": self.bot.app.config.current_environment,
            "commit": self.commit,
            "started": f"{started:%Y-%m-%d %H:%M %Z}",
            "uptime": self.process.uptime(),
            "discord_py": discord.__version__,
            "python": platform.python_version(),
        }

    def _report_member_count(self) -> None:
        if guild := self.bot.guild:
            dachshund.emit("member_count", value=guild.member_count)

    @Cog.listener()
    async def on_ready(self) -> None:
        self._report_member_count()
        dachshund.emit("members")

    @Cog.listener()
    async def on_member_join(self, _member: Member) -> None:
        self._report_member_count()
        dachshund.emit("members")
        dachshund.emit("member_flow", joined=1, left=0)

    @Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        self._report_member_count()
        dachshund.emit("members")
        dachshund.emit("member_flow", joined=0, left=1)
        dachshund.emit(
            "recent_leaves",
            id=str(member.id),
            name=member.name,
            nickname=member.nick,
            stayed=_stayed(member),
            account_created=member.created_at.strftime("%d %b %Y"),
        )

    @Cog.listener()
    async def on_audit_log_entry_create(self, entry: AuditLogEntry) -> None:
        dachshund.emit(
            "audit_log",
            action=entry.action.name.replace("_", " "),
            by=str(entry.user) if entry.user else f"id {entry.user_id}",
            target=_audit_target(entry),
            reason=entry.reason or "",
            changes=_audit_changes(entry),
        )

    @Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent) -> None:
        if payload.guild_id is None or (payload.member and payload.member.bot):
            return

        dachshund.emit("reactions_per_day", date=self._today(), value=1)
        dachshund.emit("reaction_emojis", emoji=_emoji_name(payload), value=1)

    @Cog.listener()
    async def on_socket_event_type(self, _event_type: str) -> None:
        self.gateway_events += 1

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        dachshund.emit(
            "message",
            date=datetime.now(self.timezone).date().isoformat(),
            author=None if message.author.bot else str(message.author.id),
            channel=_channel_name(message),
            value=1,
        )

    @Cog.listener()
    async def on_command(self, ctx: Context) -> None:
        setattr(ctx, STARTED_AT, time.perf_counter())

        if ctx.command:
            dachshund.emit("on_command", name=ctx.command.qualified_name, value=1)
            dachshund.emit("commands_per_day", date=self._today(), value=1)

    @Cog.listener()
    async def on_command_completion(self, ctx: Context) -> None:
        elapsed_ms = _elapsed_ms(ctx)

        if ctx.command and elapsed_ms is not None:
            dachshund.emit(
                "command_duration", name=ctx.command.qualified_name, value=elapsed_ms
            )

        dachshund.emit("command_outcome", failed=0)

        # Moderation commands log their own row, with details.
        if not _is_moderation(ctx):
            self._record_command(ctx, "ok", elapsed_ms)

    @Cog.listener()
    async def on_command_error(self, ctx: Context, error: Exception) -> None:
        name = ctx.command.qualified_name if ctx.command else "unknown"
        dachshund.emit("command_error", name=name, value=1)

        # Typos of command names would bury the commands actually run.
        if isinstance(error, CommandNotFound):
            return

        # 100 per failure, so the average over a window is the error rate in %.
        dachshund.emit("command_outcome", failed=100)

        if _is_moderation(ctx):
            dachshund.emit(
                "recent_moderation",
                action=f"{name} (failed)",
                member="",
                by=str(ctx.author),
                details=_describe(error),
            )
        else:
            self._record_command(ctx, "error", _elapsed_ms(ctx), _describe(error))

    def _record_command(
        self, ctx: Context, status: str, elapsed_ms: float | None, error: str = ""
    ) -> None:
        """A row of the recent commands table."""
        dachshund.emit(
            "recent_commands",
            command=ctx.command.qualified_name if ctx.command else "unknown",
            user=str(ctx.author),
            status=status,
            ms=elapsed_ms,
            error=error,
        )

    @Cog.listener()
    async def on_disconnect(self) -> None:
        dachshund.emit("connection_event", type="disconnect", value=1)

    @Cog.listener()
    async def on_resumed(self) -> None:
        dachshund.emit("connection_event", type="resume", value=1)


async def setup(bot: Grace) -> None:
    await bot.add_cog(DashboardCog(bot))
