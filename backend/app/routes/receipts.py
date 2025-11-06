from fastapi import APIRouter
from pydantic import BaseModel
from ..db.database import get_report_by_id
from ..utils.receipts import make_receipt

router = APIRouter(tags=["receipts"])

class VerifyOut(BaseModel):
    exists: bool
    receipt_matches: bool | None = None
    expected_receipt: str | None = None

@router.get("/receipts/{report_id}", response_model=VerifyOut)
async def verify_receipt(report_id: str, receipt: str | None = None):
    r = get_report_by_id(report_id)
    if not r:
        return VerifyOut(exists=False)
    expected = make_receipt(r["id"], r["created_at"])
    return VerifyOut(
        exists=True,
        receipt_matches=(receipt == expected) if receipt else None,
        expected_receipt=expected if (not receipt) or (receipt != expected) else expected,
    )