from pathlib import Path

from flask import Flask

from app import BASE_DIR, create_app


def test_create_app_returns_flask_instance() -> None:
	app = create_app()

	assert isinstance(app, Flask)


def test_create_app_uses_project_template_and_static_directories() -> None:
	app = create_app()

	assert Path(app.template_folder) == BASE_DIR / "templates"
	assert Path(app.static_folder) == BASE_DIR / "static"


def test_index_route_returns_successful_html_response() -> None:
	app = create_app()
	client = app.test_client()

	response = client.get("/")
	body = response.get_data(as_text=True)

	assert response.status_code == 200
	assert "ポモドーロタイマー" in body
	assert "今日の進捗" in body
	assert 'id="start-button"' in body
	assert "static/css/style.css" in body
	assert "static/js/timer-engine.js" in body
	assert "static/js/pomodoro-api.js" in body


def test_api_state_returns_default_timer_and_today_stats() -> None:
	app = create_app()
	client = app.test_client()

	response = client.get("/api/state")
	body = response.get_json()

	assert response.status_code == 200
	assert body["mode"] == "work"
	assert body["status"] == "idle"
	assert body["remaining_seconds"] == 25 * 60
	assert body["total_seconds"] == 25 * 60
	assert body["stats"]["completed_count"] == 0
	assert body["stats"]["focused_seconds"] == 0


def test_api_session_complete_returns_updated_stats() -> None:
	app = create_app()
	client = app.test_client()

	response = client.post(
		"/api/session/complete",
		json={"focused_seconds": 1500, "session_type": "work"},
	)
	body = response.get_json()
	stats_response = client.get("/api/stats/today")
	stats_body = stats_response.get_json()

	assert response.status_code == 200
	assert body["stats"]["completed_count"] == 1
	assert body["stats"]["focused_seconds"] == 1500
	assert stats_response.status_code == 200
	assert stats_body["completed_count"] == 1
	assert stats_body["focused_seconds"] == 1500


def test_api_session_reset_clears_today_stats() -> None:
	app = create_app()
	client = app.test_client()

	client.post("/api/session/complete", json={"focused_seconds": 1500})
	response = client.post("/api/session/reset")
	body = response.get_json()

	assert response.status_code == 200
	assert body["stats"]["completed_count"] == 0
	assert body["stats"]["focused_seconds"] == 0
