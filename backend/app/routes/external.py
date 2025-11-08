# app/routes/external.py
from fastapi import APIRouter, HTTPException
import httpx, asyncio, time

router = APIRouter(prefix="/api/external", tags=["external"])

CACHE = {"timestamp": 0, "data": []}
CACHE_TTL = 300  # 5 minutes


@router.get("/threats")
async def get_threats():
    # serve cached if fresh
    if time.time() - CACHE["timestamp"] < CACHE_TTL:
        return {"items": CACHE["data"]}

    sources = [
        # --- General threat lists ---
        "https://raw.githubusercontent.com/stamparm/blackbook/master/blackbook.json",  # domains
        "https://urlhaus.abuse.ch/downloads/json_recent/",  # malware URLs
        # --- IP & phishing feeds ---
        "https://phish.sinking.yachts/v2/recent",           # phishing URLs
        "https://feodotracker.abuse.ch/downloads/ipblocklist.json",  # C2 IPs
        # --- Malware bazaar (abuse.ch) ---
        "https://mb-api.abuse.ch/api/v1/",                  # MalwareBazaar (requires POST for search)
    ]

    async def fetch_json(url):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                if "malwarebazaar" in url:
                    r = await client.post(url, data={"query": "get_recent"})
                else:
                    r = await client.get(url)
                r.raise_for_status()
                return r.json()
        except Exception:
            return None

    results = await asyncio.gather(*[fetch_json(u) for u in sources])

    merged = []
    # Blackbook domains
    if results[0]:
        for d in results[0].get("domains", []):
            merged.append({
                "title": d.get("domain"),
                "source": "BlackBook",
                "risk": d.get("tag", "unknown"),
                "time": d.get("last_seen"),
                "description": d.get("category")
            })
    # URLHaus
    if results[1]:
        for e in results[1].get("urls", [])[:20]:
            merged.append({
                "title": e.get("url"),
                "source": "URLHaus",
                "risk": e.get("threat", "malware"),
                "time": e.get("date_added"),
                "description": e.get("url_status")
            })
    # Sinking Yachts (Phish)
    if results[2]:
        for e in results[2][:20]:
            merged.append({
                "title": e.get("url"),
                "source": "PhishYachts",
                "risk": "phishing",
                "time": e.get("date_added"),
                "description": e.get("target")
            })
    # Feodo Tracker
    if results[3]:
        for ip in results[3].get("ipblocklist", [])[:20]:
            merged.append({
                "title": ip.get("ip_address"),
                "source": "FeodoTracker",
                "risk": "C2",
                "time": ip.get("first_seen"),
                "description": f"Botnet: {ip.get('botnet')}"
            })
    # MalwareBazaar
    if results[4] and results[4].get("data"):
        for e in results[4]["data"][:20]:
            merged.append({
                "title": e.get("sha256_hash"),
                "source": "MalwareBazaar",
                "risk": e.get("signature") or "malware",
                "time": e.get("first_seen"),
                "description": e.get("file_name")
            })

    CACHE["timestamp"] = time.time()
    CACHE["data"] = merged
    return {"items": merged}
