"""設定サービス。"""

from collections.abc import Mapping

from repositories.settings_repository import SettingsRepository


class SettingsService:
    """設定の取得と保存を担当する。"""

    def __init__(self, repository: SettingsRepository) -> None:
        self._repository = repository

    def get_settings(self) -> dict[str, int]:
        return self._repository.get_settings()

    def save_settings(self, settings: Mapping[str, int]) -> dict[str, int]:
        return self._repository.save_settings(settings)
