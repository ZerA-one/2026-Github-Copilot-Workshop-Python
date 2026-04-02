from __future__ import annotations


class SettingsService:
    def __init__(self, repository: object) -> None:
        self._repository = repository

    def get_settings(self) -> dict[str, int]:
        return self._repository.get()
