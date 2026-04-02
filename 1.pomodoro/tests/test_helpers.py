from datetime import datetime

from domain.clock import Clock


class FixedClock(Clock):
    def __init__(self, now_value: datetime) -> None:
        self._now_value = now_value

    def now(self) -> datetime:
        return self._now_value
