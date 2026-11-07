from datetime import datetime

from dachshund.widgets import TableQuery

from lib.dashboard.handlers.members import load


def _fake_bot(guild):
    return type("Bot", (), {"get_guild": staticmethod(lambda guild_id: guild)})()


def _fake_member(id, name, nick=None, joined_at=datetime(2025, 3, 14)):
    return type(
        "Member", (), {"id": id, "name": name, "nick": nick, "joined_at": joined_at}
    )()


def _fake_guild(members):
    return type("Guild", (), {"members": members})()


def test_load__expect_every_member_as_a_row():
    bot = _fake_bot(_fake_guild([_fake_member(1, "ada", nick="Ada L.")]))

    rows, total = load({"bot": bot}, TableQuery(limit=5))

    assert rows == [
        {
            "id": 1,
            "name": "ada",
            "nickname": "Ada L.",
            "joined at": "Fri 14 Mar 2025",
        }
    ]
    assert total == 1


def test_load__with_offset_and_limit__expect_that_page_and_the_total():
    members = [_fake_member(i, f"user{i}") for i in range(3)]
    bot = _fake_bot(_fake_guild(members))

    first_rows, first_total = load({"bot": bot}, TableQuery(limit=2))
    second_rows, second_total = load({"bot": bot}, TableQuery(offset=2, limit=2))

    assert [row["id"] for row in first_rows] == [0, 1]
    assert [row["id"] for row in second_rows] == [2]
    assert first_total == second_total == 3


def test_load__with_search__expect_matching_name_or_nickname_only():
    members = [
        _fake_member(1, "ada", nick="Countess"),
        _fake_member(2, "grace"),
        _fake_member(3, "linus", nick="ADA fan"),
    ]
    bot = _fake_bot(_fake_guild(members))

    rows, total = load({"bot": bot}, TableQuery(search="ada", limit=10))

    assert [row["id"] for row in rows] == [1, 3]
    assert total == 2


def test_load__sorted_by_joined_at__expect_date_order_not_text_order():
    members = [
        _fake_member(1, "ada", joined_at=datetime(2025, 3, 14)),  # "Fri ..."
        _fake_member(2, "grace", joined_at=datetime(2024, 1, 1)),  # "Mon ..."
        _fake_member(3, "linus", joined_at=datetime(2025, 1, 2)),  # "Thu ..."
    ]
    bot = _fake_bot(_fake_guild(members))

    rows, _ = load(
        {"bot": bot}, TableQuery(sort_by="joined at", descending=True, limit=10)
    )

    assert [row["id"] for row in rows] == [1, 3, 2]


def test_load__sorted_by_nickname__expect_missing_nicknames_first():
    members = [
        _fake_member(1, "ada", nick="zed"),
        _fake_member(2, "grace"),
        _fake_member(3, "linus", nick="Bob"),
    ]
    bot = _fake_bot(_fake_guild(members))

    rows, _ = load({"bot": bot}, TableQuery(sort_by="nickname", limit=10))

    assert [row["id"] for row in rows] == [2, 3, 1]


def test_load__with_no_guild__expect_no_rows():
    rows, total = load({"bot": _fake_bot(None)}, TableQuery(limit=5))

    assert rows == []
    assert total == 0
