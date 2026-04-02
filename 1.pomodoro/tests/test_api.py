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


def test_step1_project_structure_exists() -> None:
	assert (BASE_DIR / "templates").is_dir()
	assert (BASE_DIR / "static" / "css").is_dir()
	assert (BASE_DIR / "static" / "js").is_dir()
	assert (BASE_DIR / "domain").is_dir()
	assert (BASE_DIR / "services").is_dir()
	assert (BASE_DIR / "repositories").is_dir()
	assert (BASE_DIR / "tests").is_dir()
	assert (BASE_DIR / "templates" / "index.html").is_file()
	assert (BASE_DIR / "static" / "css" / "style.css").is_file()
	assert (BASE_DIR / "static" / "js" / "timer-engine.js").is_file()
	assert (BASE_DIR / "static" / "js" / "pomodoro-state.js").is_file()
	assert (BASE_DIR / "static" / "js" / "pomodoro-ui.js").is_file()
	assert (BASE_DIR / "static" / "js" / "pomodoro-api.js").is_file()
	assert (BASE_DIR / "domain" / "pomodoro_rules.py").is_file()
	assert (BASE_DIR / "services" / "settings_service.py").is_file()
	assert (BASE_DIR / "services" / "stats_service.py").is_file()
	assert (BASE_DIR / "repositories" / "settings_repository.py").is_file()
	assert (BASE_DIR / "repositories" / "stats_repository.py").is_file()
