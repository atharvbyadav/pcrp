from fastapi import APIRouter
import httpx, asyncio, time
from typing import List, Dict, Any
from app.utils.cache_handler import load_threats, save_threats, trim_24h

router = APIRouter(prefix="/api/external", tags=["external"])

TTL = 300  # 5 minutes
last_fetch = 0

SOURCES = {
    "blackbook": "https://raw.githubusercontent.com/stamparm/blackbook/master/blackbook.json",
    "urlhaus": "https://urlhaus.abuse.ch/downloads/json_recent/",
    "phishyachts": "https://phish.sinking.yachts/v2/recent",
    "feodo": "https://feodotracker.abuse.ch/downloads/ipblocklist.json",
    "malwarebazaar": "https://mb-api.abuse.ch/api/v1/",
}

async def fetch_json(client: httpx.AsyncClient, url: str, use_post: bool = False):
    try:
        if use_post:
            r = await client.post(url, data={"query": "get_recent"})
        else:
            r = await client.get(url)
        r.raise_for_status()
        try:
            return r.json()
        except Exception:
            return None
    except Exception:
        return None

def normalize(results: List[Any]) -> List[Dict[str, Any]]:
    merged = []
    try:
        blackbook, urlhaus, phish, feodo, malb = results
    except Exception:
        blackbook = urlhaus = phish = feodo = malb = None

    if isinstance(blackbook, dict):
        for d in blackbook.get("domains", []):
            merged.append({
                "title": d.get("domain"),
                "source": "BlackBook",
                "risk": d.get("tag", "unknown"),
                "time": d.get("last_seen"),
                "description": d.get("category")
            })

    if isinstance(urlhaus, dict):
        for e in (urlhaus.get("urls", []) or [])[:50]:
            merged.append({
                "title": e.get("url"),
                "source": "URLHaus",
                "risk": e.get("threat", "malware"),
                "time": e.get("date_added"),
                "description": e.get("url_status")
            })

    if isinstance(phish, list):
        for e in phish[:50]:
            merged.append({
                "title": e.get("url"),
                "source": "PhishYachts",
                "risk": "phishing",
                "time": e.get("date_added"),
                "description": e.get("target")
            })

    if isinstance(feodo, dict):
        for ip in (feodo.get("ipblocklist", []) or [])[:50]:
            merged.append({
                "title": ip.get("ip_address"),
                "source": "FeodoTracker",
                "risk": "C2",
                "time": ip.get("first_seen"),
                "description": f"Botnet: {ip.get('botnet')}"
            })

    if isinstance(malb, dict) and malb.get("data"):
        for e in malb["data"][:50]:
            merged.append({
                "title": e.get("sha256_hash"),
                "source": "MalwareBazaar",
                "risk": e.get("signature") or "malware",
                "time": e.get("first_seen"),
                "description": e.get("file_name")
            })

    return trim_24h(merged)

@router.get("/threats")
async def get_threats():
    global last_fetch
    cached = load_threats()
    if last_fetch and (time.time() - last_fetch) < TTL and cached.get("items"):
        return {"items": cached["items"], "last_updated": cached.get("last_updated")}

    async with httpx.AsyncClient(timeout=15.0) as client:
        results = await asyncio.gather(
            fetch_json(client, SOURCES["blackbook"]),
            fetch_json(client, SOURCES["urlhaus"]),
            fetch_json(client, SOURCES["phishyachts"]),
            fetch_json(client, SOURCES["feodo"]),
            fetch_json(client, SOURCES["malwarebazaar"], use_post=True),
        )

    merged = normalize(results)
    if not merged and cached.get("items"):
        return {"items": cached["items"], "last_updated": cached.get("last_updated")}

    save_threats(merged)
    last_fetch = time.time()
    return {"items": merged}
