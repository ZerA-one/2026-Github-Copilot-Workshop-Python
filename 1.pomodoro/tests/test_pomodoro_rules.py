from domain.pomodoro_rules import (
    build_initial_state,
    mode_duration_seconds,
    next_mode_after_completion,
    update_daily_stats,
)


def test_work_completion_moves_to_short_break_by_default() -> None:
    assert next_mode_after_completion("work", completed_count=1) == "short_break"


def test_work_completion_moves_to_long_break_on_cycle_boundary() -> None:
    assert next_mode_after_completion("work", completed_count=4) == "long_break"


def test_update_daily_stats_counts_only_work_sessions() -> None:
    updated = update_daily_stats({}, "work", 1500)

    assert updated == {"completed_count": 1, "focused_seconds": 1500}
    assert update_daily_stats(updated, "short_break", 300) == updated


def test_build_initial_state_uses_work_duration_and_empty_stats() -> None:
    state = build_initial_state()

    assert state["mode"] == "work"
    assert state["timer_status"] == "idle"
    assert state["duration_seconds"] == mode_duration_seconds("work")
    assert state["remaining_seconds"] == mode_duration_seconds("work")
    assert state["completed_count"] == 0
    assert state["focused_seconds"] == 0
