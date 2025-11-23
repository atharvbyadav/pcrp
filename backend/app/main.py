import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PCRP Backend", version="4.0.1")

raw_origins = os.getenv("ALLOWED_ORIGINS", "")
origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    from app.routes import reports as core_reports
    app.include_router(core_reports.router)
except Exception:
    pass

try:
    from app.routes import receipts as core_receipts
    app.include_router(core_receipts.router)
except Exception:
    pass

from app.routes import external, dashboard, reports
app.include_router(external.router)
app.include_router(dashboard.router)
app.include_router(reports.router)

@app.get("/api/health")
def health():
    return {"ok": True}
