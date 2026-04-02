"""Pomodoro の純粋関数を提供する。"""

from __future__ import annotations

from typing import Mapping


def determine_next_mode(completed_count: int, cycles_before_long_break: int) -> str:
    if cycles_before_long_break <= 0:
        raise ValueError("cycles_before_long_break must be a positive integer.")

    if completed_count > 0 and completed_count % cycles_before_long_break == 0:
        return "long_break"

    return "short_break"


def update_daily_stats(
    current_stats: Mapping[str, int | str],
    focused_seconds: int,
) -> dict[str, int | str]:
    if not isinstance(focused_seconds, int) or isinstance(focused_seconds, bool) or focused_seconds <= 0:
        raise ValueError("duration_seconds must be a positive integer.")

    return {
        "date": str(current_stats["date"]),
        "completed_count": int(current_stats.get("completed_count", 0)) + 1,
        "focused_seconds": int(current_stats.get("focused_seconds", 0)) + focused_seconds,
    }


def build_initial_state(
    settings: Mapping[str, int],
    stats: Mapping[str, int | str],
) -> dict[str, object]:
    return {
        "mode": "work",
        "remaining_seconds": int(settings["work_minutes"]) * 60,
        "settings": dict(settings),
        "stats": dict(stats),
    }
