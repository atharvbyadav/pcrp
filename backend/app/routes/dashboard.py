from fastapi import APIRouter
from ..db.database import stats_overview, recent_reports

router = APIRouter(tags=["dashboard"])

@router.get("/dashboard/stats")
async def stats():
    return stats_overview()

@router.get("/dashboard/recent")
async def recent(limit: int = 10):
    return {"items": recent_reports(limit)}