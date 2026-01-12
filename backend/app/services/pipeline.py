from __future__ import annotations

from datetime import date
import pandas as pd

from ..core.timeutils import DayKey, previous_day
from ..schemas.output import DailyOutput, HourPoint
from .pv_csv_loader import load_pv_history_for_day
from .open_meteo_client import OpenMeteoClient
from .entsoe_client import EntsoeClient
from .forecast_model import fit_scale_from_yesterday, forecast_today
from ..repositories.output_repo import OutputRepository


class DailyPipeline:
    def __init__(
        self,
        *,
        tz: str,
        lat: float,
        lon: float,
        pv_csv_path: str,
        pv_value_column: str,
        pv_capacity_kw: float,
        output_repo: OutputRepository,
        open_meteo: OpenMeteoClient,
        entsoe: EntsoeClient,
    ):
        self.tz = tz
        self.lat = lat
        self.lon = lon
        self.pv_csv_path = pv_csv_path
        self.pv_value_column = pv_value_column
        self.pv_capacity_kw = pv_capacity_kw
        self.output_repo = output_repo
        self.open_meteo = open_meteo
        self.entsoe = entsoe

    def run(self, run_date: date) -> DailyOutput:
        yday = previous_day(run_date)
        day_key = DayKey.from_date(yday)  # ignore year by design

        pv_hist = load_pv_history_for_day(
            csv_path=self.pv_csv_path,
            value_col=self.pv_value_column,
            day_key=day_key,
        )

        weather = self.open_meteo.fetch_hourly(self.lat, self.lon, self.tz).df
        weather = weather.set_index("time")

        # Split weather into yesterday and today (based on run_date/yday in local tz)
        swr = weather["shortwave_radiation"].astype(float)

        swr_yday = swr[(swr.index.date == yday)]
        swr_today = swr[(swr.index.date == run_date)]

        # Align indexes for fitting: use intersection of timestamps
        pv_yday = pv_hist.hourly_kw
        common_idx = pv_yday.index.intersection(swr_yday.index)
        pv_yday_aligned = pv_yday.reindex(common_idx).fillna(0.0)
        swr_yday_aligned = swr_yday.reindex(common_idx).fillna(0.0)

        a = fit_scale_from_yesterday(pv_yday_aligned, swr_yday_aligned)
        fc = forecast_today(self.pv_capacity_kw, a, swr_today)

        prices = self.entsoe.fetch_day_ahead_prices(run_date)
        price_map = prices.prices if prices else {}

        points: list[HourPoint] = []
        for t, pv_kw in fc.hourly_pv_kw.items():
            iso = pd.Timestamp(t).isoformat()
            price = price_map.get(iso)
            rec = None
            if price is not None:
                rec = "Einspeisen" if (pv_kw > 0.5 and price >= 0.20) else "Eigenverbrauch"

            points.append(
                HourPoint(
                    iso_time=iso,
                    pv_kw=float(pv_kw),
                    price_eur_per_kwh=price,
                    recommendation=rec,
                )
            )

        output = DailyOutput(
            run_date=run_date.isoformat(),
            pv_history_day=yday.isoformat(),
            note="Year in PV CSV is ignored. Matching is done by month/day only. Model is a simple scale fit from yesterday.",
            points=points,
        )

        self.output_repo.save(run_date, output)
        return output
