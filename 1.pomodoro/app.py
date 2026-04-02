from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, render_template, request

from domain.pomodoro_rules import SettingsValidationError, build_initial_timer_state
from repositories.settings_repository import InMemorySettingsRepository
from services.settings_service import SettingsService


BASE_DIR = Path(__file__).resolve().parent


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )

    settings_service = SettingsService(InMemorySettingsRepository())
    app.config["SETTINGS_SERVICE"] = settings_service

    @app.get("/")
    def index() -> str:
        return render_template("index.html")

    @app.get("/api/state")
    def get_state():
        settings = settings_service.get_settings()
        return jsonify(
            {
                "settings": settings.to_dict(),
                "timer": build_initial_timer_state(settings),
            }
        )

    @app.get("/api/settings")
    def get_settings():
        settings = settings_service.get_settings()
        return jsonify({"settings": settings.to_dict()})

    @app.post("/api/settings")
    def update_settings():
        payload = request.get_json(silent=True) or {}

        try:
            settings = settings_service.update_settings(payload)
        except SettingsValidationError as exc:
            return jsonify({"errors": exc.errors}), 400

        return jsonify(
            {
                "settings": settings.to_dict(),
                "timer": build_initial_timer_state(settings),
            }
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
