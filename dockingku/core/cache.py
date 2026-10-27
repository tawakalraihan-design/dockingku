"""Cache HTTP di SQLite, supaya database online tidak dipanggil dua kali."""
import sqlite3
import time
from pathlib import Path

import httpx

from dockingku.config import CACHE_DB


class Cache:
    def __init__(self, db: Path = CACHE_DB, ttl_days: float = 30):
        db.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db, check_same_thread=False)
        self.conn.execute("CREATE TABLE IF NOT EXISTS http (key TEXT PRIMARY KEY, body BLOB, at REAL)")
        self.ttl = ttl_days * 86400

    def get(self, url: str, *, method: str = "GET", json=None, data=None, timeout: float = 60) -> bytes:
        key = f"{method} {url} {json or ''} {data or ''}"
        row = self.conn.execute("SELECT body, at FROM http WHERE key = ?", (key,)).fetchone()
        if row and time.time() - row[1] < self.ttl:
            return row[0]
        resp = httpx.request(method, url, json=json, data=data, timeout=timeout, follow_redirects=True)
        resp.raise_for_status()
        self.conn.execute("REPLACE INTO http VALUES (?, ?, ?)", (key, resp.content, time.time()))
        self.conn.commit()
        return resp.content


_cache: Cache | None = None


def cache() -> Cache:
    global _cache
    if _cache is None:
        _cache = Cache()
    return _cache
