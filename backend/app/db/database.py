import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List

DB_PATH = Path(__file__).resolve().parent.parent.parent / "pcrp.sqlite3"

def connect():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY,
            summary TEXT NOT NULL,
            category TEXT NOT NULL,
            score REAL NOT NULL,
            reasons TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

def insert_report(record: Dict[str, Any]):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO reports (id, summary, category, score, reasons, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (record["id"], record["summary"], record["category"], record["score"], record["reasons"], record["created_at"]),
    )
    conn.commit()
    conn.close()

def get_report_by_id(report_id: str) -> Optional[Dict[str, Any]]:
    conn = connect()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)

def stats_overview() -> Dict[str, Any]:
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM reports")
    total = cur.fetchone()[0]
    cur.execute("SELECT category, COUNT(*) FROM reports GROUP BY category ORDER BY COUNT(*) DESC")
    by_cat = [{"category": c, "count": n} for c, n in cur.fetchall()]
    conn.close()
    return {"total_reports": total, "by_category": by_cat}

def recent_reports(limit: int = 10) -> List[Dict[str, Any]]:
    conn = connect()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM reports ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows