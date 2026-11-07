import dachshund
from dachshund import Dashboard

from lib.dashboard.dashboard import build_dashboard
from lib.dashboard.sqlmodel_storage import SQLModelStorage


def test_build_dashboard__expect_every_page_and_widget_included(monkeypatch):
    dashboard = Dashboard(path=":memory:", storage=SQLModelStorage())
    monkeypatch.setattr(dachshund, "include", dashboard.include)

    build_dashboard()

    assert list(dashboard.pages) == ["overview", "activity", "admin"]
    assert sorted(dashboard.widgets) == sorted(
        [
            "summary",
            "latency",
            "logs",
            "average_latency_gauge",
            "daily_message_rate",
            "member_count",
            "active_members",
            "members",
            "admin_member_count",
            "weekly_message_counts",
            "on_command",
            "command_error",
            "connection_event",
            "commands_24h",
            "worst_latency",
            "commands_per_day",
            "reactions_per_day",
            "reaction_emojis",
            "error_rate",
            "gateway_events",
            "recent_joins",
            "member_flow",
            "recent_moderation",
            "channel_messages",
            "enabled_extensions",
            "disabled_extensions",
            "jobs",
            "deployment_environment",
            "deployment_commit",
            "deployment_started",
            "deployment_discord_py",
            "deployment_python",
            "process_memory",
            "process_cpu",
            "process",
            "command_duration",
            "recent_commands",
            "dashboard_logins",
        ]
    )
    assert list(dashboard.actions) == ["enable_extension", "disable_extension"]
