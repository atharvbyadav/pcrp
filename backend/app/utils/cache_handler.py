import json, os, datetime
from typing import Dict, Any, List

CACHE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache", "threats.json")

def _ensure_files():
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    if not os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "w") as f:
            json.dump({"last_updated": None, "items": []}, f)

def load_threats() -> Dict[str, Any]:
    _ensure_files()
    with open(CACHE_PATH, "r") as f:
        try:
            return json.load(f)
        except Exception:
            return {"last_updated": None, "items": []}

def save_threats(items: List[Dict[str, Any]]):
    data = {"last_updated": datetime.datetime.utcnow().isoformat() + "Z", "items": items}
    with open(CACHE_PATH, "w") as f:
        json.dump(data, f)

def trim_24h(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    now = datetime.datetime.utcnow()
    out = []
    for it in items:
        t = it.get("time") or it.get("timestamp")
        if not t:
            out.append(it)
            continue
        try:
            dt = datetime.datetime.fromisoformat(t.replace("Z","").replace("z",""))
        except Exception:
            out.append(it)
            continue
        if (now - dt).total_seconds() <= 24*3600:
            out.append(it)
    return out[-1000:]
