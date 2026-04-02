"""統計サービス。"""

from datetime import timedelta
from typing import Any

from domain.clock import Clock
from domain.pomodoro_rules import (
    MODE_TO_SETTINGS_KEY,
    build_initial_state,
    determine_next_mode,
    update_daily_stats,
)
from repositories.stats_repository import StatsRepository
from services.settings_service import SettingsService


class StatsService:
    """統計更新とセッション完了処理を担当する。"""

    def __init__(
        self,
        repository: StatsRepository,
        settings_service: SettingsService,
        clock: Clock,
    ) -> None:
        self._repository = repository
        self._settings_service = settings_service
        self._clock = clock

    def get_today_stats(self) -> dict[str, Any]:
        return self._repository.get_today_stats(self._today_key())

    def get_state(self) -> dict[str, Any]:
        return build_initial_state(
            self._settings_service.get_settings(),
            self.get_today_stats(),
        )

    def complete_session(
        self,
        session_type: str,
        duration_seconds: int,
    ) -> dict[str, Any]:
        normalized_session_type = session_type if session_type in MODE_TO_SETTINGS_KEY else "work"
        normalized_duration = max(int(duration_seconds), 0)
        now = self._clock.now()
        today_key = self._today_key()

        current_stats = self._repository.get_today_stats(today_key)
        updated_stats = update_daily_stats(
            current_stats,
            normalized_session_type,
            normalized_duration,
            today_key,
        )
        saved_stats = self._repository.save_today_stats(today_key, updated_stats)

        self._repository.record_session(
            {
                "started_at": (now - timedelta(seconds=normalized_duration)).isoformat(),
                "ended_at": now.isoformat(),
                "session_type": normalized_session_type,
                "completed": True,
                "duration_seconds": normalized_duration,
            }
        )

        settings = self._settings_service.get_settings()
        next_mode = determine_next_mode(
            saved_stats["completed_count"],
            settings["cycles_before_long_break"],
            normalized_session_type,
        )
        return {
            "current_mode": next_mode,
            "seconds_remaining": int(settings[MODE_TO_SETTINGS_KEY[next_mode]]) * 60,
            "stats": saved_stats,
        }

    def reset_today_stats(self) -> dict[str, Any]:
        return self._repository.reset_today_stats(self._today_key())

    def _today_key(self) -> str:
        return self._clock.today().isoformat()
