from datetime import date

from domain.pomodoro_rules import (
    build_initial_display_data,
    determine_next_mode,
    update_daily_stats,
)


def test_determine_next_mode_returns_short_break_after_work_session() -> None:
    next_mode = determine_next_mode(
        current_mode="work",
        completed_count=1,
        cycles_before_long_break=4,
    )

    assert next_mode == "short_break"


def test_determine_next_mode_returns_long_break_when_cycle_target_is_reached() -> None:
    next_mode = determine_next_mode(
        current_mode="work",
        completed_count=4,
        cycles_before_long_break=4,
    )

    assert next_mode == "long_break"


def test_update_daily_stats_increments_today_totals() -> None:
    updated_stats = update_daily_stats(
        {
            "date": "2026-04-02",
            "completed_count": 2,
            "focused_seconds": 3000,
        },
        focused_seconds=1500,
        today=date(2026, 4, 2),
    )

    assert updated_stats == {
        "date": "2026-04-02",
        "completed_count": 3,
        "focused_seconds": 4500,
    }


def test_build_initial_display_data_uses_work_duration_and_today_stats() -> None:
    initial_data = build_initial_display_data(
        {
            "work_minutes": 25,
            "short_break_minutes": 5,
            "long_break_minutes": 15,
            "cycles_before_long_break": 4,
        },
        {
            "date": "2026-04-02",
            "completed_count": 3,
            "focused_seconds": 4500,
        },
    )

    assert initial_data == {
        "current_mode": "work",
        "remaining_seconds": 1500,
        "completed_count": 3,
        "focused_seconds": 4500,
        "settings": {
            "work_minutes": 25,
            "short_break_minutes": 5,
            "long_break_minutes": 15,
            "cycles_before_long_break": 4,
        },
    }
