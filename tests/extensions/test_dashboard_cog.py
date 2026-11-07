from unittest.mock import patch

import pytest
from discord.ext.commands import CommandInvokeError, CommandNotFound
from freezegun import freeze_time

from bot.extensions.dashboard_cog import (
    DAILY_DAYS,
    DAILY_SOURCES,
    ERROR_LENGTH,
    TRIM_SPAN,
    SUMMARY,
    DashboardCog,
    _commit,
)


def _fake_channel(name="general", parent=None, public=True):
    """A guild channel, which @everyone can see when `public`."""
    permissions = type("Permissions", (), {"view_channel": public})()
    guild = type("Guild", (), {"default_role": object()})()

    return type(
        "Channel",
        (),
        {
            "name": name,
            "parent": parent,
            "guild": guild,
            "permissions_for": lambda self, role: permissions,
        },
    )()


def _fake_message(author_id=1, bot=False, channel=None):
    author = type("Author", (), {"id": author_id, "bot": bot})()
    channel = channel or _fake_channel()
    return type("Message", (), {"author": author, "channel": channel})()


@pytest.fixture
def dashboard_cog(mock_bot):
    """Instantiate the DashboardCog with a mock bot."""
    mock_bot.latency_ms = 50
    return DashboardCog(mock_bot)


def test_report_latency__expect_records_latency_from_bot(dashboard_cog):
    """Verify _report_latency hands the bot's latency reading to the metrics recorder."""
    dashboard_cog._report_latency()

    dashboard_cog.bot.metrics.record_latency.assert_called_once_with(50)


@patch("bot.extensions.dashboard_cog.dachshund.emit")
def test_report_member_count__expect_emits_member_count_for_configured_guild(
    mock_emit, dashboard_cog
):
    """Verify _report_member_count emits the member count for the configured guild."""
    guild = type("Guild", (), {"member_count": 15})()
    dashboard_cog.bot.get_guild = lambda guild_id: guild

    dashboard_cog._report_member_count()

    mock_emit.assert_called_once_with("member_count", value=15)


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_ready__expect_reports_member_count(mock_emit, dashboard_cog):
    """Verify on_ready reports the current member count."""
    guild = type("Guild", (), {"member_count": 7})()
    dashboard_cog.bot.get_guild = lambda guild_id: guild

    await dashboard_cog.on_ready()

    mock_emit.assert_any_call("member_count", value=7)


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_ready__expect_a_members_refresh_ping(mock_emit, dashboard_cog):
    """Verify on_ready pings the members table to refetch its loader."""
    await dashboard_cog.on_ready()

    mock_emit.assert_any_call("members")


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_member_join__expect_reports_member_count(mock_emit, dashboard_cog):
    """Verify on_member_join reports the current member count."""
    guild = type("Guild", (), {"member_count": 8})()
    dashboard_cog.bot.get_guild = lambda guild_id: guild

    await dashboard_cog.on_member_join(object())

    mock_emit.assert_any_call("member_count", value=8)


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_member_join__expect_a_members_refresh_ping(mock_emit, dashboard_cog):
    """Verify on_member_join pings the members table to refetch its loader."""
    await dashboard_cog.on_member_join(object())

    mock_emit.assert_any_call("members")


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_member_remove__expect_reports_member_count(mock_emit, dashboard_cog):
    """Verify on_member_remove reports the current member count."""
    guild = type("Guild", (), {"member_count": 6})()
    dashboard_cog.bot.get_guild = lambda guild_id: guild

    await dashboard_cog.on_member_remove(object())

    mock_emit.assert_any_call("member_count", value=6)


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_member_remove__expect_a_members_refresh_ping(
    mock_emit, dashboard_cog
):
    """Verify on_member_remove pings the members table to refetch its loader."""
    await dashboard_cog.on_member_remove(object())

    mock_emit.assert_any_call("members")


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_message__expect_one_message_event_with_date_and_author(
    mock_emit, dashboard_cog
):
    """Verify on_message emits one event per message, dated in the cog's timezone."""
    with freeze_time("2025-02-21 03:00:00"):  # still the 20th in US/Eastern
        await dashboard_cog.on_message(_fake_message(author_id=7))

    mock_emit.assert_called_once_with(
        "message", date="2025-02-20", author="7", channel="general", value=1
    )


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_message__from_a_bot__expect_no_author(mock_emit, dashboard_cog):
    """Verify a bot's message still counts, but not toward active members."""
    with freeze_time("2025-02-20 12:00:00"):
        await dashboard_cog.on_message(_fake_message(author_id=99, bot=True))

    mock_emit.assert_called_once_with(
        "message", date="2025-02-20", author=None, channel="general", value=1
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "channel, expected",
    [
        (_fake_channel("help"), "help"),
        (_fake_channel("a question", parent=_fake_channel("forum")), "forum"),
        (_fake_channel("moderation_logs", public=False), "private"),
        (
            _fake_channel("a thread", parent=_fake_channel("staff", public=False)),
            "private",
        ),
        (type("DMChannel", (), {})(), "DM"),
    ],
)
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_message__expect_channel_or_its_parent(
    mock_emit, dashboard_cog, channel, expected
):
    """Verify threads count toward their parent, DMs toward "DM", and channels
    @everyone can't see toward "private"."""
    await dashboard_cog.on_message(_fake_message(channel=channel))

    assert mock_emit.call_args.kwargs["channel"] == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "listener, joined, left",
    [("on_member_join", 1, 0), ("on_member_remove", 0, 1)],
)
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_member_flow__expect_join_or_leave_event(
    mock_emit, dashboard_cog, listener, joined, left
):
    """Verify joins and leaves feed the joins vs leaves chart."""
    await getattr(dashboard_cog, listener)(object())

    mock_emit.assert_any_call("member_flow", joined=joined, left=left)


def _command_ctx():
    command = type("Cmd", (), {"qualified_name": "ping"})()

    return type("Ctx", (), {"command": command, "author": "ada"})()


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_command_completion__expect_duration_in_ms(mock_emit, dashboard_cog):
    """Verify a command's duration runs from on_command to its completion."""
    ctx = _command_ctx()

    with patch(
        "bot.extensions.dashboard_cog.time.perf_counter", side_effect=[10.0, 10.25]
    ):
        await dashboard_cog.on_command(ctx)
        await dashboard_cog.on_command_completion(ctx)

    mock_emit.assert_any_call("command_duration", name="ping", value=250.0)
    row = mock_emit.call_args_list[-1]
    assert row.args == ("recent_commands",)
    assert row.kwargs == {
        "command": "ping",
        "user": "ada",
        "status": "ok",
        "ms": 250.0,
        "error": "",
    }


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_command_completion__moderation_command__expect_no_recent_commands_row(
    mock_emit, dashboard_cog
):
    """Verify moderation commands go to their own table, with details."""
    await dashboard_cog.on_command_completion(_moderation_ctx())

    assert "recent_commands" not in [c.args[0] for c in mock_emit.call_args_list]


def _moderation_ctx():
    ctx = _command_ctx()
    ctx.cog = type("Cog", (), {"qualified_name": "Moderation"})()
    return ctx


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_command_error__moderation_command__expect_failed_moderation_row(
    mock_emit, dashboard_cog
):
    """Verify a failed moderation command lands in the moderation table, counted too."""
    error = CommandInvokeError(PermissionError("Missing Permissions"))

    await dashboard_cog.on_command_error(_moderation_ctx(), error)

    mock_emit.assert_any_call(
        "recent_moderation",
        action="ping (failed)",
        member="",
        by="ada",
        details="PermissionError: Missing Permissions",
    )
    assert [c.args[0] for c in mock_emit.call_args_list] == [
        "command_error",
        "command_outcome",
        "recent_moderation",
    ]


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_command_completion__without_a_start__expect_row_without_duration(
    mock_emit, dashboard_cog
):
    await dashboard_cog.on_command_completion(_command_ctx())

    assert [c.args[0] for c in mock_emit.call_args_list] == [
        "command_outcome",
        "recent_commands",
    ]
    assert mock_emit.call_args.kwargs["ms"] is None


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_command__expect_emits_command_name(mock_emit, dashboard_cog):
    """Verify on_command emits the qualified command name."""
    ctx = _command_ctx()

    await dashboard_cog.on_command(ctx)

    mock_emit.assert_any_call("on_command", name="ping", value=1)


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_command_error__expect_emits_command_name(mock_emit, dashboard_cog):
    """Verify on_command_error emits the qualified command name."""
    ctx = _command_ctx()

    await dashboard_cog.on_command_error(ctx, Exception("boom"))

    mock_emit.assert_any_call("command_error", name="ping", value=1)


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_command_error__expect_recent_error_row_unwrapped(
    mock_emit, dashboard_cog
):
    """Verify the recent commands table gets the original error, not discord.py's wrapper."""
    ctx = _command_ctx()
    error = CommandInvokeError(TimeoutError("weather API"))

    with (
        freeze_time("2025-02-21 03:00:00"),
        patch(
            "bot.extensions.dashboard_cog.time.perf_counter", side_effect=[10.0, 10.5]
        ),
    ):
        await dashboard_cog.on_command(ctx)
        await dashboard_cog.on_command_error(ctx, error)

    mock_emit.assert_any_call(
        "recent_commands",
        command="ping",
        user="ada",
        status="error",
        ms=500.0,
        error="TimeoutError: weather API",
    )


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_command_error__with_long_message__expect_truncated(
    mock_emit, dashboard_cog
):
    await dashboard_cog.on_command_error(_command_ctx(), Exception("x" * 1000))

    recent = [c for c in mock_emit.call_args_list if c.args[0] == "recent_commands"]
    assert len(recent[0].kwargs["error"]) == ERROR_LENGTH


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_command_error__with_unknown_command__expect_not_in_recent_commands(
    mock_emit, dashboard_cog
):
    """Verify command name typos only count, without burying the commands run."""
    await dashboard_cog.on_command_error(_command_ctx(), CommandNotFound("nope"))

    mock_emit.assert_called_once_with("command_error", name="ping", value=1)


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_command_error__without_a_command__expect_emits_unknown(
    mock_emit, dashboard_cog
):
    """Verify on_command_error falls back to 'unknown' when ctx.command is missing."""
    ctx = type("Ctx", (), {"command": None, "author": "ada"})()

    await dashboard_cog.on_command_error(ctx, Exception("boom"))

    mock_emit.assert_any_call("command_error", name="unknown", value=1)


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_disconnect__expect_emits_disconnect_event(mock_emit, dashboard_cog):
    """Verify on_disconnect emits a connection_event of type disconnect."""
    await dashboard_cog.on_disconnect()

    mock_emit.assert_called_once_with("connection_event", type="disconnect", value=1)


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_resumed__expect_emits_resume_event(mock_emit, dashboard_cog):
    """Verify on_resumed emits a connection_event of type resume."""
    await dashboard_cog.on_resumed()

    mock_emit.assert_called_once_with("connection_event", type="resume", value=1)


@patch("bot.extensions.dashboard_cog.dachshund.emit")
def test_cog_load__expect_schedules_reports_and_daily_trim(_emit, dashboard_cog):
    """Verify cog_load schedules the minute reports and the trim after midnight."""
    dashboard_cog.cog_load()

    dashboard_cog.bot.scheduler.add_job.assert_any_call(
        dashboard_cog._report_latency, "interval", minutes=1
    )
    dashboard_cog.bot.scheduler.add_job.assert_any_call(
        dashboard_cog._report_process, "interval", minutes=1
    )
    dashboard_cog.bot.scheduler.add_job.assert_any_call(
        dashboard_cog._trim_daily_charts,
        "cron",
        hour=0,
        minute=5,
        timezone=dashboard_cog.timezone,
    )
    assert len(dashboard_cog.jobs) == 3


@patch("bot.extensions.dashboard_cog.dachshund.emit")
def test_cog_load__expect_emits_the_summary_and_process(mock_emit, dashboard_cog):
    """Verify cog_load emits the summary, and the process right away."""
    dashboard_cog.cog_load()

    mock_emit.assert_any_call("summary", value=SUMMARY)
    sources = [c.args[0] for c in mock_emit.call_args_list]
    assert sources[:4] == ["summary", "process", "deployment", "gateway_events"]
    # Then the trim, so bars missed during downtime go too.
    assert set(sources[4:]) == set(DAILY_SOURCES)


@patch("bot.extensions.dashboard_cog.dachshund.emit")
def test_report_process__expect_memory_cpu_and_deployment(mock_emit, dashboard_cog):
    dashboard_cog.process.sample = lambda: {"memory_mb": 120.5, "cpu_percent": 3.2}
    dashboard_cog.process.uptime = lambda: "2 h"
    dashboard_cog.process.started_at = 1740106800  # 2025-02-21 03:00 UTC
    dashboard_cog.commit = "abc1234"
    dashboard_cog.bot.app.config.current_environment = "production"

    with (
        patch("bot.extensions.dashboard_cog.discord.__version__", "2.6.4"),
        patch(
            "bot.extensions.dashboard_cog.platform.python_version",
            return_value="3.12.3",
        ),
    ):
        dashboard_cog._report_process()

    mock_emit.assert_any_call("process", memory_mb=120.5, cpu_percent=3.2)
    mock_emit.assert_any_call(
        "deployment",
        environment="production",
        commit="abc1234",
        started="2025-02-20 22:00 EST",
        uptime="2 h",
        discord_py="2.6.4",
        python="3.12.3",
    )


def test_commit__on_railway__expect_its_short_sha(monkeypatch):
    monkeypatch.setenv("RAILWAY_GIT_COMMIT_SHA", "0123456789abcdef")

    assert _commit() == "0123456"


def test_commit__without_git__expect_unknown(monkeypatch):
    monkeypatch.delenv("RAILWAY_GIT_COMMIT_SHA", raising=False)

    with patch("bot.extensions.dashboard_cog.subprocess.run", side_effect=OSError):
        assert _commit() == "unknown"


def test_cog_unload__expect_removes_scheduled_jobs(dashboard_cog):
    """Verify cog_unload removes every job scheduled by cog_load."""
    dashboard_cog.cog_load()
    jobs = list(dashboard_cog.jobs)

    dashboard_cog.cog_unload()

    for job in jobs:
        dashboard_cog.bot.scheduler.remove_job.assert_any_call(job.id)


def _reaction(emoji, *, guild_id=1, bot=False, member=True):
    member = type("Member", (), {"bot": bot})() if member else None
    return type(
        "Payload", (), {"guild_id": guild_id, "member": member, "emoji": emoji}
    )()


def _emoji(name, custom=False):
    return type(
        "Emoji",
        (),
        {
            "name": name,
            "is_custom_emoji": lambda self: custom,
            "__str__": lambda self: name,
        },
    )()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "emoji, expected",
    [(_emoji("🔥"), "🔥"), (_emoji("party", custom=True), ":party:")],
)
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_raw_reaction_add__expect_day_and_emoji(
    mock_emit, dashboard_cog, emoji, expected
):
    with freeze_time("2025-02-21 03:00:00"):
        await dashboard_cog.on_raw_reaction_add(_reaction(emoji))

    mock_emit.assert_any_call("reactions_per_day", date="2025-02-20", value=1)
    mock_emit.assert_any_call("reaction_emojis", emoji=expected, value=1)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [_reaction(_emoji("🔥"), bot=True), _reaction(_emoji("🔥"), guild_id=None)],
)
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_raw_reaction_add__from_a_bot_or_dm__expect_nothing(
    mock_emit, dashboard_cog, payload
):
    await dashboard_cog.on_raw_reaction_add(payload)

    mock_emit.assert_not_called()


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_on_command__expect_counted_for_its_day(mock_emit, dashboard_cog):
    with freeze_time("2025-02-21 03:00:00"):
        await dashboard_cog.on_command(_command_ctx())

    mock_emit.assert_any_call("commands_per_day", date="2025-02-20", value=1)


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_command_outcome__expect_0_on_success_and_100_on_failure(
    mock_emit, dashboard_cog
):
    """Verify the average of `failed` is the error rate in percent."""
    await dashboard_cog.on_command_completion(_command_ctx())
    await dashboard_cog.on_command_error(_command_ctx(), Exception("boom"))

    outcomes = [
        c.kwargs for c in mock_emit.call_args_list if c.args[0] == "command_outcome"
    ]
    assert outcomes == [{"failed": 0}, {"failed": 100}]


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_command_outcome__unknown_command__expect_not_counted(
    mock_emit, dashboard_cog
):
    await dashboard_cog.on_command_error(_command_ctx(), CommandNotFound("nope"))

    assert "command_outcome" not in [c.args[0] for c in mock_emit.call_args_list]


@pytest.mark.asyncio
@patch("bot.extensions.dashboard_cog.dachshund.emit")
async def test_gateway_events__expect_counted_then_reported_and_reset(
    mock_emit, dashboard_cog
):
    dashboard_cog.process.sample = lambda: {}

    for _ in range(3):
        await dashboard_cog.on_socket_event_type("MESSAGE_CREATE")

    dashboard_cog._report_process()
    dashboard_cog._report_process()

    reports = [
        c.kwargs for c in mock_emit.call_args_list if c.args[0] == "gateway_events"
    ]
    assert reports == [{"value": 3}, {"value": 0}]


@patch("bot.extensions.dashboard_cog.dachshund.emit")
def test_trim_daily_charts__expect_dates_past_the_window_deleted(
    mock_emit, dashboard_cog
):
    from datetime import date

    dashboard_cog._trim_daily_charts(now=date(2025, 3, 31))

    deleted = {(c.args[0], c.kwargs["date"]) for c in mock_emit.call_args_list}
    assert all(c.kwargs["_delete"] is True for c in mock_emit.call_args_list)
    # Day 30 back is kept, days 31 to 37 back go.
    assert ("commands_per_day", "2025-03-01") not in deleted
    assert ("commands_per_day", "2025-02-28") in deleted
    assert len(deleted) == TRIM_SPAN * len(DAILY_SOURCES)
    assert DAILY_DAYS == 30
