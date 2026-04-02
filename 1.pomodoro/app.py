from pathlib import Path

from flask import Flask, jsonify, render_template, request

from repositories.settings_repository import InMemorySettingsRepository
from repositories.stats_repository import InMemoryStatsRepository
from services.settings_service import SettingsService, SettingsValidationError
from services.stats_service import Clock, StatsService


BASE_DIR = Path(__file__).resolve().parent


def create_app(
    *,
    settings_repository: InMemorySettingsRepository | None = None,
    stats_repository: InMemoryStatsRepository | None = None,
    clock: Clock | None = None,
) -> Flask:
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )

    settings_service = SettingsService(settings_repository or InMemorySettingsRepository())
    stats_service = StatsService(
        stats_repository or InMemoryStatsRepository(),
        settings_service,
        clock=clock,
    )

    app.config["SETTINGS_SERVICE"] = settings_service
    app.config["STATS_SERVICE"] = stats_service

    @app.get("/")
    def index() -> str:
        return render_template("index.html")

    @app.get("/api/state")
    def get_state():
        return jsonify(stats_service.get_state())

    @app.get("/api/stats/today")
    def get_today_stats():
        return jsonify(stats_service.get_today_stats())

    @app.post("/api/settings")
    def update_settings():
        payload = request.get_json(silent=True)

        try:
            updated_settings = settings_service.update_settings(payload)
        except SettingsValidationError:
            return jsonify({"error": "Invalid settings payload."}), 400

        return jsonify({"success": True, "settings": updated_settings})

    @app.post("/api/session/complete")
    def complete_session():
        payload = request.get_json(silent=True)
        if payload is None:
            payload = {}

        if not isinstance(payload, dict):
            return jsonify({"error": "session payload must be a JSON object."}), 400

        try:
            updated_stats = stats_service.complete_session(
                duration_seconds=payload.get("duration_seconds"),
                session_type=str(payload.get("session_type", "work")),
            )
        except ValueError:
            return jsonify({"error": "Invalid session payload."}), 400

        return jsonify({"success": True, "updated_stats": updated_stats})

    @app.post("/api/session/reset")
    def reset_session():
        reset_stats = stats_service.reset_today_stats()
        return jsonify({"success": True, "reset_at": reset_stats["date"]})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
