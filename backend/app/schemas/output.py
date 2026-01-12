from pydantic import BaseModel
from typing import List, Optional


class HourPoint(BaseModel):
    iso_time: str  # ISO datetime
    pv_kw: float
    price_eur_per_kwh: Optional[float] = None
    recommendation: Optional[str] = None


class DailyOutput(BaseModel):
    run_date: str              # YYYY-MM-DD (today)
    pv_history_day: str        # YYYY-MM-DD (yesterday date used as reference for month/day matching)
    note: str

    points: List[HourPoint]
