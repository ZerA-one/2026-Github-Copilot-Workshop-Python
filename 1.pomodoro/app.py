from copy import deepcopy
from pathlib import Path

from flask import Flask, jsonify, render_template, request


BASE_DIR = Path(__file__).resolve().parent

DEFAULT_SETTINGS = {
	"work_minutes": 25,
	"short_break_minutes": 5,
	"long_break_minutes": 15,
	"cycles_before_long_break": 4,
}

DEFAULT_TIMER_STATE = {
	"status": "idle",
	"mode": "work",
	"remaining_seconds": DEFAULT_SETTINGS["work_minutes"] * 60,
}

DEFAULT_TODAY_STATS = {
	"completed_count": 0,
	"focused_seconds": 0,
}


def create_app() -> Flask:
	app = Flask(
		__name__,
		template_folder=str(BASE_DIR / "templates"),
		static_folder=str(BASE_DIR / "static"),
	)
	state = {
		"settings": deepcopy(DEFAULT_SETTINGS),
		"timer": deepcopy(DEFAULT_TIMER_STATE),
		"today_stats": deepcopy(DEFAULT_TODAY_STATS),
	}

	@app.get("/")
	def index() -> str:
		return render_template("index.html")

	@app.get("/api/state")
	def get_state():
		return jsonify(state)

	@app.get("/api/stats/today")
	def get_today_stats():
		return jsonify(state["today_stats"])

	@app.post("/api/settings")
	def update_settings():
		payload = request.get_json(silent=True)

		if isinstance(payload, dict):
			for key in DEFAULT_SETTINGS:
				value = payload.get(key)
				if isinstance(value, int) and value > 0:
					state["settings"][key] = value

			state["timer"]["remaining_seconds"] = (
				state["settings"]["work_minutes"] * 60
			)

		return jsonify(
			{
				"message": "Settings updated.",
				"settings": state["settings"],
			}
		)

	@app.post("/api/session/complete")
	def complete_session():
		payload = request.get_json(silent=True)
		session_type = "work"
		focused_seconds = state["settings"]["work_minutes"] * 60

		if isinstance(payload, dict):
			if payload.get("session_type") in {"work", "short_break", "long_break"}:
				session_type = payload["session_type"]

			value = payload.get("focused_seconds")
			if isinstance(value, int) and value >= 0:
				focused_seconds = value

		if session_type == "work":
			state["today_stats"]["completed_count"] += 1
			state["today_stats"]["focused_seconds"] += focused_seconds

		return jsonify(
			{
				"message": "Session recorded.",
				"today_stats": state["today_stats"],
			}
		)

	@app.post("/api/session/reset")
	def reset_session():
		state["today_stats"] = deepcopy(DEFAULT_TODAY_STATS)
		state["timer"] = deepcopy(DEFAULT_TIMER_STATE)

		return jsonify(
			{
				"message": "Today stats reset.",
				"timer": state["timer"],
				"today_stats": state["today_stats"],
			}
		)

	return app


app = create_app()


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000)
