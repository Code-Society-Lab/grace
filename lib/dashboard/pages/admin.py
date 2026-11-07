from datetime import timedelta

from dachshund import Page
from dachshund.widgets import BarChart, Logs, Number, Table, TimeSeriesChart

from lib.dashboard.handlers import extensions, jobs, members
from lib.dashboard.widgets.recent_table import RecentTable
from lib.dashboard.widgets.stat import Stat

admin_page = Page("admin", title="Admin")

admin_page.action("enable_extension", label="Enable")(extensions.enable)
admin_page.action("disable_extension", label="Disable", confirm=True)(
    extensions.disable
)

# One "deployment" event, a field per card.
DEPLOYMENT = [
    ("environment", "Environment"),
    ("started", "Started"),
    ("commit", "Commit"),
    ("discord_py", "discord.py"),
    ("python", "Python"),
]

with admin_page.row():
    for field, title in DEPLOYMENT:
        admin_page.add(
            Stat(f"deployment_{field}", title=title, source="deployment", y=field)
        )

with admin_page.row():
    with admin_page.column(span=4):
        admin_page.add(
            Number(
                "process_memory",
                title="Memory",
                source="process",
                y="memory_mb",
                unit="MB",
            )
        )
        admin_page.add(
            Number(
                "process_cpu",
                title="CPU",
                source="process",
                y="cpu_percent",
                unit="%",
            )
        )
    admin_page.add(
        TimeSeriesChart(
            "process",
            title="Memory (24 h)",
            y=["memory_mb"],
            aggregate="average",
            every=timedelta(minutes=10),
            over=timedelta(days=1),
        )
    )

with admin_page.row():
    with admin_page.column(span=4):
        admin_page.add(
            Number(
                "error_rate",
                title="Error Rate (last 24h)",
                source="command_outcome",
                y="failed",
                aggregate="average",
                over=timedelta(hours=24),
                unit="%",
            )
        )
    admin_page.add(
        TimeSeriesChart(
            "gateway_events",
            title="Gateway Events / min",
            aggregate="average",
            every=timedelta(minutes=10),
            over=timedelta(days=1),
        )
    )


with admin_page.row():
    admin_page.add(Logs("logs", title="Logs"))


with admin_page.row():
    admin_page.add(
        BarChart(
            "command_duration",
            title="Average Command Time (ms)",
            x="name",
            aggregate="average",
            persist=True,
        )
    )

    admin_page.add(
        BarChart("command_error", title="Errors Per Command", x="name", persist=True)
    )


with admin_page.row():
    admin_page.add(
        RecentTable(
            "recent_commands",
            title="Recent Commands",
            timezone="US/Eastern",
            columns=["time", "command", "user", "status", "ms", "error"],
            keep=100,
        )
    )

    admin_page.add(
        RecentTable(
            "recent_moderation",
            title="Recent Moderation",
            timezone="US/Eastern",
            columns=["time", "action", "member", "by", "details"],
            keep=100,
        )
    )

with admin_page.row():
    with admin_page.column(span=4):
        # Overview's card is already named "member_count"; names are unique.
        admin_page.add(
            Number("admin_member_count", title="Members", source="member_count")
        )

    admin_page.add(
        Table(
            "members",
            columns=members.COLUMNS,
            search=True,
            page_size=5,
            loader=members.load,
        )
    )


with admin_page.row():
    admin_page.add(
        Table(
            "enabled_extensions",
            title="Enabled Extensions",
            source=extensions.SOURCE,
            columns=extensions.COLUMNS,
            page_size=10,
            loader=extensions.load_enabled,
            actions=["disable_extension"],
        )
    )
    admin_page.add(
        Table(
            "disabled_extensions",
            title="Disabled Extensions",
            source=extensions.SOURCE,
            columns=extensions.COLUMNS,
            page_size=10,
            loader=extensions.load_disabled,
            actions=["enable_extension"],
        )
    )

with admin_page.row():
    admin_page.add(
        Table(
            "jobs",
            title="Scheduled Jobs",
            columns=jobs.COLUMNS,
            page_size=10,
            loader=jobs.load,
        )
    )

with admin_page.row():
    admin_page.add(
        RecentTable(
            "dashboard_logins",
            title="Dashboard Logins",
            timezone="US/Eastern",
            columns=["time", "user", "id", "result", "ip"],
            keep=100,
        )
    )
