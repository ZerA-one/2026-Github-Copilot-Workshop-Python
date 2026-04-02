"""Pomodoro domain package."""

from .pomodoro_rules import (
	BREAK_MODES,
	LONG_BREAK_MODE,
	SHORT_BREAK_MODE,
	SUPPORTED_MODES,
	SystemClock,
	WORK_MODE,
	build_initial_state,
	get_next_mode,
	should_take_long_break,
	update_daily_stats,
)

__all__ = [
	"BREAK_MODES",
	"LONG_BREAK_MODE",
	"SHORT_BREAK_MODE",
	"SUPPORTED_MODES",
	"SystemClock",
	"WORK_MODE",
	"build_initial_state",
	"get_next_mode",
	"should_take_long_break",
	"update_daily_stats",
]
