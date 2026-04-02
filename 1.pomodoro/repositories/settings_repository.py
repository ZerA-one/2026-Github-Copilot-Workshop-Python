"""設定リポジトリを提供する。"""

from __future__ import annotations


DEFAULT_SETTINGS = {
    "work_minutes": 25,
    "short_break_minutes": 5,
    "long_break_minutes": 15,
    "cycles_before_long_break": 4,
}


class InMemorySettingsRepository:
    def __init__(self, initial_settings: dict[str, int] | None = None) -> None:
        self._settings = dict(DEFAULT_SETTINGS)

        if initial_settings is not None:
            self._settings.update(initial_settings)

    def get_settings(self) -> dict[str, int]:
        return dict(self._settings)

    def save_settings(self, settings: dict[str, int]) -> dict[str, int]:
        self._settings = dict(settings)
        return self.get_settings()
