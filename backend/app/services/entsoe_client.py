from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional
import os
import requests


@dataclass(frozen=True)
class PricesHourly:
    """Hourly day-ahead prices in EUR/kWh, if available."""
    # key: "YYYY-MM-DDTHH:00"
    prices: dict[str, float]


class EntsoeClient:
    BASE = "https://web-api.tp.entsoe.eu/api"

    def __init__(self, api_key: Optional[str], bidding_zone: str):
        self.api_key = (api_key or "").strip()
        self.bidding_zone = bidding_zone

    def fetch_day_ahead_prices(self, d: date, tz_hint: str = "Europe/Vienna") -> Optional[PricesHourly]:
        """
        Minimal placeholder integration:
        - If no API key: return None (frontend handles it).
        - If key provided, you can later implement full XML parsing.
        """
        if not self.api_key:
            return None

        # NOTE: Real implementation needs:
        # documentType=A44, in_Domain/out_Domain, periodStart/periodEnd (UTC),
        # and XML parsing of TimeSeries->Period->Point.
        # For prototype stability we return None even with key unless you extend it.
        return None
