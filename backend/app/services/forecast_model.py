from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ForecastResult:
    hourly_pv_kw: pd.Series  # index: datetime, values: forecast kW


def fit_scale_from_yesterday(pv_yesterday_kw: pd.Series, swr_yesterday: pd.Series) -> float:
    """
    Fit a simple scale 'a' such that pv ≈ a * swr.
    Use least squares with non-negative constraint (clip).
    """
    y = pv_yesterday_kw.values.astype(float)
    x = swr_yesterday.values.astype(float)

    # avoid all zeros
    if np.nanmax(x) <= 0 or np.nanmax(y) <= 0:
        return 0.0

    # least squares a = (x·y) / (x·x)
    denom = float(np.dot(x, x))
    if denom <= 1e-9:
        return 0.0
    a = float(np.dot(x, y) / denom)
    return max(0.0, a)


def forecast_today(pv_capacity_kw: float, scale_a: float, swr_today: pd.Series) -> ForecastResult:
    """
    PV forecast = clip(scale_a * shortwave_radiation, 0..pv_capacity_kw)
    """
    pv = scale_a * swr_today.astype(float)
    pv = pv.clip(lower=0.0, upper=float(pv_capacity_kw))
    pv = pv.fillna(0.0)
    return ForecastResult(hourly_pv_kw=pv)
