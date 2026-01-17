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
        # run_date is used ONLY to choose which PV day (month/day) from CSV we want.
        pv_ref_day = previous_day(run_date)
        day_key = DayKey.from_date(pv_ref_day)  # ignore year by design

        pv_hist = load_pv_history_for_day(
            csv_path=self.pv_csv_path,
            value_col=self.pv_value_column,
            day_key=day_key,
        )

        weather = self.open_meteo.fetch_hourly(self.lat, self.lon, self.tz).df
        weather = weather.set_index("time")

        # Split weather into yesterday and today (based on run_date/yday in local tz)
        swr = weather["shortwave_radiation"].astype(float)

        # Weather data is always "yesterday + today" relative to NOW (Open-Meteo past_days/forecast_days).
        available_dates = sorted(set(swr.index.date))
        if len(available_dates) < 2:
            raise ValueError("Open-Meteo did not return enough hourly weather data (need yesterday+today).")

        weather_yday = available_dates[-2]
        weather_today = available_dates[-1]

        swr_yday = swr[swr.index.date == weather_yday]
        swr_today = swr[swr.index.date == weather_today]

        # --- Align by hour-of-day (year agnostic) ---
        pv_yday = pv_hist.hourly_kw
        swr_yday = swr_yday
        swr_today = swr_today

        # Create hour-of-day series (0..23)
        pv_by_hour = pv_yday.groupby(pv_yday.index.hour).mean()
        swr_yday_by_hour = swr_yday.groupby(swr_yday.index.hour).mean()
        swr_today_by_hour = swr_today.groupby(swr_today.index.hour).mean()

        # Ensure we have data for fitting
        common_hours = pv_by_hour.index.intersection(swr_yday_by_hour.index)
        if len(common_hours) == 0:
            raise ValueError(
                "No overlapping hours between PV history and yesterday weather. "
                "This usually means the date selection or timezone is off."
            )

        pv_fit = pv_by_hour.reindex(common_hours).fillna(0.0)
        swr_fit = swr_yday_by_hour.reindex(common_hours).fillna(0.0)

        a = fit_scale_from_yesterday(pv_fit, swr_fit)

        # Forecast today using today's hourly timestamps (keep real datetime index!)
        # We map hour->value onto the actual timestamps from swr_today
        pv_forecast_by_hour = (a * swr_today_by_hour).clip(lower=0.0, upper=float(self.pv_capacity_kw)).fillna(0.0)

        pv_forecast_series = swr_today.copy()
        pv_forecast_series[:] = [float(pv_forecast_by_hour.get(t.hour, 0.0)) for t in pv_forecast_series.index]

        # Wrap into ForecastResult-like structure
        class _Tmp:
            def __init__(self, s): self.hourly_pv_kw = s

        fc = _Tmp(pv_forecast_series)


        # fc = forecast_today(self.pv_capacity_kw, a, swr_today)

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
            run_date=weather_today.isoformat(),  # actual weather 'today'
            pv_history_day=pv_ref_day.isoformat(),  # the PV day you selected
            note="Year in PV CSV is ignored. Matching is done by month/day only. Model is a simple scale fit from yesterday.",
            points=points,
        )

        self.output_repo.save(weather_today, output)
        return output
