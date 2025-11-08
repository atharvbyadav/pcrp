from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.utils.cache_handler import load_reports, save_reports
import hashlib, uuid, datetime

router = APIRouter(prefix="/api", tags=["reports"])

class ReportIn(BaseModel):
    summary: str
    category: str

@router.post("/reports")
def create_report(payload: ReportIn):
    db = load_reports()
    now = datetime.datetime.utcnow().isoformat() + "Z"
    rid = str(uuid.uuid4())
    keywords = ["password", "otp", "bank", "wallet", "urgent", "verify"]
    score = min(1.0, sum(1 for k in keywords if k in payload.summary.lower())/len(keywords) + 0.2)
    receipt = hashlib.sha256((rid + payload.summary + payload.category).encode()).hexdigest()

    item = {
        "id": rid,
        "summary": payload.summary,
        "category": payload.category,
        "score": score,
        "reasons": [k for k in keywords if k in payload.summary.lower()],
        "receipt": receipt,
        "created_at": now
    }
    db["items"].append(item)
    db["items"] = db["items"][-1000:]
    save_reports(db["items"])
    return item

@router.get("/receipts/{rid}")
def verify_receipt(rid: str, receipt: Optional[str] = None):
    db = load_reports()
    found = next((x for x in db["items"] if x["id"] == rid), None)
    if not found:
        return {"exists": False, "receipt_matches": None, "expected_receipt": None}
    expected = found["receipt"]
    return {
        "exists": True,
        "receipt_matches": (receipt == expected) if receipt is not None else None,
        "expected_receipt": expected
    }

@router.get("/dashboard/recent")
def recent(limit: int = 12):
    db = load_reports()
    items = sorted(db["items"], key=lambda x: x.get("created_at",""), reverse=True)[:max(0, min(limit, 200))]
    return {"items": items}
