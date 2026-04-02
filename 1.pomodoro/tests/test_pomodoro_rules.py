from domain.pomodoro_rules import (
    MODE_LONG_BREAK,
    MODE_SHORT_BREAK,
    MODE_WORK,
    PomodoroSettings,
    build_initial_timer_state,
    get_mode_duration_seconds,
    get_next_mode,
    validate_settings,
)


def test_validate_settings_creates_settings_model() -> None:
    settings = validate_settings(
        {
            "work_minutes": 30,
            "short_break_minutes": 7,
            "long_break_minutes": 20,
            "cycles_before_long_break": 3,
        }
    )

    assert settings == PomodoroSettings(
        work_minutes=30,
        short_break_minutes=7,
        long_break_minutes=20,
        cycles_before_long_break=3,
    )


def test_get_mode_duration_seconds_uses_selected_setting() -> None:
    settings = PomodoroSettings(work_minutes=30, short_break_minutes=7, long_break_minutes=20)

    assert get_mode_duration_seconds(settings, MODE_WORK) == 1800
    assert get_mode_duration_seconds(settings, MODE_SHORT_BREAK) == 420
    assert get_mode_duration_seconds(settings, MODE_LONG_BREAK) == 1200


def test_get_next_mode_returns_long_break_at_configured_cycle() -> None:
    settings = PomodoroSettings(cycles_before_long_break=2)

    assert get_next_mode(MODE_WORK, 1, settings) == MODE_SHORT_BREAK
    assert get_next_mode(MODE_WORK, 2, settings) == MODE_LONG_BREAK
    assert get_next_mode(MODE_SHORT_BREAK, 2, settings) == MODE_WORK


def test_build_initial_timer_state_uses_work_duration() -> None:
    settings = PomodoroSettings(work_minutes=40)

    assert build_initial_timer_state(settings) == {
        "mode": MODE_WORK,
        "remaining_seconds": 2400,
        "completed_work_sessions": 0,
    }
