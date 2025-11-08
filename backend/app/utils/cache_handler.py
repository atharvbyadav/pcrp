import json, os, datetime
from typing import Dict, Any, List

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CACHE_PATH = os.path.join(BASE_DIR, "cache", "threats.json")
REPORTS_PATH = os.path.join(BASE_DIR, "cache", "reports.json")

def _ensure():
    os.makedirs(os.path.join(BASE_DIR, "cache"), exist_ok=True)
    if not os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "w") as f:
            json.dump({"last_updated": None, "items": []}, f)
    if not os.path.exists(REPORTS_PATH):
        with open(REPORTS_PATH, "w") as f:
            json.dump({"items": []}, f)

def load_threats() -> Dict[str, Any]:
    _ensure()
    try:
        with open(CACHE_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {"last_updated": None, "items": []}

def save_threats(items: List[Dict[str, Any]]):
    _ensure()
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

def load_reports() -> Dict[str, Any]:
    _ensure()
    try:
        with open(REPORTS_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {"items": []}

def save_reports(items: List[Dict[str, Any]]):
    _ensure()
    with open(REPORTS_PATH, "w") as f:
        json.dump({"items": items}, f)
