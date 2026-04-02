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


def test_state_api_returns_default_settings_and_today_stats(client) -> None:
	response = client.get("/api/state")
	body = response.get_json()

	assert response.status_code == 200
	assert body == {
		"mode": "work",
		"remaining_seconds": 1500,
		"settings": {
			"work_minutes": 25,
			"short_break_minutes": 5,
			"long_break_minutes": 15,
			"cycles_before_long_break": 4,
		},
		"stats": {
			"date": "2026-04-02",
			"completed_count": 0,
			"focused_seconds": 0,
		},
	}


def test_settings_api_updates_values_and_changes_state_duration(client) -> None:
	response = client.post(
		"/api/settings",
		json={
			"work_minutes": 30,
			"short_break_minutes": 10,
		},
	)
	body = response.get_json()
	state_response = client.get("/api/state")

	assert response.status_code == 200
	assert body["success"] is True
	assert body["settings"]["work_minutes"] == 30
	assert body["settings"]["short_break_minutes"] == 10
	assert state_response.get_json()["remaining_seconds"] == 1800


def test_settings_api_rejects_invalid_payload(client) -> None:
	response = client.post(
		"/api/settings",
		json={
			"work_minutes": 0,
		},
	)

	assert response.status_code == 400
	assert response.get_json()["error"] == "work_minutes must be a positive integer."


def test_session_complete_api_updates_today_stats(client) -> None:
	response = client.post("/api/session/complete", json={"duration_seconds": 1500})
	body = response.get_json()
	stats_response = client.get("/api/stats/today")

	assert response.status_code == 200
	assert body == {
		"success": True,
		"updated_stats": {
			"date": "2026-04-02",
			"completed_count": 1,
			"focused_seconds": 1500,
		},
	}
	assert stats_response.get_json() == {
		"date": "2026-04-02",
		"completed_count": 1,
		"focused_seconds": 1500,
	}


def test_session_complete_api_rejects_invalid_duration(client) -> None:
	response = client.post("/api/session/complete", json={"duration_seconds": -1})

	assert response.status_code == 400
	assert response.get_json()["error"] == "duration_seconds must be a positive integer."


def test_session_reset_api_resets_today_stats(client) -> None:
	client.post("/api/session/complete", json={"duration_seconds": 1500})

	reset_response = client.post("/api/session/reset")
	stats_response = client.get("/api/stats/today")

	assert reset_response.status_code == 200
	assert reset_response.get_json() == {
		"success": True,
		"reset_at": "2026-04-02",
	}
	assert stats_response.get_json() == {
		"date": "2026-04-02",
		"completed_count": 0,
		"focused_seconds": 0,
	}


def test_today_stats_api_returns_default_empty_stats(client) -> None:
	response = client.get("/api/stats/today")

	assert response.status_code == 200
	assert response.get_json() == {
		"date": "2026-04-02",
		"completed_count": 0,
		"focused_seconds": 0,
	}
