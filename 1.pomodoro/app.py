from pathlib import Path

from flask import Flask, jsonify, render_template, request

from repositories.settings_repository import InMemorySettingsRepository
from repositories.stats_repository import InMemoryStatsRepository
from services.settings_service import SettingsService
from services.stats_service import StatsService


BASE_DIR = Path(__file__).resolve().parent


def create_app() -> Flask:
	app = Flask(
		__name__,
		template_folder=str(BASE_DIR / "templates"),
		static_folder=str(BASE_DIR / "static"),
	)
	settings_service = SettingsService(InMemorySettingsRepository())
	stats_service = StatsService(InMemoryStatsRepository(), settings_service)

	@app.get("/")
	def index() -> str:
		return render_template("index.html")

	@app.get("/api/state")
	def get_state():
		return jsonify(stats_service.get_state())

	@app.get("/api/stats/today")
	def get_today_stats():
		return jsonify(stats_service.get_today_stats())

	@app.post("/api/session/complete")
	def complete_session():
		payload = request.get_json(silent=True) or {}
		focused_seconds = payload.get("focused_seconds")
		if focused_seconds is None:
			focused_seconds = settings_service.get_settings()["work_minutes"] * 60

		return jsonify(
			stats_service.complete_session(
				focused_seconds=max(int(focused_seconds), 0),
				session_type=str(payload.get("session_type", "work")),
			)
		)

	@app.post("/api/session/reset")
	def reset_session():
		return jsonify(stats_service.reset_today())

	return app


app = create_app()


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000)
