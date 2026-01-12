from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class DayKey:
    """A calendar-year-agnostic key: month/day only."""
    month: int
    day: int

    @staticmethod
    def from_date(d: date) -> "DayKey":
        return DayKey(month=d.month, day=d.day)


def now_in_tz(tz_name: str) -> datetime:
    return datetime.now(ZoneInfo(tz_name))


def today_in_tz(tz_name: str) -> date:
    return now_in_tz(tz_name).date()


def previous_day(d: date) -> date:
    return d - timedelta(days=1)
