"""SQLite-backed request log storage for the dashboard."""

from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path

from . import config

_LOCK = threading.RLock()


def _db_path() -> Path:
    return Path(config.LOG_DB)


def _connect() -> sqlite3.Connection:
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS request_logs (
            seq INTEGER PRIMARY KEY AUTOINCREMENT,
            id TEXT NOT NULL UNIQUE,
            method TEXT,
            path TEXT,
            target_path TEXT,
            route_mode TEXT,
            upstream_mode TEXT,
            status_code INTEGER,
            response_status INTEGER,
            error TEXT,
            started_at TEXT,
            duration_ms INTEGER,
            stream_event_count INTEGER,
            body_json TEXT NOT NULL
        )
        """
    )
    return conn


def _prune(conn: sqlite3.Connection) -> None:
    if config.LOG_STORE_LIMIT <= 0:
        conn.execute("DELETE FROM request_logs")
        return

    conn.execute(
        """
        DELETE FROM request_logs
        WHERE seq NOT IN (
            SELECT seq FROM request_logs
            ORDER BY seq DESC
            LIMIT ?
        )
        """,
        (config.LOG_STORE_LIMIT,),
    )


def store_log(entry: dict) -> None:
    if not config.DASHBOARD_ENABLED:
        return

    body_json = json.dumps(entry, ensure_ascii=False, separators=(",", ":"))
    with _LOCK, _connect() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO request_logs (
                id,
                method,
                path,
                target_path,
                route_mode,
                upstream_mode,
                status_code,
                response_status,
                error,
                started_at,
                duration_ms,
                stream_event_count,
                body_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry.get("id"),
                entry.get("method"),
                entry.get("path"),
                entry.get("target_path"),
                entry.get("route_mode"),
                entry.get("upstream_mode"),
                entry.get("status_code"),
                entry.get("response_status"),
                entry.get("error"),
                entry.get("started_at"),
                entry.get("duration_ms"),
                entry.get("stream_event_count"),
                body_json,
            ),
        )
        _prune(conn)


def read_logs() -> list[dict]:
    if not config.DASHBOARD_ENABLED:
        return []

    return read_log_summaries()


def read_log_summaries() -> list[dict]:
    if not config.DASHBOARD_ENABLED or config.LOG_STORE_LIMIT <= 0:
        return []

    with _LOCK, _connect() as conn:
        rows = conn.execute(
            """
            SELECT
                id,
                method,
                path,
                target_path,
                route_mode,
                upstream_mode,
                status_code,
                response_status,
                error,
                started_at,
                duration_ms,
                stream_event_count
            FROM request_logs
            ORDER BY seq DESC
            LIMIT ?
            """,
            (config.LOG_STORE_LIMIT,),
        ).fetchall()

    return [dict(row) for row in rows]


def read_log_detail(log_id: str) -> dict | None:
    if not config.DASHBOARD_ENABLED:
        return None

    with _LOCK, _connect() as conn:
        row = conn.execute(
            "SELECT body_json FROM request_logs WHERE id = ?",
            (log_id,),
        ).fetchone()

    if row is None:
        return None

    try:
        return json.loads(row["body_json"])
    except json.JSONDecodeError:
        return None


def clear_logs() -> None:
    with _LOCK, _connect() as conn:
        conn.execute("DELETE FROM request_logs")
