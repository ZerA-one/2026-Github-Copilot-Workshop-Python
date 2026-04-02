from pathlib import Path
from datetime import datetime

from flask import Flask, jsonify, render_template, request

from repositories.settings_repository import JsonSettingsRepository, SettingsRepository
from repositories.stats_repository import JsonStatsRepository, StatsRepository
from services.settings_service import SettingsService
from services.stats_service import Clock, StatsService


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def create_app(
    *,
    storage_dir: Path | None = None,
    settings_repository: SettingsRepository | None = None,
    stats_repository: StatsRepository | None = None,
    clock: Clock | None = None,
) -> Flask:
    active_storage_dir = Path(storage_dir) if storage_dir else DATA_DIR
    settings_service = SettingsService(
        settings_repository or JsonSettingsRepository(active_storage_dir / "settings.json")
    )
    stats_service = StatsService(
        stats_repository or JsonStatsRepository(active_storage_dir / "stats.json"),
        clock=clock,
    )

    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )

    @app.get("/")
    def index() -> str:
        return render_template("index.html")

    @app.get("/api/state")
    def get_state():
        settings = settings_service.get_settings()
        today_stats = stats_service.get_today_stats()

        return jsonify(
            {
                "settings": settings,
                "today_stats": today_stats,
                "session_log": stats_service.list_session_logs(),
                "current_mode": "work",
                "remaining_seconds": settings["work_minutes"] * 60,
            }
        )

    @app.get("/api/stats/today")
    def get_today_stats():
        return jsonify(stats_service.get_today_stats())

    @app.post("/api/settings")
    def update_settings():
        payload = request.get_json(silent=True) or {}

        try:
            settings = settings_service.update_settings(payload)
        except ValueError as error:
            return jsonify({"error": str(error)}), 400

        return jsonify({"settings": settings})

    @app.post("/api/session/complete")
    def complete_session():
        payload = request.get_json(silent=True) or {}
        session_type = payload.get("session_type", "work")
        focused_seconds = payload.get("focused_seconds", 0)

        try:
            started_at = _parse_datetime(payload.get("started_at"))
            ended_at = _parse_datetime(payload.get("ended_at"))
            result = stats_service.complete_session(
                session_type=session_type,
                focused_seconds=focused_seconds,
                started_at=started_at,
                ended_at=ended_at,
                completed=payload.get("completed", True),
            )
        except ValueError as error:
            return jsonify({"error": str(error)}), 400

        return jsonify(result)

    @app.post("/api/session/reset")
    def reset_session():
        return jsonify({"daily_stats": stats_service.reset_today()})

    return app


def _parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None

    try:
        return datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("started_at and ended_at must be ISO 8601 datetime strings") from error


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
