from pathlib import Path
import sys
from datetime import date, datetime

import pytest

from app import create_app
from repositories.settings_repository import InMemorySettingsRepository
from repositories.stats_repository import InMemoryStatsRepository


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class FixedClock:
    def __init__(self, current_datetime: datetime) -> None:
        self._current_datetime = current_datetime

    def now(self) -> datetime:
        return self._current_datetime

    def today(self) -> date:
        return self._current_datetime.date()


@pytest.fixture
def fixed_clock() -> FixedClock:
    return FixedClock(datetime(2026, 4, 2, 10, 54, 30))


@pytest.fixture
def settings_repository() -> InMemorySettingsRepository:
    return InMemorySettingsRepository()


@pytest.fixture
def stats_repository() -> InMemoryStatsRepository:
    return InMemoryStatsRepository()


@pytest.fixture
def app(fixed_clock: FixedClock, settings_repository: InMemorySettingsRepository, stats_repository: InMemoryStatsRepository):
    application = create_app(
        settings_repository=settings_repository,
        stats_repository=stats_repository,
        clock=fixed_clock,
    )
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    return app.test_client()
