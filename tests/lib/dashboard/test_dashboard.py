import dachshund
from dachshund import Dashboard

from lib.dashboard.dashboard import build_dashboard
from lib.dashboard.sqlmodel_storage import SQLModelStorage


def test_build_dashboard__expect_every_page_and_widget_included(monkeypatch):
    dashboard = Dashboard(path=":memory:", storage=SQLModelStorage())
    monkeypatch.setattr(dachshund, "include", dashboard.include)

    build_dashboard()

    assert list(dashboard.pages) == ["overview", "activity"]
    assert sorted(dashboard.widgets) == sorted(
        [
            "summary",
            "latency",
            "average_latency_gauge",
            "daily_message_rate",
            "member_count",
            "active_members",
            "members",
            "weekly_message_counts",
            "on_command",
            "command_error",
            "connection_event",
        ]
    )
    assert list(dashboard.actions) == []
