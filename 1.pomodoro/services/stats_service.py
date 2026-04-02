from __future__ import annotations

from domain.pomodoro_rules import build_initial_state, update_daily_stats


class StatsService:
    def __init__(self, repository: object, settings_service: object) -> None:
        self._repository = repository
        self._settings_service = settings_service

    def get_state(self) -> dict[str, object]:
        settings = self._settings_service.get_settings()
        stats = self.get_today_stats()
        return build_initial_state(settings, stats)

    def get_today_stats(self) -> dict[str, int | str]:
        return self._repository.get_today_stats()

    def complete_session(
        self,
        focused_seconds: int,
        session_type: str = "work",
    ) -> dict[str, object]:
        current_stats = self.get_today_stats()
        updated_stats = update_daily_stats(current_stats, focused_seconds)
        self._repository.save_today_stats(updated_stats)
        self._repository.add_session_log(
            {
                "session_type": session_type,
                "completed": True,
                "focused_seconds": focused_seconds,
            }
        )
        return self.get_state()

    def reset_today(self) -> dict[str, object]:
        self._repository.reset_today_stats()
        return self.get_state()
