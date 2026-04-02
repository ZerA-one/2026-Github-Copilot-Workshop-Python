from pathlib import Path

from flask import Flask

from app import BASE_DIR, create_app


VALID_SETTINGS = {
    "work_minutes": 30,
    "short_break_minutes": 7,
    "long_break_minutes": 20,
    "cycles_before_long_break": 3,
}


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
    assert "Step 10" in body
    assert 'id="settings-form"' in body
    assert "static/js/timer-engine.js" in body


def test_get_state_returns_default_settings_and_timer() -> None:
    app = create_app()
    client = app.test_client()

    response = client.get("/api/state")

    assert response.status_code == 200
    assert response.json == {
        "settings": {
            "work_minutes": 25,
            "short_break_minutes": 5,
            "long_break_minutes": 15,
            "cycles_before_long_break": 4,
        },
        "timer": {
            "mode": "work",
            "remaining_seconds": 1500,
            "completed_work_sessions": 0,
        },
    }


def test_post_settings_persists_updated_values_for_following_requests() -> None:
    app = create_app()
    client = app.test_client()

    response = client.post("/api/settings", json=VALID_SETTINGS)

    assert response.status_code == 200
    assert response.json == {
        "settings": VALID_SETTINGS,
        "timer": {
            "mode": "work",
            "remaining_seconds": 1800,
            "completed_work_sessions": 0,
        },
    }

    state_response = client.get("/api/state")
    settings_response = client.get("/api/settings")

    assert state_response.json["settings"] == VALID_SETTINGS
    assert state_response.json["timer"]["remaining_seconds"] == 1800
    assert settings_response.json == {"settings": VALID_SETTINGS}


def test_post_settings_returns_validation_errors_for_invalid_values() -> None:
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/api/settings",
        json={
            "work_minutes": 0,
            "short_break_minutes": "abc",
            "long_break_minutes": 121,
        },
    )

    assert response.status_code == 400
    assert response.json == {
        "errors": {
            "work_minutes": "1〜120 の範囲で入力してください。",
            "short_break_minutes": "整数で入力してください。",
            "long_break_minutes": "1〜120 の範囲で入力してください。",
            "cycles_before_long_break": "必須項目です。",
        }
    }
