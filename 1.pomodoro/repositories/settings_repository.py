from __future__ import annotations

from copy import deepcopy


DEFAULT_SETTINGS = {
    "work_minutes": 25,
    "short_break_minutes": 5,
    "long_break_minutes": 15,
    "cycles_before_long_break": 4,
}


class InMemorySettingsRepository:
    def __init__(self, initial_settings: dict[str, int] | None = None) -> None:
        self._settings = deepcopy(DEFAULT_SETTINGS)
        if initial_settings:
            self._settings.update(initial_settings)

    def get(self) -> dict[str, int]:
        return deepcopy(self._settings)
