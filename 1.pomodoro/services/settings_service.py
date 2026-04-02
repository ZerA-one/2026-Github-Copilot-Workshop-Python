from __future__ import annotations

from typing import Any

from repositories.settings_repository import DEFAULT_SETTINGS, SettingsRepository


class SettingsService:
    def __init__(self, repository: SettingsRepository) -> None:
        self._repository = repository

    def get_settings(self) -> dict[str, int]:
        return self._repository.get_settings()

    def update_settings(self, payload: dict[str, Any]) -> dict[str, int]:
        current_settings = self._repository.get_settings()
        merged_settings = {**current_settings, **payload}
        validated_settings = self._validate_settings(merged_settings)
        return self._repository.save_settings(validated_settings)

    def _validate_settings(self, settings: dict[str, Any]) -> dict[str, int]:
        validated_settings: dict[str, int] = {}

        for key in DEFAULT_SETTINGS:
            if key not in settings:
                raise ValueError(f"{key} is required")

            value = settings[key]
            if not isinstance(value, int):
                raise ValueError(f"{key} must be an integer")
            if value <= 0:
                raise ValueError(f"{key} must be greater than zero")

            validated_settings[key] = value

        unknown_keys = set(settings) - set(DEFAULT_SETTINGS)
        if unknown_keys:
            raise ValueError(f"Unknown settings: {', '.join(sorted(unknown_keys))}")

        return validated_settings
