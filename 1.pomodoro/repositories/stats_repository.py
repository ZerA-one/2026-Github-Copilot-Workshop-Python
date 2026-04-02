from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Protocol


DEFAULT_DAILY_STATS = {
    "completed_count": 0,
    "focused_seconds": 0,
}


class StatsRepository(Protocol):
    def get_daily_stats(self, target_date: str) -> dict[str, Any]:
        """指定日の統計を返す。"""

    def save_daily_stats(self, target_date: str, stats: dict[str, int]) -> dict[str, Any]:
        """指定日の統計を保存する。"""

    def reset_daily_stats(self, target_date: str) -> dict[str, Any]:
        """指定日の統計をリセットする。"""

    def append_session_log(self, session_entry: dict[str, Any]) -> dict[str, Any]:
        """セッション履歴を追加する。"""

    def list_session_logs(self) -> list[dict[str, Any]]:
        """保存されているセッション履歴を返す。"""


class InMemoryStatsRepository:
    def __init__(
        self,
        initial_daily_stats: dict[str, dict[str, int]] | None = None,
        initial_session_log: list[dict[str, Any]] | None = None,
    ) -> None:
        self._daily_stats = deepcopy(initial_daily_stats or {})
        self._session_log = deepcopy(initial_session_log or [])

    def get_daily_stats(self, target_date: str) -> dict[str, Any]:
        stats = self._daily_stats.get(target_date, dict(DEFAULT_DAILY_STATS))
        return {"date": target_date, **stats}

    def save_daily_stats(self, target_date: str, stats: dict[str, int]) -> dict[str, Any]:
        self._daily_stats[target_date] = {**DEFAULT_DAILY_STATS, **stats}
        return self.get_daily_stats(target_date)

    def reset_daily_stats(self, target_date: str) -> dict[str, Any]:
        self._daily_stats[target_date] = dict(DEFAULT_DAILY_STATS)
        return self.get_daily_stats(target_date)

    def append_session_log(self, session_entry: dict[str, Any]) -> dict[str, Any]:
        entry = deepcopy(session_entry)
        self._session_log.append(entry)
        return entry

    def list_session_logs(self) -> list[dict[str, Any]]:
        return deepcopy(self._session_log)


class JsonStatsRepository:
    def __init__(self, file_path: Path | str) -> None:
        self._file_path = Path(file_path)

    def get_daily_stats(self, target_date: str) -> dict[str, Any]:
        data = self._read_data()
        stats = data["daily_stats"].get(target_date, dict(DEFAULT_DAILY_STATS))
        return {"date": target_date, **stats}

    def save_daily_stats(self, target_date: str, stats: dict[str, int]) -> dict[str, Any]:
        data = self._read_data()
        data["daily_stats"][target_date] = {**DEFAULT_DAILY_STATS, **stats}
        self._write_data(data)
        return {"date": target_date, **data["daily_stats"][target_date]}

    def reset_daily_stats(self, target_date: str) -> dict[str, Any]:
        return self.save_daily_stats(target_date, dict(DEFAULT_DAILY_STATS))

    def append_session_log(self, session_entry: dict[str, Any]) -> dict[str, Any]:
        data = self._read_data()
        entry = deepcopy(session_entry)
        data["session_log"].append(entry)
        self._write_data(data)
        return entry

    def list_session_logs(self) -> list[dict[str, Any]]:
        data = self._read_data()
        return deepcopy(data["session_log"])

    def _read_data(self) -> dict[str, Any]:
        if not self._file_path.exists():
            data = {"daily_stats": {}, "session_log": []}
            self._write_data(data)
            return data

        try:
            with self._file_path.open("r", encoding="utf-8") as file:
                loaded = json.load(file)
        except json.JSONDecodeError:
            loaded = {"daily_stats": {}, "session_log": []}
            self._write_data(loaded)

        if not isinstance(loaded, dict):
            loaded = {}

        daily_stats = loaded.get("daily_stats")
        session_log = loaded.get("session_log")

        return {
            "daily_stats": daily_stats if isinstance(daily_stats, dict) else {},
            "session_log": session_log if isinstance(session_log, list) else [],
        }

    def _write_data(self, data: dict[str, Any]) -> None:
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self._file_path.with_suffix(f"{self._file_path.suffix}.tmp")

        with temp_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

        temp_path.replace(self._file_path)
