"""SQLite 历史记录（F6）。

表 history：
  id, url, title, artist, output_path, status, quality, created_at
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(_PROJECT_ROOT, "data", "history.db")


class HistoryDB:
    def __init__(self, path: str = DB_PATH):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.path = path
        self._init()

    def _conn(self) -> sqlite3.Connection:
        c = sqlite3.connect(self.path)
        c.row_factory = sqlite3.Row
        return c

    def _init(self) -> None:
        with self._conn() as c:
            c.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT,
                    title TEXT,
                    artist TEXT,
                    output_path TEXT,
                    status TEXT,
                    quality TEXT,
                    created_at TEXT
                )
            """)

    def add(self, *, url: str, title: str, artist: str,
            output_path: str, status: str, quality: str) -> None:
        with self._conn() as c:
            c.execute(
                "INSERT INTO history (url,title,artist,output_path,status,quality,created_at)"
                " VALUES (?,?,?,?,?,?,?)",
                (url, title, artist, output_path, status, quality,
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    def search(self, keyword: str = "", limit: int = 500) -> list[dict]:
        kw = f"%{(keyword or '').strip()}%"
        with self._conn() as c:
            if keyword.strip():
                rows = c.execute(
                    "SELECT * FROM history WHERE title LIKE ? OR artist LIKE ? OR url LIKE ?"
                    " ORDER BY id DESC LIMIT ?", (kw, kw, kw, limit)).fetchall()
            else:
                rows = c.execute(
                    "SELECT * FROM history ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]

    def delete(self, record_id: int) -> None:
        with self._conn() as c:
            c.execute("DELETE FROM history WHERE id=?", (record_id,))

    def clear_all(self) -> None:
        with self._conn() as c:
            c.execute("DELETE FROM history")

    def count(self) -> int:
        with self._conn() as c:
            return c.execute("SELECT COUNT(*) FROM history").fetchone()[0]
