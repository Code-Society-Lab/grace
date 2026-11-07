from dachshund import Page
from dachshund.widgets import BarChart, Number

activity_page = Page("activity", title="Activity", public=True)

with activity_page.row():
    activity_page.add(Number("member_count"))
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
            title="Today's Messages Rate",
            source="message",
            aggregate="count",
            over="day",
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

with activity_page.row():
    activity_page.add(
        BarChart("on_command", title="Calls Per Command", x="name", persist=True)
    )
