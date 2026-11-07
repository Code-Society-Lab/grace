from dataclasses import KW_ONLY, dataclass
from typing import Any, Sequence

from dachshund.storage import Event
from dachshund.widgets import BarChart


@dataclass
class TopBarChart(BarChart):
    """A `BarChart` of only its `top` biggest bars, biggest first.

    ## Example

    ```python
    with dachshund.row():
        dachshund.add(TopBarChart("emojis", x="emoji", top=10, persist=True))
    dachshund.emit("emojis", emoji="🔥", value=1)
    ```
    """

    _: KW_ONLY

    top: int = 10

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.top < 1:
            raise ValueError(f"{self.name!r} has top={self.top}, show at least 1.")

    def render(self, events: Sequence[Event]) -> dict[str, Any]:
        payload = super().render(events)
        bars = sorted(
            zip(payload["x"], payload["y"][0]), key=lambda bar: bar[1], reverse=True
        )[: self.top]

        payload["x"] = [category for category, _ in bars]
        payload["y"] = [[value for _, value in bars]]

        return payload
