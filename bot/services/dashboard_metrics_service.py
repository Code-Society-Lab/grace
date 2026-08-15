from dataclasses import dataclass

import dachshund


@dataclass
class DashboardMetrics:
    highest_latency_ms: int = 0

    def record_latency(self, latency_ms: int, *, is_from_command: bool = False) -> None:
        command_latency_ms = latency_ms if is_from_command else None

        dachshund.emit("latency", check=latency_ms, command=command_latency_ms)

        if latency_ms > self.highest_latency_ms:
            self.highest_latency_ms = latency_ms
            dachshund.emit("highest_latency", value=self.highest_latency_ms)
