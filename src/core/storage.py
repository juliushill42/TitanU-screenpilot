"""SQLite history storage for screenshot analyses."""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional


DB_PATH = Path.home() / ".screen-copilot" / "history.db"


def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                created   TEXT    NOT NULL,
                image_name TEXT,
                ocr_text  TEXT    NOT NULL,
                explanation TEXT  NOT NULL,
                actions   TEXT    NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_created ON analyses(created DESC)")


def save(image_name: Optional[str], ocr_text: str, result: dict) -> int:
    with _conn() as conn:
        cur = conn.execute(
            "INSERT INTO analyses (created, image_name, ocr_text, explanation, actions) VALUES (?,?,?,?,?)",
            (
                datetime.utcnow().isoformat(),
                image_name,
                ocr_text,
                result.get("explanation", ""),
                json.dumps(result.get("actions", []))
            )
        )
        return cur.lastrowid


def search(query: str, limit: int = 20) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            """SELECT id, created, image_name, explanation, actions
               FROM analyses
               WHERE ocr_text LIKE ? OR explanation LIKE ?
               ORDER BY created DESC LIMIT ?""",
            (f"%{query}%", f"%{query}%", limit)
        ).fetchall()
    return [_row_to_dict(r) for r in rows]


def recent(limit: int = 20) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT id, created, image_name, explanation, actions FROM analyses ORDER BY created DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [_row_to_dict(r) for r in rows]


def delete(record_id: int) -> None:
    with _conn() as conn:
        conn.execute("DELETE FROM analyses WHERE id = ?", (record_id,))


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["actions"] = json.loads(d["actions"])
    return d
