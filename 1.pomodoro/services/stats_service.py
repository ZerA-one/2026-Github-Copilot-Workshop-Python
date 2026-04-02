from __future__ import annotations

from datetime import date

from domain.pomodoro_rules import (
    advance_state_after_completion,
    build_initial_state,
    normalize_stats,
)


class StatsService:
    def __init__(self, repository, settings_service, today_provider=None) -> None:
        self.repository = repository
        self.settings_service = settings_service
        self.today_provider = today_provider or date.today

    def _today_key(self) -> str:
        return self.today_provider().isoformat()

    def get_today_stats(self) -> dict[str, int]:
        return normalize_stats(
            self.repository.get_stats_for_date(self._today_key()),
        )

    def reset_today(self) -> dict[str, int]:
        self.repository.reset_stats_for_date(self._today_key())
        return self.get_today_stats()

    def get_initial_state(self) -> dict[str, object]:
        return build_initial_state(
            self.settings_service.get_settings(),
            self.get_today_stats(),
        )

    def complete_session(
        self,
        mode: str,
        duration_seconds: int | None = None,
    ) -> dict[str, object]:
        next_state = advance_state_after_completion(
            mode,
            self.get_today_stats(),
            self.settings_service.get_settings(),
            duration_seconds=duration_seconds,
        )
        today_stats = normalize_stats(next_state["today_stats"])
        self.repository.save_stats_for_date(self._today_key(), today_stats)

        return {
            "today_stats": today_stats,
            "next_state": {
                "mode": next_state["mode"],
                "timer_status": next_state["timer_status"],
                "duration_seconds": next_state["duration_seconds"],
                "remaining_seconds": next_state["remaining_seconds"],
                "completed_count": next_state["completed_count"],
                "focused_seconds": next_state["focused_seconds"],
                "settings": next_state["settings"],
            },
        }
