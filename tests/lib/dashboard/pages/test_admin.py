from datetime import timedelta

import pytest
from dachshund import Column, Row
from dachshund.widgets import BarChart, Logs, Table, TimeSeriesChart

from lib.dashboard.widgets.recent_table import RecentTable
from lib.dashboard.widgets.stat import Stat
from lib.dashboard.handlers import extensions, jobs, members
from lib.dashboard.pages.admin import admin_page

WIDGETS = {
    name: widget for page in admin_page.every() for name, widget in page.widgets.items()
}

DEPLOYMENT_FIELDS = [
    "environment",
    "started",
    "commit",
    "discord_py",
    "python",
]


def test_admin_page__with_deployment__expect_a_stat_card_per_field():
    for field in DEPLOYMENT_FIELDS:
        card = WIDGETS[f"deployment_{field}"]

        assert isinstance(card, Stat)
        assert (card.source, card.y) == ("deployment", field)


def test_admin_page__expect_private():
    assert admin_page.public is False


def test_admin_page__expect_a_tab_per_area():
    assert admin_page.rows == []
    assert [(tab.name, tab.title) for tab in admin_page.tabs.values()] == [
        ("health", "Health"),
        ("members", "Members"),
        ("commands", "Commands"),
        ("extensions", "Extensions"),
    ]


@pytest.mark.parametrize(
    "tab, rows",
    [
        (
            "health",
            [
                Row([Column([f"deployment_{field}"]) for field in DEPLOYMENT_FIELDS]),
                Row(
                    [Column(["process_memory", "process_cpu"], 4), Column(["process"])]
                ),
                Row([Column(["error_rate"], 4), Column(["gateway_events"])]),
                Row([Column(["logs"]), Column(["error_logs"])]),
                Row([Column(["dashboard_logs"]), Column(["dashboard_logins"])]),
            ],
        ),
        (
            "commands",
            [
                Row([Column(["command_duration"]), Column(["command_error"])]),
                Row([Column(["recent_commands"])]),
            ],
        ),
        (
            "members",
            [
                Row([Column(["audit_log"]), Column(["recent_moderation"])]),
                Row([Column(["recent_members"]), Column(["recent_leaves"])]),
                Row([Column(["members"])]),
            ],
        ),
        (
            "extensions",
            [
                Row([Column(["enabled_extensions"]), Column(["disabled_extensions"])]),
                Row([Column(["jobs"]), Column(["scheduler_logs"])]),
            ],
        ),
    ],
)
def test_admin_page__expect_each_tab_layout(tab, rows):
    assert admin_page.tabs[tab].rows == rows


def test_admin_page__expect_tabs_private():
    assert not any(tab.public for tab in admin_page.tabs.values())


def test_admin_page__with_recent_moderation__expect_newest_hundred():
    table = WIDGETS["recent_moderation"]

    assert isinstance(table, RecentTable)
    assert table.columns == ["time", "action", "member", "by", "details"]
    assert table.keep == 100


@pytest.mark.parametrize(
    "name, loader, actions",
    [
        ("enabled_extensions", extensions.load_enabled, ["disable_extension"]),
        ("disabled_extensions", extensions.load_disabled, ["enable_extension"]),
    ],
)
def test_admin_page__with_extension_tables__expect_the_action_moving_them_across(
    name, loader, actions
):
    table = WIDGETS[name]

    assert table.source == "extensions"
    assert table.loader is loader
    assert table.actions == actions


def test_admin_page__expect_actions_from_the_extension_handlers():
    assert admin_page.actions["enable_extension"].handler is extensions.enable
    assert admin_page.actions["disable_extension"].handler is extensions.disable


def test_admin_page__with_jobs_table__expect_jobs_loader():
    assert WIDGETS["jobs"].loader is jobs.load


def test_admin_page__expect_private_actions_disable_confirmed():
    assert admin_page.actions["disable_extension"].confirm is True
    assert not admin_page.actions["enable_extension"].public
    assert not admin_page.actions["disable_extension"].public


def test_admin_page__with_process__expect_memory_and_cpu_numbers():
    memory = WIDGETS["process_memory"]
    cpu = WIDGETS["process_cpu"]

    assert (memory.source, memory.y, memory.unit) == ("process", "memory_mb", "MB")
    assert (cpu.source, cpu.y, cpu.unit) == ("process", "cpu_percent", "%")


def test_admin_page__with_command_duration__expect_persisted_average():
    chart = WIDGETS["command_duration"]

    assert isinstance(chart, BarChart)
    assert chart.aggregate == "average"
    assert chart.persist is True


def test_admin_page__with_recent_commands__expect_newest_hundred():
    table = WIDGETS["recent_commands"]

    assert isinstance(table, RecentTable)
    assert table.columns == ["time", "command", "user", "status", "ms", "error"]
    assert table.keep == 100


def test_admin_page__with_error_rate__expect_average_failed_percent_over_a_day():
    number = WIDGETS["error_rate"]

    assert (number.source, number.y, number.aggregate, number.unit) == (
        "command_outcome",
        "failed",
        "average",
        "%",
    )
    assert number.over == timedelta(hours=24)


def test_admin_page__with_gateway_events__expect_per_minute_counts_over_a_day():
    chart = WIDGETS["gateway_events"]

    assert isinstance(chart, TimeSeriesChart)
    assert chart.aggregate == "average"
    assert chart.every == timedelta(minutes=10)
    assert chart.over == timedelta(days=1)


@pytest.mark.parametrize(
    "name",
    [
        "recent_commands",
        "recent_moderation",
        "dashboard_logins",
        "audit_log",
        "recent_leaves",
    ],
)
def test_admin_page__recent_tables__expect_the_dashboard_timezone(name):
    assert WIDGETS[name].timezone is None


def test_admin_page__with_logins__expect_newest_hundred():
    table = WIDGETS["dashboard_logins"]

    assert isinstance(table, RecentTable)
    assert table.columns == ["time", "user", "id", "result", "ip"]
    assert table.keep == 100


def test_admin_page__with_logs__expect_everything_but_the_scheduler():
    logs = WIDGETS["logs"]

    assert isinstance(logs, Logs)
    assert logs.include == []
    assert logs.exclude == ["apscheduler"]
    assert logs.level == "INFO"


def test_admin_page__with_scheduler_logs__expect_only_the_scheduler():
    logs = WIDGETS["scheduler_logs"]

    assert isinstance(logs, Logs)
    assert logs.include == ["apscheduler"]


def test_admin_page__with_dashboard_logs__expect_only_dachshund():
    logs = WIDGETS["dashboard_logs"]

    assert isinstance(logs, Logs)
    assert logs.include == ["dachshund"]


def test_admin_page__with_recent_members__expect_reloaded_on_member_flow():
    table = WIDGETS["recent_members"]

    assert isinstance(table, Table)
    assert table.loader is members.load_recent
    assert table.source == "member_flow"
    assert table.columns == members.RECENT_COLUMNS


def test_admin_page__with_error_logs__expect_last_500_errors():
    widget = WIDGETS["error_logs"]

    assert isinstance(widget, Logs)
    assert (widget.level, widget.keep) == ("ERROR", 500)


def test_admin_page__with_command_errors__expect_persisted_bar_chart():
    chart = WIDGETS["command_error"]

    assert isinstance(chart, BarChart)
    assert chart.x == "name"
    assert chart.persist is True


def test_admin_page__with_members_table__expect_a_loader():
    table = WIDGETS["members"]

    assert isinstance(table, Table)
    assert table.loader is members.load
    assert table.persist is False
    assert table.actions == []


def test_admin_page__with_audit_log__expect_newest_two_hundred():
    table = WIDGETS["audit_log"]

    assert isinstance(table, RecentTable)
    assert table.columns == ["time", "action", "by", "target", "reason", "changes"]
    assert table.keep == 200


def test_admin_page__with_recent_leaves__expect_newest_hundred():
    table = WIDGETS["recent_leaves"]

    assert isinstance(table, RecentTable)
    assert table.keep == 100
