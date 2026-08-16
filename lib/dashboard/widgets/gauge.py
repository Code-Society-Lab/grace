from dataclasses import KW_ONLY, dataclass
from pathlib import Path
from typing import Any, ClassVar, Sequence

from dachshund import Widget
from dachshund.storage.events import Event


@dataclass
class Gauge(Widget):
    """The latest number from its source, as an arc gauge with green/amber/red zones.

    `y` names the field read and defaults to `value`. `warning_at`/`critical_at`
    default to 60%/85% of the way across `[min, max]` when not given.

    ## Example

    ```python
    dachshund.widget("cpu", type="gauge", title="CPU Load", max=100, unit="%")
    dachshund.emit("cpu", value=42)
    ```
    """

    _: KW_ONLY

    y: str = "value"
    min: float = 0
    max: float = 100
    warning_at: float | None = None
    critical_at: float | None = None
    unit: str | None = None

    type: ClassVar[str] = "gauge"
    op: ClassVar[str] = "replace"
    script: ClassVar[Path] = Path(__file__).parent / "gauge.js"
    style: ClassVar[Path] = Path(__file__).parent / "gauge.css"

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.max <= self.min:
            raise ValueError("A gauge's max must be greater than its min.")

        span = self.max - self.min

        if self.warning_at is None:
            self.warning_at = self.min + span * 0.6
        if self.critical_at is None:
            self.critical_at = self.min + span * 0.85

    def render(self, events: Sequence[Event]) -> dict[str, Any]:
        """The most recent reading of `y`, plus the range/zone config the arc needs."""
        return {
            "value": self.value(events[-1], self.y) if events else None,
            "min": self.min,
            "max": self.max,
            "warning_at": self.warning_at,
            "critical_at": self.critical_at,
            "unit": self.unit,
        }
