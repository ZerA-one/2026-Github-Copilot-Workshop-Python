"""Pomodoro のドメインルールを純粋関数として提供する。"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping, Protocol

WORK_MODE = "work"
SHORT_BREAK_MODE = "short_break"
LONG_BREAK_MODE = "long_break"
BREAK_MODES = frozenset({SHORT_BREAK_MODE, LONG_BREAK_MODE})
SUPPORTED_MODES = frozenset({WORK_MODE, *BREAK_MODES})


class Clock(Protocol):
	def now(self) -> datetime: ...


class SystemClock:
	def now(self) -> datetime:
		return datetime.now()


def should_take_long_break(
	completed_count: int,
	cycles_before_long_break: int,
) -> bool:
	if completed_count < 0:
		raise ValueError("completed_count must be zero or greater")
	if cycles_before_long_break <= 0:
		raise ValueError("cycles_before_long_break must be greater than zero")

	return completed_count > 0 and completed_count % cycles_before_long_break == 0


def get_next_mode(
	current_mode: str,
	completed_count: int,
	cycles_before_long_break: int,
) -> str:
	if current_mode not in SUPPORTED_MODES:
		raise ValueError(f"unsupported mode: {current_mode}")

	if current_mode == WORK_MODE:
		if should_take_long_break(completed_count, cycles_before_long_break):
			return LONG_BREAK_MODE
		return SHORT_BREAK_MODE

	return WORK_MODE


def update_daily_stats(
	daily_stats: Mapping[str, Any],
	session_type: str,
	session_seconds: int,
) -> dict[str, Any]:
	if session_type not in SUPPORTED_MODES:
		raise ValueError(f"unsupported session_type: {session_type}")
	if session_seconds < 0:
		raise ValueError("session_seconds must be zero or greater")

	updated_stats = dict(daily_stats)
	updated_stats["completed_count"] = int(updated_stats.get("completed_count", 0))
	updated_stats["focused_seconds"] = int(updated_stats.get("focused_seconds", 0))

	if session_type == WORK_MODE:
		updated_stats["completed_count"] += 1
		updated_stats["focused_seconds"] += session_seconds

	return updated_stats


def build_initial_state(
	settings: Mapping[str, int],
	daily_stats: Mapping[str, Any],
	current_mode: str = WORK_MODE,
) -> dict[str, Any]:
	if current_mode not in SUPPORTED_MODES:
		raise ValueError(f"unsupported mode: {current_mode}")

	settings_snapshot = dict(settings)
	daily_stats_snapshot = dict(daily_stats)

	return {
		"current_mode": current_mode,
		"remaining_seconds": _get_mode_duration_seconds(current_mode, settings_snapshot),
		"settings": settings_snapshot,
		"daily_stats": daily_stats_snapshot,
	}


def _get_mode_duration_seconds(settings_mode: str, settings: Mapping[str, int]) -> int:
	mode_to_minutes_key = {
		WORK_MODE: "work_minutes",
		SHORT_BREAK_MODE: "short_break_minutes",
		LONG_BREAK_MODE: "long_break_minutes",
	}
	minutes = int(settings[mode_to_minutes_key[settings_mode]])
	return minutes * 60
