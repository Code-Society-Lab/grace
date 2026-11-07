from dataclasses import KW_ONLY, dataclass
from pathlib import Path
from typing import Any, ClassVar, Sequence

from dachshund.storage import Event
from dachshund.widgets import Widget


@dataclass
class Stat(Widget):
    """The latest value of a field, as short text on a small card.

    For values that aren't numbers, like a version or a commit, where `Number`
    would show "—". Several can read one event, a field each.

    ## Example

    ```python
    with dachshund.row():
        dachshund.add(Stat("commit", source="deployment", y="commit"))
        dachshund.add(Stat("python", source="deployment", y="python"))
    dachshund.emit("deployment", commit="f76ee33", python="3.12.3")
    ```
    """

    _: KW_ONLY

    y: str = "value"

    type: ClassVar[str] = "stat"
    op: ClassVar[str] = "replace"
    script: ClassVar[Path] = Path(__file__).parent / "stat.js"
    style: ClassVar[Path] = Path(__file__).parent / "stat.css"

    def render(self, events: Sequence[Event]) -> dict[str, Any]:
        """The newest event's `y`, as text."""
        value = events[-1].payload.get(self.y) if events else None

        return {"value": None if value is None else str(value)}
