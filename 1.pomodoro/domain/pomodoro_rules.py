from __future__ import annotations

from copy import deepcopy
from typing import Mapping


DEFAULT_SETTINGS = {
    "work_minutes": 25,
    "short_break_minutes": 5,
    "long_break_minutes": 15,
    "cycles_before_long_break": 4,
}

DEFAULT_STATS = {
    "completed_count": 0,
    "focused_seconds": 0,
}

VALID_MODES = {"work", "short_break", "long_break"}


def normalize_settings(settings: Mapping[str, object] | None = None) -> dict[str, int]:
    normalized = deepcopy(DEFAULT_SETTINGS)

    if settings is not None:
        for key, value in settings.items():
            if key in normalized:
                normalized[key] = int(value)

    for key, value in normalized.items():
        if value <= 0:
            raise ValueError(f"{key} は 1 以上の整数で指定してください。")

    return normalized


def normalize_stats(stats: Mapping[str, object] | None = None) -> dict[str, int]:
    normalized = deepcopy(DEFAULT_STATS)

    if stats is not None:
        for key, value in stats.items():
            if key in normalized:
                normalized[key] = max(0, int(value))

    return normalized


def mode_duration_seconds(mode: str, settings: Mapping[str, object] | None = None) -> int:
    if mode not in VALID_MODES:
        raise ValueError("不正なモードです。")

    normalized_settings = normalize_settings(settings)

    if mode == "work":
        return normalized_settings["work_minutes"] * 60
    if mode == "short_break":
        return normalized_settings["short_break_minutes"] * 60
    return normalized_settings["long_break_minutes"] * 60


def is_long_break_cycle(
    completed_count: int,
    settings: Mapping[str, object] | None = None,
) -> bool:
    normalized_settings = normalize_settings(settings)
    normalized_count = max(0, int(completed_count))
    cycles = normalized_settings["cycles_before_long_break"]

    return normalized_count > 0 and normalized_count % cycles == 0


def next_mode_after_completion(
    mode: str,
    completed_count: int,
    settings: Mapping[str, object] | None = None,
) -> str:
    if mode not in VALID_MODES:
        raise ValueError("不正なモードです。")

    if mode == "work":
        if is_long_break_cycle(completed_count, settings):
            return "long_break"
        return "short_break"

    return "work"


def update_daily_stats(
    stats: Mapping[str, object] | None,
    mode: str,
    duration_seconds: int,
) -> dict[str, int]:
    if mode not in VALID_MODES:
        raise ValueError("不正なモードです。")

    normalized_stats = normalize_stats(stats)
    normalized_duration = max(0, int(duration_seconds))

    if mode == "work":
        normalized_stats["completed_count"] += 1
        normalized_stats["focused_seconds"] += normalized_duration

    return normalized_stats


def build_initial_state(
    settings: Mapping[str, object] | None = None,
    stats: Mapping[str, object] | None = None,
) -> dict[str, object]:
    normalized_settings = normalize_settings(settings)
    normalized_stats = normalize_stats(stats)
    duration_seconds = mode_duration_seconds("work", normalized_settings)

    return {
        "mode": "work",
        "timer_status": "idle",
        "duration_seconds": duration_seconds,
        "remaining_seconds": duration_seconds,
        "completed_count": normalized_stats["completed_count"],
        "focused_seconds": normalized_stats["focused_seconds"],
        "settings": normalized_settings,
    }


def advance_state_after_completion(
    mode: str,
    stats: Mapping[str, object] | None,
    settings: Mapping[str, object] | None = None,
    duration_seconds: int | None = None,
) -> dict[str, object]:
    normalized_settings = normalize_settings(settings)
    elapsed = (
        int(duration_seconds)
        if duration_seconds is not None
        else mode_duration_seconds(mode, normalized_settings)
    )
    updated_stats = update_daily_stats(stats, mode, elapsed)
    next_mode = next_mode_after_completion(
        mode,
        updated_stats["completed_count"],
        normalized_settings,
    )
    next_duration = mode_duration_seconds(next_mode, normalized_settings)

    return {
        "mode": next_mode,
        "timer_status": "idle",
        "duration_seconds": next_duration,
        "remaining_seconds": next_duration,
        "completed_count": updated_stats["completed_count"],
        "focused_seconds": updated_stats["focused_seconds"],
        "settings": normalized_settings,
        "today_stats": updated_stats,
    }
