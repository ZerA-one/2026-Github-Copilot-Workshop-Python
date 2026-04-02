"""Pomodoro のドメインルールを提供する純粋関数群。"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date
from typing import Any


def is_long_break_due(completed_count: int, cycles_before_long_break: int) -> bool:
    """長休憩へ進むべき回数に到達しているか判定する。"""

    if cycles_before_long_break <= 0:
        return False

    return completed_count > 0 and completed_count % cycles_before_long_break == 0


def determine_next_mode(
    current_mode: str,
    completed_count: int,
    cycles_before_long_break: int,
) -> str:
    """現在モードと完了回数から次モードを決定する。"""

    if current_mode == "work":
        if is_long_break_due(completed_count, cycles_before_long_break):
            return "long_break"
        return "short_break"

    if current_mode in {"short_break", "long_break"}:
        return "work"

    raise ValueError(f"Unsupported mode: {current_mode}")


def update_daily_stats(
    daily_stats: Mapping[str, Any] | None,
    *,
    focused_seconds: int,
    today: date,
) -> dict[str, Any]:
    """当日の集計値を更新した新しい辞書を返す。"""

    today_value = today.isoformat()
    current_stats = dict(daily_stats or {})

    if current_stats.get("date") != today_value:
        current_stats = {
            "date": today_value,
            "completed_count": 0,
            "focused_seconds": 0,
        }

    return {
        "date": today_value,
        "completed_count": int(current_stats.get("completed_count", 0)) + 1,
        "focused_seconds": int(current_stats.get("focused_seconds", 0)) + focused_seconds,
    }


def build_initial_display_data(
    settings: Mapping[str, Any],
    daily_stats: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """初期表示に必要な状態データを組み立てる。"""

    current_stats = dict(daily_stats or {})

    return {
        "current_mode": "work",
        "remaining_seconds": int(settings["work_minutes"]) * 60,
        "completed_count": int(current_stats.get("completed_count", 0)),
        "focused_seconds": int(current_stats.get("focused_seconds", 0)),
        "settings": dict(settings),
    }
