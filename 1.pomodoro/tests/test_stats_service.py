from datetime import date, datetime

from repositories.stats_repository import JsonStatsRepository
from services.stats_service import StatsService


class FrozenClock:
    def __init__(self, current: datetime) -> None:
        self._current = current

    def now(self) -> datetime:
        return self._current


def test_stats_service_persists_daily_stats_and_session_log(tmp_path) -> None:
    file_path = tmp_path / "stats.json"
    first_service = StatsService(
        JsonStatsRepository(file_path),
        clock=FrozenClock(datetime(2026, 4, 2, 9, 0, 0)),
    )

    result = first_service.complete_session("work", focused_seconds=1500)

    assert result["daily_stats"] == {
        "date": "2026-04-02",
        "completed_count": 1,
        "focused_seconds": 1500,
    }
    assert result["session_log"]["session_type"] == "work"
    assert result["session_log"]["completed"] is True

    second_service = StatsService(
        JsonStatsRepository(file_path),
        clock=FrozenClock(datetime(2026, 4, 2, 10, 0, 0)),
    )

    assert second_service.get_today_stats() == {
        "date": "2026-04-02",
        "completed_count": 1,
        "focused_seconds": 1500,
    }
    assert len(second_service.list_session_logs()) == 1


def test_stats_service_returns_stats_for_requested_date(tmp_path) -> None:
    file_path = tmp_path / "stats.json"
    repository = JsonStatsRepository(file_path)
    repository.save_daily_stats(
        "2026-04-01",
        {"completed_count": 2, "focused_seconds": 3000},
    )
    service = StatsService(
        repository,
        clock=FrozenClock(datetime(2026, 4, 2, 9, 0, 0)),
    )

    assert service.get_stats_for_date(date(2026, 4, 1)) == {
        "date": "2026-04-01",
        "completed_count": 2,
        "focused_seconds": 3000,
    }
    assert service.get_today_stats() == {
        "date": "2026-04-02",
        "completed_count": 0,
        "focused_seconds": 0,
    }
