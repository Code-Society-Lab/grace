from collections import deque
from dataclasses import KW_ONLY, dataclass, field
from datetime import UTC, datetime, tzinfo
from typing import Any, Sequence
from zoneinfo import ZoneInfo

from dachshund.storage import Event
from dachshund.widgets import Table
from dachshund.widgets.table.table import _fields

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


@dataclass
class RecentTable(Table):
    """A row per event of its source, newest first, with when it happened.

    The newest `keep` rows are kept in the dashboard's `storage`, across
    restarts. Each row's `time` is its event's, in `timezone`, the dashboard's
    by default.

    ## Example

    ```python
    with dachshund.row():
        dachshund.add(
            RecentTable("errors", columns=["time", "command", "error"], keep=50)
        )
    dachshund.emit("errors", command="weather", error="Timeout")
    ```
    """

    _: KW_ONLY

    keep: int = 50
    timezone: str | None = None
    persist: bool = field(default=True, init=False)

    _rows: deque[dict[str, Any]] = field(
        default_factory=deque, init=False, repr=False, compare=False
    )
    _dashboard: Any = field(default=None, init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if self.key is not None:
            raise ValueError(f"{self.name!r} shows a row per event, it takes no key.")

        self.persist = False
        super().__post_init__()
        self.persist = True

        if self.keep < 1:
            raise ValueError(f"{self.name!r} has keep={self.keep}, keep at least 1.")

        self._rows = deque(maxlen=self.keep)

    def bind(self, dashboard: Any) -> None:
        self._dashboard = dashboard

    def unbind(self) -> None:
        self._dashboard = None

    @property
    def zone(self) -> tzinfo:
        if self.timezone:
            return ZoneInfo(self.timezone)

        return self._dashboard.timezone if self._dashboard else UTC

    def raw_events(self) -> int | None:
        """Only the newest event, its rows are kept in `storage`."""
        return 1

    def accumulate(self, event: Event) -> None:
        """Add `event` as the newest row."""
        self._rows.append(
            {"at": event.at.timestamp(), "fields": _fields(event.payload)}
        )

    def snapshot(self) -> dict[str, Any]:
        """The kept rows, oldest first."""
        return {"rows": list(self._rows)}

    def restore(self, data: dict[str, Any]) -> None:
        """The newest `keep` rows of a snapshot."""
        self._rows = deque(data.get("rows", []), maxlen=self.keep)

    def render(self, events: Sequence[Event]) -> dict[str, Any]:
        """The kept rows, newest first, each stamped with its event's time."""
        rows = [
            {"fields": {**row["fields"], "time": self._stamp(row["at"])}}
            for row in reversed(self._rows)
        ]

        return {"columns": self.shown, "rows": rows}

    def _stamp(self, at: float) -> str:
        return (
            datetime.fromtimestamp(at, tz=UTC)
            .astimezone(self.zone)
            .strftime(TIME_FORMAT)
        )
