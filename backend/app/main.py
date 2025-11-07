from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import reports, receipts, dashboard
from .db.database import init_db
import os

app = FastAPI(title="Public Cyber Incident Reporting Portal (PCRP)")

allowed_origins = [
    "http://localhost:5173",
    "https://atharvbyadav.github.io"
]

env_allowed = os.getenv("ALLOWED_ORIGINS")
if env_allowed:
    allowed_origins.extend([o.strip() for o in env_allowed.split(",")])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/")
def root():
    return {"message": "PCRP backend running", "allowed_origins": allowed_origins}

app.include_router(reports.router, prefix="/api")
app.include_router(receipts.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
