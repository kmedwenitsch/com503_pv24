from datetime import date
from fastapi import APIRouter, Depends, Query
from typing import Optional

from ..core.config import settings
from ..core.timeutils import today_in_tz
from ..schemas.output import DailyOutput
from ..services.pipeline import DailyPipeline

router = APIRouter()


def get_pipeline() -> DailyPipeline:
    # late imports to avoid circulars
    from ..repositories.output_repo import OutputRepository
    from ..services.open_meteo_client import OpenMeteoClient
    from ..services.entsoe_client import EntsoeClient

    repo = OutputRepository(base_dir="./backend/data/outputs")
    open_meteo = OpenMeteoClient()
    entsoe = EntsoeClient(settings.entsoe_api_key, settings.entsoe_bidding_zone)

    return DailyPipeline(
        tz=settings.app_tz,
        lat=settings.lat,
        lon=settings.lon,
        pv_csv_path=settings.pv_csv_path,
        pv_value_column=settings.pv_value_column,
        pv_capacity_kw=settings.pv_capacity_kw,
        output_repo=repo,
        open_meteo=open_meteo,
        entsoe=entsoe,
    )


@router.post("/jobs/run-daily", response_model=DailyOutput)
def run_daily(
    run_date: Optional[str] = Query(default=None, description="YYYY-MM-DD, defaults to today in app TZ"),
    pipeline: DailyPipeline = Depends(get_pipeline),
):
    d = date.fromisoformat(run_date) if run_date else today_in_tz(settings.app_tz)
    return pipeline.run(d)
