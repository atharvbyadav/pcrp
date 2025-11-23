from fastapi import APIRouter
import httpx, asyncio, time
from datetime import datetime, timedelta
from app.utils.cache_handler import load_threats, save_threats

router = APIRouter(prefix="/api/external", tags=["external"])

TTL = 600  # 10 minutes cache
last_fetch = 0


CISA_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
URLHAUS_URL = "https://urlhaus.abuse.ch/downloads/json_recent/"


async def fetch_json(client: httpx.AsyncClient, url: str):
    try:
        r = await client.get(url, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def filter_last_12_months(data: list):
    cutoff = datetime.utcnow() - timedelta(days=365)
    filtered = []

    for item in data:
        try:
            date_str = item.get("dateAdded") or item.get("dueDate")
            if not date_str:
                continue

            dt = datetime.fromisoformat(date_str.replace("Z",""))
            if dt >= cutoff:
                filtered.append(item)
        except:
            continue

    return filtered


def normalize(cisa, urlhaus):
    merged = []

    # --- CISA KEV ---
    if cisa and isinstance(cisa, dict):
        kev_list = cisa.get("vulnerabilities", [])
        kev_list = filter_last_12_months(kev_list)

        for v in kev_list:
            merged.append({
                "title": v.get("cveID"),
                "source": "CISA KEV",
                "risk": "exploited",
                "time": v.get("dateAdded"),
                "description": v.get("shortDescription")
            })

    # --- URLHaus ---
    if urlhaus and isinstance(urlhaus, dict):
        for e in (urlhaus.get("urls") or [])[:200]:  # Trim to reduce load
            merged.append({
                "title": e.get("url"),
                "source": "URLHaus",
                "risk": e.get("threat", "malware"),
                "time": e.get("date_added"),
                "description": e.get("url_status"),
            })

    return merged


@router.get("/threats")
async def get_threats():
    global last_fetch

    cached = load_threats()

    if last_fetch and (time.time() - last_fetch) < TTL and cached.get("items"):
        return {
            "items": cached["items"],
            "last_updated": cached.get("last_updated")
        }

    async with httpx.AsyncClient() as client:
        cisa, urlhaus = await asyncio.gather(
            fetch_json(client, CISA_URL),
            fetch_json(client, URLHAUS_URL),
        )

    merged = normalize(cisa, urlhaus)

    # Always fallback to CISA (it NEVER goes down)
    if not merged and cisa:
        merged = normalize(cisa, None)

    save_threats(merged)
    last_fetch = time.time()

    return {
        "items": merged,
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }
