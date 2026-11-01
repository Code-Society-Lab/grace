from dachshund import Row, Table

from lib.dashboard.pages.overview import greet_user, load_members, overview_page
from lib.dashboard.widgets.gauge import Gauge


def test_overview_page__expect_summary_latency_then_members():
    assert overview_page.rows == [
        Row(["summary"]),
        Row(["average_latency_gauge", "latency"], (1, 2)),
        Row(["member_count", "members"], (1, 2)),
        Row(["connection_event"]),
    ]


def test_overview_page__with_average_latency_gauge__expect_gauge_widget_in_ms():
    gauge = overview_page.widgets["average_latency_gauge"]

    assert isinstance(gauge, Gauge)
    assert gauge.source == "average_latency"
    assert gauge.unit == "ms"


def test_overview_page__with_members_table__expect_a_loader():
    members = overview_page.widgets["members"]

    assert isinstance(members, Table)
    assert members.loader is load_members
    assert members.persist is False
    assert members.actions == ["greet"]


def test_overview_page__expect_the_greet_action():
    action = overview_page.actions["greet"]

    assert action.handler is greet_user
    assert action.label == "Greet"


def _fake_bot(guild):
    return type("Bot", (), {"get_guild": staticmethod(lambda guild_id: guild)})()


def _fake_member(id, name):
    return type("Member", (), {"id": id, "name": name})()


def test_load_members__expect_every_member_as_a_row():
    guild = type(
        "Guild",
        (),
        {
            "id": 1349086642446532639,
            "name": "Code Society",
            "members": [_fake_member(1, "ada")],
        },
    )()
    bot = _fake_bot(guild)

    rows, next_cursor = load_members({"bot": bot}, None, 5)

    assert rows == [
        {
            "id": 1,
            "name": "ada",
            "guild": "Code Society",
            "_guild_id": "1349086642446532639",
        }
    ]
    assert next_cursor is None


def test_load_members__expect_a_next_cursor_when_more_remain():
    members = [_fake_member(i, f"user{i}") for i in range(3)]
    guild = type(
        "Guild",
        (),
        {"id": 1349086642446532639, "name": "Code Society", "members": members},
    )()
    bot = _fake_bot(guild)

    first_rows, next_cursor = load_members({"bot": bot}, None, 2)
    second_rows, second_cursor = load_members({"bot": bot}, next_cursor, 2)

    assert [row["id"] for row in first_rows] == [0, 1]
    assert next_cursor == "2"
    assert [row["id"] for row in second_rows] == [2]
    assert second_cursor is None
