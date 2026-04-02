from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request

from domain.clock import SystemClock
from repositories.settings_repository import InMemorySettingsRepository
from repositories.stats_repository import InMemoryStatsRepository
from services.settings_service import SettingsService
from services.stats_service import StatsService


BASE_DIR = Path(__file__).resolve().parent


def create_app(
    settings_service: SettingsService | None = None,
    stats_service: StatsService | None = None,
) -> Flask:
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )

    resolved_settings_service = settings_service or SettingsService(InMemorySettingsRepository())
    resolved_stats_service = stats_service or StatsService(
        InMemoryStatsRepository(),
        resolved_settings_service,
        SystemClock(),
    )

    app.config["settings_service"] = resolved_settings_service
    app.config["stats_service"] = resolved_stats_service

    @app.get("/")
    def index() -> str:
        return render_template("index.html")

    @app.get("/api/state")
    def api_state() -> Any:
        return jsonify(resolved_stats_service.get_state())

    @app.get("/api/stats/today")
    def api_stats_today() -> Any:
        return jsonify(resolved_stats_service.get_today_stats())

    @app.post("/api/settings")
    def api_settings() -> Any:
        payload = request.get_json(silent=True) or {}
        return jsonify(resolved_settings_service.save_settings(_coerce_settings_payload(payload)))

    @app.post("/api/session/complete")
    def api_session_complete() -> Any:
        payload = request.get_json(silent=True) or {}
        return jsonify(
            resolved_stats_service.complete_session(
                str(payload.get("session_type", "work")),
                _coerce_int(payload.get("duration_seconds"), default=0),
            )
        )

    @app.post("/api/session/reset")
    def api_session_reset() -> Any:
        return jsonify(resolved_stats_service.reset_today_stats())

    return app


def _coerce_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _coerce_settings_payload(payload: dict[str, Any]) -> dict[str, int]:
    return {
        key: _coerce_int(value, default=0)
        for key, value in payload.items()
        if key in InMemorySettingsRepository().get_settings()
    }


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
