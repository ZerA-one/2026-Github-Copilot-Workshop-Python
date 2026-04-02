from datetime import datetime
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


class FrozenClock:
    def __init__(self, current: datetime) -> None:
        self._current = current

    def now(self) -> datetime:
        return self._current


def test_api_state_persists_settings_stats_and_session_history(tmp_path) -> None:
    first_app = create_app(
        storage_dir=tmp_path,
        clock=FrozenClock(datetime(2026, 4, 2, 9, 0, 0)),
    )
    first_client = first_app.test_client()

    settings_response = first_client.post(
        "/api/settings",
        json={
            "work_minutes": 30,
            "short_break_minutes": 6,
            "long_break_minutes": 18,
            "cycles_before_long_break": 5,
        },
    )
    session_response = first_client.post(
        "/api/session/complete",
        json={
            "session_type": "work",
            "focused_seconds": 1800,
        },
    )

    assert settings_response.status_code == 200
    assert session_response.status_code == 200

    second_app = create_app(
        storage_dir=tmp_path,
        clock=FrozenClock(datetime(2026, 4, 2, 10, 0, 0)),
    )
    second_client = second_app.test_client()

    response = second_client.get("/api/state")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["settings"] == {
        "work_minutes": 30,
        "short_break_minutes": 6,
        "long_break_minutes": 18,
        "cycles_before_long_break": 5,
    }
    assert payload["today_stats"] == {
        "date": "2026-04-02",
        "completed_count": 1,
        "focused_seconds": 1800,
    }
    assert payload["session_log"][0]["session_type"] == "work"
    assert payload["remaining_seconds"] == 30 * 60


def test_api_reset_today_stats_keeps_history(tmp_path) -> None:
    app = create_app(
        storage_dir=tmp_path,
        clock=FrozenClock(datetime(2026, 4, 2, 9, 0, 0)),
    )
    client = app.test_client()

    client.post(
        "/api/session/complete",
        json={
            "session_type": "work",
            "focused_seconds": 1500,
        },
    )

    reset_response = client.post("/api/session/reset")
    state_response = client.get("/api/state")

    assert reset_response.status_code == 200
    assert reset_response.get_json()["daily_stats"] == {
        "date": "2026-04-02",
        "completed_count": 0,
        "focused_seconds": 0,
    }
    assert len(state_response.get_json()["session_log"]) == 1
