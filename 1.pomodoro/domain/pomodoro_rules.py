"""Pomodoro のドメインルール。"""

from collections.abc import Mapping
from typing import Any


DEFAULT_MODE = "work"
MODE_TO_SETTINGS_KEY = {
    "work": "work_minutes",
    "short_break": "short_break_minutes",
    "long_break": "long_break_minutes",
}


def is_long_break_due(
    completed_work_sessions: int,
    cycles_before_long_break: int,
) -> bool:
    """長休憩に入るべきかを返す。"""
    return (
        cycles_before_long_break > 0
        and completed_work_sessions > 0
        and completed_work_sessions % cycles_before_long_break == 0
    )


def determine_next_mode(
    completed_work_sessions: int,
    cycles_before_long_break: int,
    completed_session_type: str,
) -> str:
    """完了したセッション種別に応じて次モードを返す。"""
    if completed_session_type == "work":
        if is_long_break_due(completed_work_sessions, cycles_before_long_break):
            return "long_break"
        return "short_break"
    return DEFAULT_MODE


def normalize_daily_stats(stats: Mapping[str, Any] | None, date_key: str) -> dict[str, Any]:
    """統計データを API 向けの既定形式へ整える。"""
    source = stats or {}
    return {
        "date": str(source.get("date", date_key)),
        "completed_count": int(source.get("completed_count", 0)),
        "focused_seconds": int(source.get("focused_seconds", 0)),
    }


def update_daily_stats(
    stats: Mapping[str, Any] | None,
    session_type: str,
    duration_seconds: int,
    date_key: str,
) -> dict[str, Any]:
    """セッション完了後の統計を返す。"""
    updated = normalize_daily_stats(stats, date_key)
    if session_type == "work":
        updated["completed_count"] += 1
        updated["focused_seconds"] += max(int(duration_seconds), 0)
    return updated


def build_initial_state(
    settings: Mapping[str, int],
    stats: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """初期表示用の状態を組み立てる。"""
    normalized_stats = normalize_daily_stats(stats, date_key=str((stats or {}).get("date", "")))
    return {
        "current_mode": DEFAULT_MODE,
        "seconds_remaining": int(settings["work_minutes"]) * 60,
        "settings": dict(settings),
        "stats": normalized_stats,
    }
