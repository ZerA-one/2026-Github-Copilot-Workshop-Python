from typing import Any, TypedDict
from copy import deepcopy
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request
from werkzeug.exceptions import BadRequest


BASE_DIR = Path(__file__).resolve().parent

class Settings(TypedDict):
	work_minutes: int
	short_break_minutes: int
	long_break_minutes: int
	cycles_before_long_break: int


class TimerState(TypedDict):
	status: str
	mode: str
	remaining_seconds: int


class TodayStats(TypedDict):
	completed_count: int
	focused_seconds: int


class ApiState(TypedDict):
	settings: Settings
	timer: TimerState
	today_stats: TodayStats


DEFAULT_SETTINGS: Settings = {
	"work_minutes": 25,
	"short_break_minutes": 5,
	"long_break_minutes": 15,
	"cycles_before_long_break": 4,
}

DEFAULT_TIMER_STATE: TimerState = {
	"status": "idle",
	"mode": "work",
	"remaining_seconds": DEFAULT_SETTINGS["work_minutes"] * 60,
}

DEFAULT_TODAY_STATS: TodayStats = {
	"completed_count": 0,
	"focused_seconds": 0,
}


def build_timer_state(settings: Settings) -> TimerState:
	return {
		"status": "idle",
		"mode": "work",
		"remaining_seconds": settings["work_minutes"] * 60,
	}


def parse_and_validate_json() -> tuple[dict[str, Any] | None, tuple[Response, int] | None]:
	"""Allow empty bodies for scaffold endpoints while rejecting malformed JSON."""

	if not request.data:
		return {}, None

	try:
		payload = request.get_json()
	except BadRequest:
		return None, (jsonify({"message": "Request body must be valid JSON."}), 400)

	if payload is None:
		return {}, None

	if not isinstance(payload, dict):
		return None, (jsonify({"message": "Request body must be a JSON object."}), 400)

	return payload, None


def create_app() -> Flask:
	app = Flask(
		__name__,
		template_folder=str(BASE_DIR / "templates"),
		static_folder=str(BASE_DIR / "static"),
	)
	state: ApiState = {
		"settings": deepcopy(DEFAULT_SETTINGS),
		"timer": build_timer_state(DEFAULT_SETTINGS),
		"today_stats": deepcopy(DEFAULT_TODAY_STATS),
	}

	@app.get("/")
	def index() -> str:
		return render_template("index.html")

	@app.get("/api/state")
	def get_state() -> Response:
		return jsonify(state)

	@app.get("/api/stats/today")
	def get_today_stats() -> Response:
		return jsonify(state["today_stats"])

	@app.post("/api/settings")
	def update_settings() -> Response | tuple[Response, int]:
		payload, error_response = parse_and_validate_json()

		if error_response is not None:
			return error_response

		for key in DEFAULT_SETTINGS:
			value = payload.get(key)
			if isinstance(value, int) and value > 0:
				state["settings"][key] = value

		state["timer"] = build_timer_state(state["settings"])

		return jsonify(
			{
				"message": "Settings updated.",
				"settings": state["settings"],
			}
		)

	@app.post("/api/session/complete")
	def complete_session() -> Response | tuple[Response, int]:
		payload, error_response = parse_and_validate_json()

		if error_response is not None:
			return error_response

		session_type = "work"
		focused_seconds = state["settings"]["work_minutes"] * 60

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
	def reset_session() -> Response:
		state["today_stats"] = deepcopy(DEFAULT_TODAY_STATS)
		state["timer"] = build_timer_state(state["settings"])

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
