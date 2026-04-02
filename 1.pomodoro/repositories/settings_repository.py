from __future__ import annotations

from copy import deepcopy
from typing import Mapping


class InMemorySettingsRepository:
    def __init__(self, initial_settings: Mapping[str, object] | None = None) -> None:
        self._settings = deepcopy(dict(initial_settings or {}))

    def get_settings(self) -> dict[str, object]:
        return deepcopy(self._settings)

    def save_settings(self, settings: Mapping[str, object]) -> dict[str, object]:
        self._settings = deepcopy(dict(settings))
        return self.get_settings()
