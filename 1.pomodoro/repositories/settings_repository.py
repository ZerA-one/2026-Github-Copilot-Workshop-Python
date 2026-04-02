from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol


DEFAULT_SETTINGS = {
    "work_minutes": 25,
    "short_break_minutes": 5,
    "long_break_minutes": 15,
    "cycles_before_long_break": 4,
}


class SettingsRepository(Protocol):
    def get_settings(self) -> dict[str, int]:
        """保存されている設定を返す。"""

    def save_settings(self, settings: dict[str, int]) -> dict[str, int]:
        """設定を保存し、保存後の値を返す。"""


class InMemorySettingsRepository:
    def __init__(self, initial_settings: dict[str, int] | None = None) -> None:
        self._settings = {**DEFAULT_SETTINGS, **(initial_settings or {})}

    def get_settings(self) -> dict[str, int]:
        return dict(self._settings)

    def save_settings(self, settings: dict[str, int]) -> dict[str, int]:
        self._settings = {**DEFAULT_SETTINGS, **settings}
        return self.get_settings()


class JsonSettingsRepository:
    def __init__(self, file_path: Path | str) -> None:
        self._file_path = Path(file_path)

    def get_settings(self) -> dict[str, int]:
        data = self._read_data()
        settings = data.get("settings")

        if not isinstance(settings, dict):
            settings = dict(DEFAULT_SETTINGS)
            self._write_data({"settings": settings})

        return {**DEFAULT_SETTINGS, **settings}

    def save_settings(self, settings: dict[str, int]) -> dict[str, int]:
        merged_settings = {**DEFAULT_SETTINGS, **settings}
        self._write_data({"settings": merged_settings})
        return dict(merged_settings)

    def _read_data(self) -> dict[str, object]:
        if not self._file_path.exists():
            return {}

        try:
            with self._file_path.open("r", encoding="utf-8") as file:
                loaded = json.load(file)
        except json.JSONDecodeError:
            self._write_data({"settings": dict(DEFAULT_SETTINGS)})
            return {"settings": dict(DEFAULT_SETTINGS)}

        return loaded if isinstance(loaded, dict) else {}

    def _write_data(self, data: dict[str, object]) -> None:
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self._file_path.with_suffix(f"{self._file_path.suffix}.tmp")

        with temp_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

        temp_path.replace(self._file_path)
