from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Protocol

from repositories.stats_repository import DEFAULT_DAILY_STATS, StatsRepository


class Clock(Protocol):
    def now(self) -> datetime:
        """現在時刻を返す。"""


class SystemClock:
    def now(self) -> datetime:
        return datetime.now()


class StatsService:
    def __init__(self, repository: StatsRepository, clock: Clock | None = None) -> None:
        self._repository = repository
        self._clock = clock or SystemClock()

    def get_today_stats(self) -> dict[str, Any]:
        return self.get_stats_for_date(self._clock.now().date())

    def get_stats_for_date(self, target_date: date | str) -> dict[str, Any]:
        date_key = target_date.isoformat() if isinstance(target_date, date) else target_date
        return self._repository.get_daily_stats(date_key)

    def complete_session(
        self,
        session_type: str,
        focused_seconds: int,
        started_at: datetime | None = None,
        ended_at: datetime | None = None,
        completed: bool = True,
    ) -> dict[str, Any]:
        if session_type not in {"work", "short_break", "long_break"}:
            raise ValueError("session_type must be work, short_break, or long_break")
        if not isinstance(focused_seconds, int):
            raise ValueError("focused_seconds must be an integer")
        if focused_seconds < 0:
            raise ValueError("focused_seconds must be zero or greater")

        finished_at = ended_at or self._clock.now()
        begun_at = started_at or finished_at - timedelta(seconds=focused_seconds)
        date_key = finished_at.date().isoformat()

        current_stats = self._repository.get_daily_stats(date_key)
        next_stats = dict(DEFAULT_DAILY_STATS)
        next_stats.update(
            {
                "completed_count": current_stats["completed_count"],
                "focused_seconds": current_stats["focused_seconds"],
            }
        )

        if completed and session_type == "work":
            next_stats["completed_count"] += 1
            next_stats["focused_seconds"] += focused_seconds

        saved_stats = self._repository.save_daily_stats(date_key, next_stats)
        saved_session = self._repository.append_session_log(
            {
                "started_at": begun_at.isoformat(),
                "ended_at": finished_at.isoformat(),
                "session_type": session_type,
                "completed": completed,
                "focused_seconds": focused_seconds,
            }
        )

        return {
            "daily_stats": saved_stats,
            "session_log": saved_session,
        }

    def reset_today(self) -> dict[str, Any]:
        return self._repository.reset_daily_stats(self._clock.now().date().isoformat())

    def list_session_logs(self) -> list[dict[str, Any]]:
        return self._repository.list_session_logs()
