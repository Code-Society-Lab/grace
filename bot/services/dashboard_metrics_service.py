from dataclasses import dataclass

import dachshund

EMA_ALPHA = 0.2


@dataclass
class DashboardMetrics:
    lowest_latency_ms: int = 0
    highest_latency_ms: int = 0
    average_latency_ms: float = 0

    @classmethod
    async def load(cls) -> "DashboardMetrics":
        """Rebuild metrics from dachshund's event store."""
        metrics = cls()

        for event in await dachshund.default().events.events("latency"):
            value = event.payload.get("check")

            if value is not None:
                metrics._accumulate(value)

        return metrics

    def _accumulate(self, latency_ms: int) -> None:
        if self.average_latency_ms == 0.0:
            self.average_latency_ms = latency_ms
        else:
            self.average_latency_ms += EMA_ALPHA * (
                latency_ms - self.average_latency_ms
            )

        if latency_ms < self.lowest_latency_ms or self.lowest_latency_ms == 0:
            self.lowest_latency_ms = latency_ms

        if latency_ms > self.highest_latency_ms:
            self.highest_latency_ms = latency_ms

    def record_latency(self, latency_ms: int, *, is_from_command: bool = False) -> None:
        command_latency_ms = latency_ms if is_from_command else None
        dachshund.emit("latency", check=latency_ms, command=command_latency_ms)

        previous_lowest = self.lowest_latency_ms
        previous_highest = self.highest_latency_ms

        self._accumulate(latency_ms)

        dachshund.emit("average_latency", value=self.average_latency_ms)

        if self.lowest_latency_ms != previous_lowest:
            dachshund.emit("lowest_latency", value=self.lowest_latency_ms)

        if self.highest_latency_ms != previous_highest:
            dachshund.emit("highest_latency", value=self.highest_latency_ms)
