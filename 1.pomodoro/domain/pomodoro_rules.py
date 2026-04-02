from __future__ import annotations

from dataclasses import asdict, dataclass


MODE_WORK = "work"
MODE_SHORT_BREAK = "short_break"
MODE_LONG_BREAK = "long_break"

MODE_MINUTES_FIELDS = {
    MODE_WORK: "work_minutes",
    MODE_SHORT_BREAK: "short_break_minutes",
    MODE_LONG_BREAK: "long_break_minutes",
}

FIELD_RANGES = {
    "work_minutes": (1, 120),
    "short_break_minutes": (1, 60),
    "long_break_minutes": (1, 120),
    "cycles_before_long_break": (1, 12),
}


@dataclass(frozen=True)
class PomodoroSettings:
    work_minutes: int = 25
    short_break_minutes: int = 5
    long_break_minutes: int = 15
    cycles_before_long_break: int = 4

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


class SettingsValidationError(ValueError):
    def __init__(self, errors: dict[str, str]) -> None:
        super().__init__("settings validation failed")
        self.errors = errors


def validate_settings(payload: dict[str, object]) -> PomodoroSettings:
    values: dict[str, int] = {}
    errors: dict[str, str] = {}

    for field_name, (minimum, maximum) in FIELD_RANGES.items():
        raw_value = payload.get(field_name)

        if raw_value is None or raw_value == "":
            errors[field_name] = "必須項目です。"
            continue

        try:
            value = int(raw_value)
        except (TypeError, ValueError):
            errors[field_name] = "整数で入力してください。"
            continue

        if not minimum <= value <= maximum:
            errors[field_name] = f"{minimum}〜{maximum} の範囲で入力してください。"
            continue

        values[field_name] = value

    if errors:
        raise SettingsValidationError(errors)

    return PomodoroSettings(**values)


def get_mode_duration_seconds(settings: PomodoroSettings, mode: str) -> int:
    field_name = MODE_MINUTES_FIELDS[mode]
    return getattr(settings, field_name) * 60


def get_next_mode(current_mode: str, completed_work_sessions: int, settings: PomodoroSettings) -> str:
    if current_mode == MODE_WORK:
        if completed_work_sessions % settings.cycles_before_long_break == 0:
            return MODE_LONG_BREAK
        return MODE_SHORT_BREAK

    return MODE_WORK


def build_initial_timer_state(settings: PomodoroSettings) -> dict[str, int | str]:
    return {
        "mode": MODE_WORK,
        "remaining_seconds": get_mode_duration_seconds(settings, MODE_WORK),
        "completed_work_sessions": 0,
    }
