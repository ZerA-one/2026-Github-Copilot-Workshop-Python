"""統計サービスを提供する。"""

from __future__ import annotations

from datetime import date, datetime
from typing import Protocol

from domain.pomodoro_rules import build_initial_state, update_daily_stats
from repositories.stats_repository import InMemoryStatsRepository
from services.settings_service import SettingsService


class Clock(Protocol):
    def now(self) -> datetime: ...

    def today(self) -> date: ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now()

    def today(self) -> date:
        return self.now().date()


class StatsService:
    def __init__(
        self,
        repository: InMemoryStatsRepository,
        settings_service: SettingsService,
        clock: Clock | None = None,
    ) -> None:
        self._repository = repository
        self._settings_service = settings_service
        self._clock = clock or SystemClock()

    def get_state(self) -> dict[str, object]:
        return build_initial_state(
            self._settings_service.get_settings(),
            self.get_today_stats(),
        )

    def get_today_stats(self) -> dict[str, int | str]:
        return self._repository.get_daily_stats(self._today_text())

    def complete_session(
        self,
        *,
        duration_seconds: int | None = None,
        session_type: str = "work",
    ) -> dict[str, int | str]:
        if duration_seconds is None:
            duration_seconds = self._settings_service.get_settings()["work_minutes"] * 60

        current_stats = self.get_today_stats()
        updated_stats = update_daily_stats(current_stats, duration_seconds)
        saved_stats = self._repository.save_daily_stats(updated_stats)

        self._repository.add_session_log(
            {
                "date": self._today_text(),
                "ended_at": self._clock.now().isoformat(),
                "session_type": session_type,
                "duration_seconds": duration_seconds,
                "completed": True,
            }
        )

        return saved_stats

    def reset_today_stats(self) -> dict[str, int | str]:
        return self._repository.reset_daily_stats(self._today_text())

    def list_session_logs(self) -> list[dict[str, object]]:
        return self._repository.list_session_logs()

    def _today_text(self) -> str:
        return self._clock.today().isoformat()
