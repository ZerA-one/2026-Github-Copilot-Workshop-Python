from datetime import datetime

from repositories.settings_repository import InMemorySettingsRepository
from repositories.stats_repository import InMemoryStatsRepository
from services.settings_service import SettingsService
from services.stats_service import StatsService
from tests.test_helpers import FixedClock


def test_stats_service_completes_work_session_and_updates_stats() -> None:
    clock = FixedClock(datetime(2026, 4, 2, 9, 0, 0))
    settings_service = SettingsService(InMemorySettingsRepository())
    stats_repository = InMemoryStatsRepository()
    service = StatsService(stats_repository, settings_service, clock)

    result = service.complete_session("work", 1500)

    assert result["current_mode"] == "short_break"
    assert result["seconds_remaining"] == 5 * 60
    assert result["stats"] == {
        "date": "2026-04-02",
        "completed_count": 1,
        "focused_seconds": 1500,
    }
    assert stats_repository.get_session_logs() == [
        {
            "started_at": "2026-04-02T08:35:00",
            "ended_at": "2026-04-02T09:00:00",
            "session_type": "work",
            "completed": True,
            "duration_seconds": 1500,
        }
    ]


def test_stats_service_uses_long_break_after_configured_cycle() -> None:
    clock = FixedClock(datetime(2026, 4, 2, 12, 0, 0))
    settings_service = SettingsService(InMemorySettingsRepository())
    settings_service.save_settings({"cycles_before_long_break": 2})
    stats_repository = InMemoryStatsRepository(
        initial_daily_stats={
            "2026-04-02": {
                "completed_count": 1,
                "focused_seconds": 1500,
            }
        }
    )
    service = StatsService(stats_repository, settings_service, clock)

    result = service.complete_session("work", 1500)

    assert result["current_mode"] == "long_break"
    assert result["seconds_remaining"] == 15 * 60
    assert result["stats"]["completed_count"] == 2
    assert result["stats"]["focused_seconds"] == 3000


def test_settings_service_persists_settings_in_memory() -> None:
    service = SettingsService(InMemorySettingsRepository())

    saved = service.save_settings({"work_minutes": 30, "short_break_minutes": 10})

    assert saved["work_minutes"] == 30
    assert saved["short_break_minutes"] == 10
    assert service.get_settings()["long_break_minutes"] == 15
