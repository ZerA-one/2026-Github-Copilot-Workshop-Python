"""設定サービスを提供する。"""

from __future__ import annotations

from repositories.settings_repository import DEFAULT_SETTINGS, InMemorySettingsRepository


class SettingsValidationError(ValueError):
    """設定値が不正な場合の例外。"""


class SettingsService:
    def __init__(self, repository: InMemorySettingsRepository) -> None:
        self._repository = repository

    def get_settings(self) -> dict[str, int]:
        return self._repository.get_settings()

    def update_settings(self, payload: object) -> dict[str, int]:
        if not isinstance(payload, dict) or not payload:
            raise SettingsValidationError("settings payload must be a non-empty JSON object.")

        unknown_keys = set(payload) - set(DEFAULT_SETTINGS)
        if unknown_keys:
            raise SettingsValidationError("settings payload contains unsupported keys.")

        current_settings = self._repository.get_settings()
        updated_settings = dict(current_settings)

        for key, value in payload.items():
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise SettingsValidationError(f"{key} must be a positive integer.")

            updated_settings[key] = value

        return self._repository.save_settings(updated_settings)
