"""統計リポジトリを提供する。"""

from __future__ import annotations


def build_empty_daily_stats(date_text: str) -> dict[str, int | str]:
    return {
        "date": date_text,
        "completed_count": 0,
        "focused_seconds": 0,
    }


class InMemoryStatsRepository:
    def __init__(self) -> None:
        self._daily_stats: dict[str, dict[str, int | str]] = {}
        self._session_logs: list[dict[str, object]] = []

    def get_daily_stats(self, date_text: str) -> dict[str, int | str]:
        return dict(self._daily_stats.get(date_text, build_empty_daily_stats(date_text)))

    def save_daily_stats(self, stats: dict[str, int | str]) -> dict[str, int | str]:
        date_text = str(stats["date"])
        self._daily_stats[date_text] = dict(stats)
        return self.get_daily_stats(date_text)

    def add_session_log(self, session_log: dict[str, object]) -> dict[str, object]:
        saved_log = dict(session_log)
        self._session_logs.append(saved_log)
        return dict(saved_log)

    def list_session_logs(self) -> list[dict[str, object]]:
        return [dict(log) for log in self._session_logs]

    def reset_daily_stats(self, date_text: str) -> dict[str, int | str]:
        self._daily_stats[date_text] = build_empty_daily_stats(date_text)
        return self.get_daily_stats(date_text)
