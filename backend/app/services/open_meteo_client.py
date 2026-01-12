from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import requests
import pandas as pd


@dataclass(frozen=True)
class WeatherHourly:
    """Hourly weather signal used for PV forecast."""
    df: pd.DataFrame
    # columns: ["time", "shortwave_radiation"] etc.


class OpenMeteoClient:
    BASE = "https://api.open-meteo.com/v1/forecast"

    def fetch_hourly(self, lat: float, lon: float, tz: str) -> WeatherHourly:
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "shortwave_radiation,cloud_cover",
            "timezone": tz,
            "past_days": 1,  # includes yesterday
            "forecast_days": 1,  # includes today
        }
        r = requests.get(self.BASE, params=params, timeout=25)
        r.raise_for_status()
        data = r.json()

        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        swr = hourly.get("shortwave_radiation", [])
        cloud = hourly.get("cloud_cover", [])

        df = pd.DataFrame(
            {
                "time": pd.to_datetime(times),
                "shortwave_radiation": swr,
                "cloud_cover": cloud,
            }
        )
        return WeatherHourly(df=df)
