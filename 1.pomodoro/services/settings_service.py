from __future__ import annotations

from domain.pomodoro_rules import PomodoroSettings, validate_settings
from repositories.settings_repository import InMemorySettingsRepository


class SettingsService:
    def __init__(self, repository: InMemorySettingsRepository) -> None:
        self._repository = repository

    def get_settings(self) -> PomodoroSettings:
        return self._repository.get_settings()

    def update_settings(self, payload: dict[str, object]) -> PomodoroSettings:
        settings = validate_settings(payload)
        return self._repository.save_settings(settings)
