from unittest.mock import patch

from bot.services import process_stats_service
from bot.services.process_stats_service import ProcessStats, memory_mb


def test_memory_mb__expect_this_process_uses_some():
    assert memory_mb() > 0


def test_sample__expect_cpu_percent_of_one_core_since_last_sample():
    stats = ProcessStats(_cpu=10.0, _at=100.0)

    with (
        patch.object(process_stats_service, "_cpu_seconds", return_value=10.5),
        patch.object(process_stats_service.time, "monotonic", return_value=102.0),
        patch.object(process_stats_service, "memory_mb", return_value=123.456),
    ):
        sample = stats.sample()

    assert sample == {"memory_mb": 123.5, "cpu_percent": 25.0}


def test_uptime__expect_days_hours_minutes():
    stats = ProcessStats(started_at=0)

    assert stats.uptime(now=2 * 86400 + 3 * 3600 + 4 * 60 + 59) == "2 d 3 h 4 min"
    assert stats.uptime(now=3600) == "1 h"
    assert stats.uptime(now=30) == "0 min"
