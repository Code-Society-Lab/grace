from typing import Any

from dachshund.widgets import TableQuery

Page = tuple[list[dict[str, Any]], int]


def page_rows(
    rows: list[dict[str, Any]], query: TableQuery, columns: list[str]
) -> Page:
    """`query`'s page of `rows`: searched across `columns`, sorted, then sliced."""
    if query.search:
        needle = query.search.lower()
        rows = [
            row
            for row in rows
            if any(needle in str(row.get(column, "")).lower() for column in columns)
        ]

    if query.sort_by in columns:
        rows = sorted(
            rows,
            key=lambda row: str(row.get(query.sort_by, "")).lower(),
            reverse=query.descending,
        )

    return rows[query.offset : query.offset + query.limit], len(rows)
