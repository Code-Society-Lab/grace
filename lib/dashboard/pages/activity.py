from datetime import timedelta

from dachshund import Page
from dachshund.widgets import BarChart, Number, TimeSeriesChart

from lib.dashboard.widgets.top_bar_chart import TopBarChart

activity_page = Page("activity", title="Activity", public=True)

with activity_page.row():
    activity_page.add(
        Number(
            "active_members",
            title="Active Today",
            source="message",
            y="author",
            aggregate="distinct",
            over="day",
        )
    )
    activity_page.add(
        Number(
            "daily_message_rate",
            title="Messages (last 24h)",
            source="message",
            aggregate="count",
            over="day",
        )
    )
    activity_page.add(
        Number(
            "commands_24h",
            title="Commands (last 24h)",
            source="on_command",
            aggregate="count",
            over=timedelta(hours=24),
        )
    )
    activity_page.add(
        Number(
            "recent_joins",
            title="Joins (last hour)",
            source="member_flow",
            y="joined",
            aggregate="sum",
            over=timedelta(hours=1),
        )
    )

with activity_page.row():
    activity_page.add(
        TimeSeriesChart(
            "member_flow",
            title="Joins vs Leaves",
            y=["joined", "left"],
            aggregate="sum",
            every=timedelta(days=1),
            over=timedelta(days=30),
        )
    )

with activity_page.row():
    activity_page.add(
        BarChart(
            "weekly_message_counts",
            title="Messages / day",
            source="message",
            x="date",
            persist=True,
        )
    )
    activity_page.add(
        BarChart(
            "channel_messages",
            title="Messages per Channel",
            source="message",
            x="channel",
            persist=True,
        )
    )

with activity_page.row():
    activity_page.add(
        BarChart(
            "commands_per_day",
            title="Commands / day",
            x="date",
            persist=True,
        )
    )
    activity_page.add(
        BarChart("on_command", title="Calls Per Command", x="name", persist=True)
    )

with activity_page.row():
    activity_page.add(
        BarChart(
            "reactions_per_day",
            title="Reactions / day",
            x="date",
            persist=True,
        )
    )
    activity_page.add(
        TopBarChart(
            "reaction_emojis",
            title="Top Emojis",
            x="emoji",
            top=10,
            persist=True,
        )
    )
