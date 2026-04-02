"""統計リポジトリ。"""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from domain.pomodoro_rules import normalize_daily_stats


class StatsRepository(ABC):
    """統計とセッション記録の保存・取得インターフェース。"""

    @abstractmethod
    def get_today_stats(self, date_key: str) -> dict[str, Any]:
        """指定日の統計を取得する。"""

    @abstractmethod
    def save_today_stats(
        self,
        date_key: str,
        stats: Mapping[str, Any],
    ) -> dict[str, Any]:
        """指定日の統計を保存する。"""

    @abstractmethod
    def record_session(self, session: Mapping[str, Any]) -> dict[str, Any]:
        """セッション完了記録を保存する。"""

    @abstractmethod
    def reset_today_stats(self, date_key: str) -> dict[str, Any]:
        """指定日の統計をリセットする。"""


class InMemoryStatsRepository(StatsRepository):
    """統計の In-memory 実装。"""

    def __init__(
        self,
        initial_daily_stats: Mapping[str, Mapping[str, Any]] | None = None,
    ) -> None:
        self._daily_stats: dict[str, dict[str, Any]] = {}
        self._session_logs: list[dict[str, Any]] = []
        if initial_daily_stats:
            for date_key, stats in initial_daily_stats.items():
                self.save_today_stats(date_key, stats)

    def get_today_stats(self, date_key: str) -> dict[str, Any]:
        return normalize_daily_stats(self._daily_stats.get(date_key), date_key)

    def save_today_stats(
        self,
        date_key: str,
        stats: Mapping[str, Any],
    ) -> dict[str, Any]:
        normalized = normalize_daily_stats(stats, date_key)
        self._daily_stats[date_key] = normalized
        return dict(normalized)

    def record_session(self, session: Mapping[str, Any]) -> dict[str, Any]:
        saved_session = dict(session)
        self._session_logs.append(saved_session)
        return dict(saved_session)

    def reset_today_stats(self, date_key: str) -> dict[str, Any]:
        return self.save_today_stats(date_key, {"date": date_key})

    def get_session_logs(self) -> list[dict[str, Any]]:
        return [dict(session) for session in self._session_logs]
