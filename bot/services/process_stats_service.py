import os
import resource
import time
from dataclasses import dataclass, field

# Set on first import, which is once per process: reloading a cog keeps it.
PROCESS_STARTED_AT = time.time()


def memory_mb() -> float:
    """The process's resident memory, in MB.

    Read from /proc on Linux; elsewhere, the peak, the closest the standard
    library offers.
    """
    try:
        with open("/proc/self/statm") as statm:
            pages = int(statm.read().split()[1])

        return pages * os.sysconf("SC_PAGE_SIZE") / 1024**2
    except (OSError, ValueError, IndexError):
        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # KB on Linux, bytes on macOS.
        return peak / 1024**2 if os.uname().sysname == "Darwin" else peak / 1024


def _cpu_seconds() -> float:
    times = os.times()
    return times.user + times.system


@dataclass
class ProcessStats:
    """CPU use since the previous sample, and memory, of this process."""

    started_at: float = PROCESS_STARTED_AT
    _cpu: float = field(default_factory=_cpu_seconds)
    _at: float = field(default_factory=time.monotonic)

    def sample(self) -> dict[str, float]:
        """Memory in MB, and CPU as a percent of one core since the last sample."""
        cpu, at = _cpu_seconds(), time.monotonic()
        elapsed = at - self._at
        percent = (cpu - self._cpu) / elapsed * 100 if elapsed > 0 else 0.0
        self._cpu, self._at = cpu, at

        return {
            "memory_mb": round(memory_mb(), 1),
            "cpu_percent": round(percent, 1),
        }

    def uptime(self, now: float | None = None) -> str:
        """How long the process has run, like "2 d 3 h 4 min"."""
        seconds = int((time.time() if now is None else now) - self.started_at)
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes = seconds // 60
        parts = [(days, "d"), (hours, "h"), (minutes, "min")]

        return " ".join(f"{n} {unit}" for n, unit in parts if n) or "0 min"
