from dachshund import BarChart, Number, Page

activity_page = Page("activity", title="Activity")

activity_page.row(
    Number("daily_message_rate", title="Today's Messages Rate"),
    BarChart("weekly_message_counts", title="Messages / day", x="date", persist=True),
    widths=(1, 2),
)
activity_page.row(
    BarChart("on_command", title="Calls Per Command", x="name", persist=True)
)
activity_page.row(
    BarChart("command_error", title="Errors Per Command", x="name", persist=True)
)
