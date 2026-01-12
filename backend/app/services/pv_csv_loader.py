from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import pandas as pd

from ..core.timeutils import DayKey


@dataclass(frozen=True)
class PVHistory:
    """PV production history for a specific month/day (year ignored), resampled hourly."""
    day_key: DayKey
    hourly_kw: pd.Series  # index: datetime (original year), values: avg power kW (hourly)


def load_pv_history_for_day(csv_path: str, value_col: str, day_key: DayKey) -> PVHistory:
    """
    Reads the CSV, filters rows matching month/day (ignoring year), converts to numeric,
    and returns hourly average kW.
    """
    df = pd.read_csv(csv_path, sep=";")
    if "timestamp" not in df.columns:
        raise ValueError("CSV must contain a 'timestamp' column")
    if value_col not in df.columns:
        raise ValueError(f"CSV does not contain the configured value column: {value_col}")

    # parse timestamps (dayfirst because format like 27.07.2023)
    ts = pd.to_datetime(df["timestamp"], dayfirst=True, errors="coerce")
    df = df.assign(ts=ts).dropna(subset=["ts"])

    # numeric conversion with decimal comma
    values = (
        df[value_col]
        .astype(str)
        .str.replace(".", "", regex=False)      # just in case thousands sep appears
        .str.replace(",", ".", regex=False)
    )
    df = df.assign(val=pd.to_numeric(values, errors="coerce")).dropna(subset=["val"])

    # filter by month/day only
    mask = (df["ts"].dt.month == day_key.month) & (df["ts"].dt.day == day_key.day)
    day_df = df.loc[mask, ["ts", "val"]].copy()
    if day_df.empty:
        raise ValueError(f"No PV rows found for month/day={day_key.month:02d}-{day_key.day:02d} in CSV")

    # ensure time order
    day_df = day_df.sort_values("ts").set_index("ts")

    # assume val is power (kW) in 15-min. We'll resample to hourly mean kW.
    hourly = day_df["val"].resample("1H").mean()

    # fill missing hours (if any) with 0
    hourly = hourly.asfreq("1H", fill_value=0.0)

    return PVHistory(day_key=day_key, hourly_kw=hourly)
