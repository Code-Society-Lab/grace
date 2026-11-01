from dachshund import BarChart, Number, Page

activity_page = Page("activity", title="Activity")

messages = activity_page.tab("messages", title="Messages")
message_rate = messages.add(Number("daily_message_rate", title="Today's Messages Rate"))
message_counts = messages.add(
    BarChart("weekly_message_counts", title="Messages / day", x="date", persist=True)
)
messages.row(message_rate, message_counts)

commands = activity_page.tab("commands", title="Commands")
calls = commands.add(
    BarChart("on_command", title="Calls Per Command", x="name", persist=True)
)
errors = commands.add(
    BarChart("command_error", title="Errors Per Command", x="name", persist=True)
)
commands.row(calls)
commands.row(errors)

connections = activity_page.tab("connections", title="Connections")
connections.add(
    BarChart("connection_event", title="Connection Events", x="type", persist=True)
)
