from __future__ import annotations

from copy import deepcopy
from typing import Mapping


class InMemoryStatsRepository:
    def __init__(self, initial_stats_by_date: Mapping[str, Mapping[str, object]] | None = None) -> None:
        self._stats_by_date = {
            date_key: deepcopy(dict(stats))
            for date_key, stats in (initial_stats_by_date or {}).items()
        }

    def get_stats_for_date(self, date_key: str) -> dict[str, object]:
        return deepcopy(self._stats_by_date.get(date_key, {}))

    def save_stats_for_date(
        self,
        date_key: str,
        stats: Mapping[str, object],
    ) -> dict[str, object]:
        self._stats_by_date[date_key] = deepcopy(dict(stats))
        return self.get_stats_for_date(date_key)

    def reset_stats_for_date(self, date_key: str) -> dict[str, object]:
        self._stats_by_date[date_key] = {}
        return self.get_stats_for_date(date_key)
