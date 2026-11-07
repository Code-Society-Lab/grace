import pytest
from dachshund.widgets import TableQuery

from lib.dashboard.handlers.paging import page_rows

ROWS = [
    {"name": "Banana", "kind": "fruit"},
    {"name": "apple", "kind": "fruit"},
    {"name": "Carrot", "kind": "vegetable"},
]
COLUMNS = ["name", "kind"]


def _query(**kwargs):
    return TableQuery(**{"offset": 0, "limit": 10, **kwargs})


def test_page_rows__expect_every_row_in_order():
    assert page_rows(ROWS, _query(), COLUMNS) == (ROWS, 3)


def test_page_rows__with_search__expect_case_insensitive_match_in_any_column():
    rows, total = page_rows(ROWS, _query(search="VEG"), COLUMNS)

    assert (rows, total) == ([ROWS[2]], 1)


@pytest.mark.parametrize(
    "descending, expected",
    [(False, ["apple", "Banana", "Carrot"]), (True, ["Carrot", "Banana", "apple"])],
)
def test_page_rows__sorted__expect_case_insensitive_order(descending, expected):
    rows, _ = page_rows(ROWS, _query(sort_by="name", descending=descending), COLUMNS)

    assert [row["name"] for row in rows] == expected


def test_page_rows__sorted_by_unknown_column__expect_original_order():
    rows, _ = page_rows(ROWS, _query(sort_by="_hidden"), COLUMNS)

    assert rows == ROWS


def test_page_rows__with_offset_and_limit__expect_that_page_and_the_total():
    rows, total = page_rows(ROWS, _query(offset=1, limit=1), COLUMNS)

    assert (rows, total) == ([ROWS[1]], 3)
