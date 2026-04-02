from repositories.settings_repository import InMemorySettingsRepository
from repositories.stats_repository import InMemoryStatsRepository
from services.settings_service import SettingsService
from services.stats_service import StatsService


def test_complete_session_updates_daily_stats_and_records_session_log(fixed_clock) -> None:
    settings_service = SettingsService(InMemorySettingsRepository())
    stats_service = StatsService(
        InMemoryStatsRepository(),
        settings_service,
        clock=fixed_clock,
    )

    updated_stats = stats_service.complete_session(duration_seconds=1500)
    session_logs = stats_service.list_session_logs()

    assert updated_stats == {
        "date": "2026-04-02",
        "completed_count": 1,
        "focused_seconds": 1500,
    }
    assert len(session_logs) == 1
    assert session_logs[0]["session_type"] == "work"
    assert session_logs[0]["duration_seconds"] == 1500
    assert session_logs[0]["completed"] is True


def test_complete_session_uses_current_work_minutes_when_duration_is_omitted(fixed_clock) -> None:
    settings_repository = InMemorySettingsRepository({"work_minutes": 30})
    settings_service = SettingsService(settings_repository)
    stats_service = StatsService(
        InMemoryStatsRepository(),
        settings_service,
        clock=fixed_clock,
    )

    updated_stats = stats_service.complete_session()

    assert updated_stats["completed_count"] == 1
    assert updated_stats["focused_seconds"] == 1800


def test_reset_today_stats_clears_completed_count_and_focused_seconds(fixed_clock) -> None:
    settings_service = SettingsService(InMemorySettingsRepository())
    stats_service = StatsService(
        InMemoryStatsRepository(),
        settings_service,
        clock=fixed_clock,
    )

    stats_service.complete_session(duration_seconds=1500)
    reset_stats = stats_service.reset_today_stats()

    assert reset_stats == {
        "date": "2026-04-02",
        "completed_count": 0,
        "focused_seconds": 0,
    }


def test_complete_session_rejects_non_positive_duration(fixed_clock) -> None:
    settings_service = SettingsService(InMemorySettingsRepository())
    stats_service = StatsService(
        InMemoryStatsRepository(),
        settings_service,
        clock=fixed_clock,
    )

    try:
        stats_service.complete_session(duration_seconds=0)
    except ValueError as exc:
        assert str(exc) == "duration_seconds must be a positive integer."
    else:
        raise AssertionError("ValueError was not raised for invalid duration.")
