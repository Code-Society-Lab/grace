from dataclasses import KW_ONLY, dataclass
from typing import Any, Sequence
from zoneinfo import ZoneInfo

from dachshund.storage import Event
from dachshund.widgets import Table

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


@dataclass
class RecentTable(Table):
    """A row per event of its source, newest first, with when it happened.

    The newest `keep` events stay in the event store, across restarts, where a
    plain `Table` only keeps its newest one once events are compacted. Each
    row's `time` is its event's, in `timezone`.

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
    timezone: str = "UTC"

    def __post_init__(self) -> None:
        if self.persist:
            raise ValueError(
                f"{self.name!r} keeps its rows in the event store, give it "
                "`keep` instead of persist=True."
            )

        if self.key is not None:
            raise ValueError(f"{self.name!r} shows a row per event, it takes no key.")

        super().__post_init__()

        if self.keep < 1:
            raise ValueError(f"{self.name!r} has keep={self.keep}, keep at least 1.")

        self._zone = ZoneInfo(self.timezone)

    def raw_events(self) -> int | None:
        """Its newest `keep` events."""
        return self.keep

    def render(self, events: Sequence[Event]) -> dict[str, Any]:
        """The newest `keep` rows, newest first, each stamped with its event's time."""
        payload = super().render(events)

        # Without a key, rows and events line up one to one.
        for row, event in zip(payload["rows"], events):
            row["fields"]["time"] = event.at.astimezone(self._zone).strftime(
                TIME_FORMAT
            )

        payload["rows"] = payload["rows"][-self.keep :][::-1]

        return payload
