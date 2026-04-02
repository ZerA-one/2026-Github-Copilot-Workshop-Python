"""設定リポジトリ。"""

from abc import ABC, abstractmethod
from collections.abc import Mapping


DEFAULT_SETTINGS = {
    "work_minutes": 25,
    "short_break_minutes": 5,
    "long_break_minutes": 15,
    "cycles_before_long_break": 4,
}


class SettingsRepository(ABC):
    """設定の保存・取得インターフェース。"""

    @abstractmethod
    def get_settings(self) -> dict[str, int]:
        """設定を取得する。"""

    @abstractmethod
    def save_settings(self, settings: Mapping[str, int]) -> dict[str, int]:
        """設定を保存する。"""


class InMemorySettingsRepository(SettingsRepository):
    """設定の In-memory 実装。"""

    def __init__(self, initial_settings: Mapping[str, int] | None = None) -> None:
        self._settings = dict(DEFAULT_SETTINGS)
        if initial_settings:
            self.save_settings(initial_settings)

    def get_settings(self) -> dict[str, int]:
        return dict(self._settings)

    def save_settings(self, settings: Mapping[str, int]) -> dict[str, int]:
        for key in DEFAULT_SETTINGS:
            if key in settings:
                self._settings[key] = int(settings[key])
        return self.get_settings()
