from datetime import date
from fastapi import APIRouter, HTTPException, Query

from ..repositories.output_repo import OutputRepository
from ..schemas.output import DailyOutput

router = APIRouter()
repo = OutputRepository(base_dir="./backend/data/outputs")


@router.get("/outputs/latest", response_model=DailyOutput)
def latest():
    out = repo.load_latest()
    if not out:
        raise HTTPException(status_code=404, detail="No outputs found yet. Run /jobs/run-daily first.")
    return out


@router.get("/outputs/by-date", response_model=DailyOutput)
def by_date(d: str = Query(..., description="YYYY-MM-DD")):
    out = repo.load(date.fromisoformat(d))
    if not out:
        raise HTTPException(status_code=404, detail=f"No output found for {d}")
    return out
