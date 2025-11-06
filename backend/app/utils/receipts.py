import hashlib

def make_receipt(report_id: str, created_at_iso: str) -> str:
    # Minimal deterministic receipt: hash(id || created_at)
    data = (report_id + "|" + created_at_iso).encode("utf-8")
    return hashlib.sha256(data).hexdigest()