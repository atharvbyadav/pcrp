from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import reports, receipts, dashboard
from .db.database import init_db

app = FastAPI(title="Public Cyber Incident Reporting Portal (PCRP)")

# CORS for local React dev (Vite default port)
origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reports.router, prefix="/api")
app.include_router(receipts.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/")
def root():
    return {"message": "PCRP API is running"}