from __future__ import annotations

from domain.pomodoro_rules import PomodoroSettings


class InMemorySettingsRepository:
    def __init__(self, initial_settings: PomodoroSettings | None = None) -> None:
        self._settings = initial_settings or PomodoroSettings()

    def get_settings(self) -> PomodoroSettings:
        return self._settings

    def save_settings(self, settings: PomodoroSettings) -> PomodoroSettings:
        self._settings = settings
        return self._settings
