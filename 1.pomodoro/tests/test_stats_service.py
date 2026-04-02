from repositories.settings_repository import InMemorySettingsRepository
from repositories.stats_repository import InMemoryStatsRepository
from services.settings_service import SettingsService
from services.stats_service import StatsService


def create_service() -> StatsService:
    settings_service = SettingsService(InMemorySettingsRepository())
    return StatsService(InMemoryStatsRepository(), settings_service)


def test_get_state_uses_default_work_duration_and_empty_stats() -> None:
    service = create_service()

    state = service.get_state()

    assert state["mode"] == "work"
    assert state["remaining_seconds"] == 25 * 60
    assert state["total_seconds"] == 25 * 60
    assert state["stats"]["completed_count"] == 0
    assert state["stats"]["focused_seconds"] == 0


def test_complete_session_and_reset_today_update_stats_from_repository() -> None:
    service = create_service()

    completed_state = service.complete_session(focused_seconds=1500)
    reset_state = service.reset_today()

    assert completed_state["stats"]["completed_count"] == 1
    assert completed_state["stats"]["focused_seconds"] == 1500
    assert reset_state["stats"]["completed_count"] == 0
    assert reset_state["stats"]["focused_seconds"] == 0
