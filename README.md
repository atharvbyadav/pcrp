# PCRP — Public Cyber Incident Reporting Portal (Free, Local, Ready-to-Run)

This is a minimal, production-style **FastAPI + React (Vite)** implementation you can run 100% for free.

## Prerequisites
- Python 3.12+
- Node.js 18+ and npm
- (Optional) Docker + Docker Compose

---

## Option A — Run Locally (Simplest)

### 1) Start the API (FastAPI)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API will be at: http://localhost:8000

### 2) Start the Frontend (Vite)
Open a second terminal:
```bash
cd frontend
npm install
npm run dev
```
Frontend will be at: http://localhost:5173  
It proxies API calls to http://localhost:8000 via `vite.config.js`

---

## Option B — Run with Docker (One command)

```bash
docker compose up --build
```

- Backend: http://localhost:8000
- Frontend (served by nginx build): http://localhost:5173

> Note: In Docker mode, the frontend is served from nginx at port 5173 (mapped to container 80).
  The dev proxy is not used; your API is still at http://localhost:8000.

---

## What Works Now
- Submit a report (summary + category) → triage score + reasons → receipt returned
- Verify a receipt using report ID (and optional receipt string)
- Stats dashboard shows total reports and counts by category
- All data stored locally in `backend/pcrp.sqlite3` (SQLite)

## Next Steps (Nice to add later)
- Client-side redaction UI (mask emails/phones before submit)
- Evidence upload endpoint + hashing
- Merkle commitments batch + public log view
- Crisis-mode clustering & alerts
- STIX/TAXII export

---

## Project Structure
- `backend/` — FastAPI app with SQLite storage (no setup needed)
- `frontend/` — React + Vite SPA, with proxy to API for local dev
- `docker-compose.yml` — optional Dockerized run

## Troubleshooting
- If React can't reach API: ensure FastAPI is running on port 8000, and you started Vite dev server on 5173.
- If database file missing: the app will create `pcrp.sqlite3` automatically on first run.
- Windows PowerShell execution policy errors: run `Set-ExecutionPolicy -Scope Process Bypass` before venv activate.

---

## Demo Flow
1. Open http://localhost:5173
2. Submit a phishing-like summary (include a URL) and pick a category
3. Copy the **Report ID** and **Receipt**
4. Paste into **Verify Receipt** to see validation