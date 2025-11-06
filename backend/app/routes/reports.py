from fastapi import APIRouter
from pydantic import BaseModel, Field
from uuid import uuid4
from datetime import datetime, timezone
import json

from ..core.triage import evaluate_text
from ..db.database import insert_report
from ..utils.receipts import make_receipt

router = APIRouter(tags=["reports"])

class ReportIn(BaseModel):
    summary: str = Field(..., min_length=10, max_length=4000)
    category: str = Field(..., description="e.g., phishing, scam, malware, harassment")

class ReportOut(BaseModel):
    id: str
    score: float
    reasons: list[str]
    receipt: str
    created_at: str

@router.post("/reports", response_model=ReportOut)
async def create_report(payload: ReportIn):
    report_id = str(uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    score, reasons = evaluate_text(payload.summary)
    record = {
        "id": report_id,
        "summary": payload.summary,
        "category": payload.category,
        "score": score,
        "reasons": json.dumps(reasons),
        "created_at": created_at,
    }
    insert_report(record)

    receipt = make_receipt(report_id, created_at)
    return {
        "id": report_id,
        "score": score,
        "reasons": reasons,
        "receipt": receipt,
        "created_at": created_at,
    }