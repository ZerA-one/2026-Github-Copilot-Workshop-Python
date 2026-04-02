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
    assert "読み込み中" in body
    assert "static/css/style.css" in body
    assert "static/js/timer-engine.js" in body


def test_api_state_returns_initial_timer_state() -> None:
    app = create_app()
    client = app.test_client()

    response = client.get("/api/state")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["data"]["mode"] == "work"
    assert payload["data"]["timer_status"] == "idle"
    assert payload["data"]["duration_seconds"] == 1500


def test_api_session_complete_updates_stats_and_next_mode() -> None:
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/api/session/complete",
        json={"mode": "work", "duration_seconds": 1500},
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["data"]["today_stats"] == {
        "completed_count": 1,
        "focused_seconds": 1500,
    }
    assert payload["data"]["next_state"]["mode"] == "short_break"


def test_api_reset_clears_today_stats() -> None:
    app = create_app()
    client = app.test_client()
    client.post("/api/session/complete", json={"mode": "work", "duration_seconds": 1500})

    response = client.post("/api/session/reset")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["data"]["today_stats"] == {
        "completed_count": 0,
        "focused_seconds": 0,
    }
    assert payload["data"]["state"]["mode"] == "work"


def test_api_settings_validation_returns_bad_request() -> None:
    app = create_app()
    client = app.test_client()

    response = client.post("/api/settings", json={"work_minutes": 0})
    payload = response.get_json()

    assert response.status_code == 400
    assert payload["ok"] is False
    assert payload["error"] == "入力内容を確認してください。"
