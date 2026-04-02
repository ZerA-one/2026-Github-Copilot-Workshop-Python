from __future__ import annotations


def build_initial_state(
    settings: dict[str, int],
    stats: dict[str, int | str],
) -> dict[str, object]:
    work_seconds = settings["work_minutes"] * 60
    return {
        "mode": "work",
        "status": "idle",
        "remaining_seconds": work_seconds,
        "total_seconds": work_seconds,
        "settings": settings,
        "stats": stats,
    }


def update_daily_stats(
    stats: dict[str, int | str],
    focused_seconds: int,
) -> dict[str, int | str]:
    next_stats = dict(stats)
    next_stats["completed_count"] = int(next_stats["completed_count"]) + 1
    next_stats["focused_seconds"] = int(next_stats["focused_seconds"]) + focused_seconds
    return next_stats
