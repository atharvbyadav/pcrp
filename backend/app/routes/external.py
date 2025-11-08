from fastapi import APIRouter, HTTPException
import httpx, os

router = APIRouter(prefix="/api/external", tags=["external"])

@router.get("/threats")
async def threats():
    FEED_URL = os.getenv("THREAT_FEED_URL", "https://YOUR-FREE-FEED-URL.json")
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.get(FEED_URL)
            r.raise_for_status()
            data = r.json()
            items = data if isinstance(data, list) else data.get("items", [])
            return {"items": items[:20]}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Upstream error: {e}")
