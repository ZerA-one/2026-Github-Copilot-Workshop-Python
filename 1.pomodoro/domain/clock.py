"""Clock 抽象。"""

from abc import ABC, abstractmethod
from datetime import date, datetime


class Clock(ABC):
    """時刻取得を抽象化するインターフェース。"""

    @abstractmethod
    def now(self) -> datetime:
        """現在日時を返す。"""

    def today(self) -> date:
        """現在日付を返す。"""
        return self.now().date()


class SystemClock(Clock):
    """実運用用のシステム時計。"""

    def now(self) -> datetime:
        return datetime.now()
