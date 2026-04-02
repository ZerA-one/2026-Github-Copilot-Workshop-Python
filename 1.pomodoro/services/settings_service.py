from __future__ import annotations

from typing import Mapping

from domain.pomodoro_rules import normalize_settings


class SettingsService:
    def __init__(self, repository) -> None:
        self.repository = repository

    def get_settings(self) -> dict[str, int]:
        return normalize_settings(self.repository.get_settings())

    def update_settings(self, settings: Mapping[str, object] | None) -> dict[str, int]:
        current = self.get_settings()
        merged = {**current, **dict(settings or {})}
        normalized = normalize_settings(merged)
        self.repository.save_settings(normalized)
        return normalized
