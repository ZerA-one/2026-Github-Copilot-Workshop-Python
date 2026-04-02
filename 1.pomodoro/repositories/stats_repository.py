from __future__ import annotations

from copy import deepcopy
from datetime import date


class InMemoryStatsRepository:
    def __init__(self) -> None:
        self._daily_stats: dict[str, dict[str, int | str]] = {}
        self._session_log: list[dict[str, int | str | bool]] = []

    def get_today_stats(self) -> dict[str, int | str]:
        today = date.today().isoformat()
        stats = self._daily_stats.setdefault(
            today,
            {
                "date": today,
                "completed_count": 0,
                "focused_seconds": 0,
            },
        )
        return deepcopy(stats)

    def save_today_stats(self, stats: dict[str, int | str]) -> dict[str, int | str]:
        self._daily_stats[str(stats["date"])] = deepcopy(stats)
        return self.get_today_stats()

    def reset_today_stats(self) -> dict[str, int | str]:
        today = date.today().isoformat()
        self._daily_stats[today] = {
            "date": today,
            "completed_count": 0,
            "focused_seconds": 0,
        }
        return self.get_today_stats()

    def add_session_log(self, session: dict[str, int | str | bool]) -> None:
        self._session_log.append(deepcopy(session))
