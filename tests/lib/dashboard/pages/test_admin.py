from datetime import timedelta

import pytest
from dachshund import Column, Row
from dachshund.widgets import BarChart, Logs, Table, TimeSeriesChart

from lib.dashboard.widgets.recent_table import RecentTable
from lib.dashboard.widgets.stat import Stat
from lib.dashboard.handlers import extensions, jobs, members
from lib.dashboard.pages.admin import admin_page

DEPLOYMENT_FIELDS = [
    "environment",
    "started",
    "commit",
    "discord_py",
    "python",
]


def test_admin_page__with_deployment__expect_a_stat_card_per_field():
    for field in DEPLOYMENT_FIELDS:
        card = admin_page.widgets[f"deployment_{field}"]

        assert isinstance(card, Stat)
        assert (card.source, card.y) == ("deployment", field)


def test_admin_page__expect_private():
    assert admin_page.public is False


def test_admin_page__expect_health_then_commands_then_moderation_then_tables():
    assert admin_page.rows == [
        Row([Column([f"deployment_{field}"]) for field in DEPLOYMENT_FIELDS]),
        Row([Column(["process_memory", "process_cpu"], 4), Column(["process"])]),
        Row([Column(["error_rate"], 4), Column(["gateway_events"])]),
        Row([Column(["logs"])]),
        Row([Column(["command_duration"]), Column(["command_error"])]),
        Row([Column(["recent_commands"]), Column(["recent_moderation"])]),
        Row([Column(["admin_member_count"], 4), Column(["members"])]),
        Row([Column(["enabled_extensions"]), Column(["disabled_extensions"])]),
        Row([Column(["jobs"])]),
        Row([Column(["dashboard_logins"])]),
    ]


def test_admin_page__with_recent_moderation__expect_newest_hundred():
    table = admin_page.widgets["recent_moderation"]

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
    table = admin_page.widgets[name]

    assert table.source == "extensions"
    assert table.loader is loader
    assert table.actions == actions


def test_admin_page__expect_actions_from_the_extension_handlers():
    assert admin_page.actions["enable_extension"].handler is extensions.enable
    assert admin_page.actions["disable_extension"].handler is extensions.disable


def test_admin_page__with_jobs_table__expect_jobs_loader():
    assert admin_page.widgets["jobs"].loader is jobs.load


def test_admin_page__expect_private_actions_disable_confirmed():
    assert admin_page.actions["disable_extension"].confirm is True
    assert not admin_page.actions["enable_extension"].public
    assert not admin_page.actions["disable_extension"].public


def test_admin_page__with_process__expect_memory_and_cpu_numbers():
    memory = admin_page.widgets["process_memory"]
    cpu = admin_page.widgets["process_cpu"]

    assert (memory.source, memory.y, memory.unit) == ("process", "memory_mb", "MB")
    assert (cpu.source, cpu.y, cpu.unit) == ("process", "cpu_percent", "%")


def test_admin_page__with_command_duration__expect_persisted_average():
    chart = admin_page.widgets["command_duration"]

    assert isinstance(chart, BarChart)
    assert chart.aggregate == "average"
    assert chart.persist is True


def test_admin_page__with_recent_commands__expect_newest_hundred():
    table = admin_page.widgets["recent_commands"]

    assert isinstance(table, RecentTable)
    assert table.columns == ["time", "command", "user", "status", "ms", "error"]
    assert table.keep == 100


def test_admin_page__with_error_rate__expect_average_failed_percent_over_a_day():
    number = admin_page.widgets["error_rate"]

    assert (number.source, number.y, number.aggregate, number.unit) == (
        "command_outcome",
        "failed",
        "average",
        "%",
    )
    assert number.over == timedelta(hours=24)


def test_admin_page__with_gateway_events__expect_per_minute_counts_over_a_day():
    chart = admin_page.widgets["gateway_events"]

    assert isinstance(chart, TimeSeriesChart)
    assert chart.aggregate == "average"
    assert chart.every == timedelta(minutes=10)
    assert chart.over == timedelta(days=1)


@pytest.mark.parametrize(
    "name", ["recent_commands", "recent_moderation", "dashboard_logins"]
)
def test_admin_page__recent_tables__expect_times_in_eastern(name):
    assert admin_page.widgets[name].timezone == "US/Eastern"


def test_admin_page__with_logins__expect_newest_hundred():
    table = admin_page.widgets["dashboard_logins"]

    assert isinstance(table, RecentTable)
    assert table.columns == ["time", "user", "id", "result", "ip"]
    assert table.keep == 100


def test_admin_page__with_logs__expect_logs_widget():
    assert isinstance(admin_page.widgets["logs"], Logs)


def test_admin_page__with_command_errors__expect_persisted_bar_chart():
    chart = admin_page.widgets["command_error"]

    assert isinstance(chart, BarChart)
    assert chart.x == "name"
    assert chart.persist is True


def test_admin_page__with_members_table__expect_a_loader():
    table = admin_page.widgets["members"]

    assert isinstance(table, Table)
    assert table.loader is members.load
    assert table.persist is False
    assert table.actions == []
