from datetime import datetime

import pytest

from domain.pomodoro_rules import (
	LONG_BREAK_MODE,
	SHORT_BREAK_MODE,
	SystemClock,
	WORK_MODE,
	build_initial_state,
	get_next_mode,
	should_take_long_break,
	update_daily_stats,
)


def test_should_take_long_break_returns_true_at_configured_cycle() -> None:
	assert should_take_long_break(completed_count=4, cycles_before_long_break=4) is True


def test_get_next_mode_returns_short_break_after_regular_work_session() -> None:
	assert (
		get_next_mode(
			current_mode=WORK_MODE,
			completed_count=3,
			cycles_before_long_break=4,
		)
		== SHORT_BREAK_MODE
	)


def test_get_next_mode_returns_long_break_after_threshold_work_session() -> None:
	assert (
		get_next_mode(
			current_mode=WORK_MODE,
			completed_count=4,
			cycles_before_long_break=4,
		)
		== LONG_BREAK_MODE
	)


def test_get_next_mode_returns_work_after_break() -> None:
	assert (
		get_next_mode(
			current_mode=SHORT_BREAK_MODE,
			completed_count=1,
			cycles_before_long_break=4,
		)
		== WORK_MODE
	)


def test_update_daily_stats_accumulates_completed_work_session_without_mutating_input() -> None:
	original_stats = {
		"date": "2026-04-02",
		"completed_count": 2,
		"focused_seconds": 3000,
	}

	updated_stats = update_daily_stats(
		daily_stats=original_stats,
		session_type=WORK_MODE,
		session_seconds=1500,
	)

	assert updated_stats == {
		"date": "2026-04-02",
		"completed_count": 3,
		"focused_seconds": 4500,
	}
	assert original_stats == {
		"date": "2026-04-02",
		"completed_count": 2,
		"focused_seconds": 3000,
	}


def test_update_daily_stats_ignores_break_sessions() -> None:
	assert update_daily_stats(
		daily_stats={"date": "2026-04-02", "completed_count": 1, "focused_seconds": 1500},
		session_type=LONG_BREAK_MODE,
		session_seconds=900,
	) == {
		"date": "2026-04-02",
		"completed_count": 1,
		"focused_seconds": 1500,
	}


def test_build_initial_state_uses_work_duration_and_copies_input_data() -> None:
	settings = {
		"work_minutes": 25,
		"short_break_minutes": 5,
		"long_break_minutes": 15,
		"cycles_before_long_break": 4,
	}
	daily_stats = {
		"date": "2026-04-02",
		"completed_count": 3,
		"focused_seconds": 4500,
	}

	initial_state = build_initial_state(settings=settings, daily_stats=daily_stats)

	assert initial_state == {
		"current_mode": WORK_MODE,
		"remaining_seconds": 1500,
		"settings": settings,
		"daily_stats": daily_stats,
	}
	assert initial_state["settings"] is not settings
	assert initial_state["daily_stats"] is not daily_stats


def test_system_clock_returns_datetime_instance() -> None:
	assert isinstance(SystemClock().now(), datetime)


def test_should_take_long_break_rejects_invalid_cycle_configuration() -> None:
	with pytest.raises(ValueError):
		should_take_long_break(completed_count=1, cycles_before_long_break=0)
