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
	assert "Step 1" in body
	assert "static/css/style.css" in body
	assert "static/js/timer-engine.js" in body


def test_get_state_returns_default_in_memory_payload() -> None:
	app = create_app()
	client = app.test_client()

	response = client.get("/api/state")
	body = response.get_json()

	assert response.status_code == 200
	assert body == {
		"settings": {
			"work_minutes": 25,
			"short_break_minutes": 5,
			"long_break_minutes": 15,
			"cycles_before_long_break": 4,
		},
		"timer": {
			"status": "idle",
			"mode": "work",
			"remaining_seconds": 1500,
		},
		"today_stats": {
			"completed_count": 0,
			"focused_seconds": 0,
		},
	}


def test_get_today_stats_returns_default_stats() -> None:
	app = create_app()
	client = app.test_client()

	response = client.get("/api/stats/today")

	assert response.status_code == 200
	assert response.get_json() == {
		"completed_count": 0,
		"focused_seconds": 0,
	}


def test_post_settings_updates_in_memory_settings() -> None:
	app = create_app()
	client = app.test_client()

	response = client.post(
		"/api/settings",
		json={
			"work_minutes": 30,
			"short_break_minutes": 7,
		},
	)
	body = response.get_json()
	state_response = client.get("/api/state")

	assert response.status_code == 200
	assert body == {
		"message": "Settings updated.",
		"settings": {
			"work_minutes": 30,
			"short_break_minutes": 7,
			"long_break_minutes": 15,
			"cycles_before_long_break": 4,
		},
	}
	assert state_response.get_json()["timer"]["remaining_seconds"] == 1800


def test_post_session_complete_updates_today_stats() -> None:
	app = create_app()
	client = app.test_client()

	response = client.post(
		"/api/session/complete",
		json={"session_type": "work", "focused_seconds": 900},
	)

	assert response.status_code == 200
	assert response.get_json() == {
		"message": "Session recorded.",
		"today_stats": {
			"completed_count": 1,
			"focused_seconds": 900,
		},
	}


def test_post_session_reset_clears_today_stats_and_timer() -> None:
	app = create_app()
	client = app.test_client()

	client.post(
		"/api/settings",
		json={"work_minutes": 30},
	)
	client.post(
		"/api/session/complete",
		json={"session_type": "work", "focused_seconds": 900},
	)
	response = client.post("/api/session/reset")

	assert response.status_code == 200
	assert response.get_json() == {
		"message": "Today stats reset.",
		"timer": {
			"status": "idle",
			"mode": "work",
			"remaining_seconds": 1500,
		},
		"today_stats": {
			"completed_count": 0,
			"focused_seconds": 0,
		},
	}
