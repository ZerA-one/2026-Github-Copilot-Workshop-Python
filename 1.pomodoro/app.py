from pathlib import Path

from flask import Flask, jsonify, render_template, request

from repositories.settings_repository import InMemorySettingsRepository
from repositories.stats_repository import InMemoryStatsRepository
from services.settings_service import SettingsService
from services.stats_service import StatsService


BASE_DIR = Path(__file__).resolve().parent


def create_app(
    settings_repository: InMemorySettingsRepository | None = None,
    stats_repository: InMemoryStatsRepository | None = None,
) -> Flask:
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )

    settings_service = SettingsService(
        settings_repository or InMemorySettingsRepository(),
    )
    stats_service = StatsService(
        stats_repository or InMemoryStatsRepository(),
        settings_service,
    )

    def api_success(data: dict[str, object], status_code: int = 200):
        return jsonify({"ok": True, "data": data}), status_code

    def api_error(message: str, status_code: int = 400):
        return jsonify({"ok": False, "error": message}), status_code

    @app.get("/")
    def index() -> str:
        return render_template("index.html")

    @app.get("/api/state")
    def get_state():
        return api_success(stats_service.get_initial_state())

    @app.get("/api/stats/today")
    def get_today_stats():
        return api_success(stats_service.get_today_stats())

    @app.post("/api/settings")
    def update_settings():
        try:
            settings = settings_service.update_settings(request.get_json(silent=True))
        except ValueError as error:
            return api_error(str(error), 400)
        return api_success({"settings": settings})

    @app.post("/api/session/complete")
    def complete_session():
        payload = request.get_json(silent=True) or {}
        mode = payload.get("mode", "work")
        duration_seconds = payload.get("duration_seconds")

        try:
            result = stats_service.complete_session(mode, duration_seconds)
        except ValueError as error:
            return api_error(str(error), 400)

        return api_success(result)

    @app.post("/api/session/reset")
    def reset_session():
        today_stats = stats_service.reset_today()
        state = stats_service.get_initial_state()
        return api_success({"today_stats": today_stats, "state": state})

    return app


app = create_app()


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000)
