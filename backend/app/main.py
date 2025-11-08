from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PCRP Backend", version="4.0.0")

# Strict CORS: GitHub Pages + localhost dev
origins = [
    "https://atharvbyadav.github.io",
    "https://atharvbyadav.github.io/pcrp",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your existing core routers if present in your project
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

# Include new external intelligence routers
from app.routes import external, dashboard
app.include_router(external.router)
app.include_router(dashboard.router)

@app.get("/api/health")
def health():
    return {"ok": True}
