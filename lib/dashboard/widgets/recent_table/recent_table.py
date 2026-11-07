from dataclasses import KW_ONLY, dataclass
from typing import Any, Sequence

from dachshund.storage import Event
from dachshund.widgets import Table


@dataclass
class RecentTable(Table):
    """A row per event of its source, newest first.

    The newest `keep` events stay in the event store, across restarts, where a
    plain `Table` only keeps its newest one once events are compacted.

    ## Example

    ```python
    with dachshund.row():
        dachshund.add(RecentTable("errors", columns=["command", "error"], keep=50))
    dachshund.emit("errors", command="weather", error="Timeout")
    ```
    """

    _: KW_ONLY

    keep: int = 50

    def __post_init__(self) -> None:
        if self.persist:
            raise ValueError(
                f"{self.name!r} keeps its rows in the event store, give it "
                "`keep` instead of persist=True."
            )

        super().__post_init__()

        if self.keep < 1:
            raise ValueError(f"{self.name!r} has keep={self.keep}, keep at least 1.")

    def render(self, events: Sequence[Event]) -> dict[str, Any]:
        """The newest `keep` rows, newest first."""
        payload = super().render(events)
        payload["rows"] = payload["rows"][-self.keep :][::-1]

        return payload
