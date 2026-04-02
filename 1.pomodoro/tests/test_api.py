from pathlib import Path

from flask import Flask

from app import BASE_DIR, create_app
from domain.clock import Clock
from repositories.settings_repository import InMemorySettingsRepository
from repositories.stats_repository import InMemoryStatsRepository
from services.settings_service import SettingsService
from services.stats_service import StatsService


class FixedClock(Clock):
    def __init__(self, now_value) -> None:
        self._now_value = now_value

    def now(self):
        return self._now_value


def create_test_client():
    from datetime import datetime

    settings_service = SettingsService(InMemorySettingsRepository())
    stats_service = StatsService(
        InMemoryStatsRepository(),
        settings_service,
        FixedClock(datetime(2026, 4, 2, 9, 0, 0)),
    )
    app = create_app(settings_service=settings_service, stats_service=stats_service)
    return app.test_client()


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


def test_api_state_returns_service_backed_data() -> None:
    client = create_test_client()

    response = client.get("/api/state")

    assert response.status_code == 200
    assert response.get_json() == {
        "current_mode": "work",
        "seconds_remaining": 1500,
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


def test_api_settings_persists_updates_for_following_state_requests() -> None:
    client = create_test_client()

    save_response = client.post("/api/settings", json={"work_minutes": 30})
    state_response = client.get("/api/state")

    assert save_response.status_code == 200
    assert save_response.get_json()["work_minutes"] == 30
    assert state_response.get_json()["settings"]["work_minutes"] == 30
    assert state_response.get_json()["seconds_remaining"] == 1800


def test_api_session_complete_and_reset_use_service_layer() -> None:
    client = create_test_client()

    complete_response = client.post(
        "/api/session/complete",
        json={"session_type": "work", "duration_seconds": 1500},
    )
    stats_response = client.get("/api/stats/today")
    reset_response = client.post("/api/session/reset")

    assert complete_response.status_code == 200
    assert complete_response.get_json()["current_mode"] == "short_break"
    assert complete_response.get_json()["stats"]["completed_count"] == 1
    assert complete_response.get_json()["stats"]["focused_seconds"] == 1500
    assert stats_response.get_json()["completed_count"] == 1
    assert stats_response.get_json()["focused_seconds"] == 1500
    assert reset_response.get_json() == {
        "date": "2026-04-02",
        "completed_count": 0,
        "focused_seconds": 0,
    }
