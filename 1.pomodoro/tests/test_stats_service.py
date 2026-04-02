from datetime import date

from repositories.settings_repository import InMemorySettingsRepository
from repositories.stats_repository import InMemoryStatsRepository
from services.settings_service import SettingsService
from services.stats_service import StatsService


def build_service() -> StatsService:
    settings_service = SettingsService(InMemorySettingsRepository())
    return StatsService(
        InMemoryStatsRepository(),
        settings_service,
        today_provider=lambda: date(2026, 4, 2),
    )


def test_complete_work_session_updates_today_stats_and_next_state() -> None:
    service = build_service()

    result = service.complete_session("work", duration_seconds=1500)

    assert result["today_stats"] == {"completed_count": 1, "focused_seconds": 1500}
    assert result["next_state"]["mode"] == "short_break"
    assert result["next_state"]["timer_status"] == "idle"


def test_complete_break_session_keeps_focus_totals() -> None:
    service = build_service()
    service.complete_session("work", duration_seconds=1500)

    result = service.complete_session("short_break", duration_seconds=300)

    assert result["today_stats"] == {"completed_count": 1, "focused_seconds": 1500}
    assert result["next_state"]["mode"] == "work"


def test_reset_today_clears_stats() -> None:
    service = build_service()
    service.complete_session("work", duration_seconds=1500)

    assert service.reset_today() == {"completed_count": 0, "focused_seconds": 0}
