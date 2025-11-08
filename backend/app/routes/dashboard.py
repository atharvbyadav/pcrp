from fastapi import APIRouter
from collections import Counter
from app.utils.cache_handler import load_threats

router = APIRouter(prefix="/api/external", tags=["external"])

@router.get("/stats")
def get_stats():
    cache = load_threats()
    items = cache.get("items", [])
    total = len(items)
    by_risk = Counter([ (it.get("risk") or "unknown").lower() for it in items ])
    by_source = Counter([ (it.get("source") or "unknown") for it in items ])

    top_risk = max(by_risk, key=by_risk.get) if by_risk else None
    top_source = max(by_source, key=by_source.get) if by_source else None

    return {
        "summary": {
            "total": total,
            "top_risk": top_risk,
            "top_source": top_source,
            "last_sync": cache.get("last_updated")
        },
        "breakdown": dict(by_risk),
        "sources": dict(by_source)
    }
