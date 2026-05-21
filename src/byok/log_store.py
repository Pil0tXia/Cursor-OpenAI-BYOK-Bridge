"""Disk-backed request log storage for the dashboard."""

from __future__ import annotations

import json
import threading
from collections import deque
from pathlib import Path

from . import config

_LOCK = threading.RLock()
_SUMMARY_FIELDS = (
    "id",
    "method",
    "path",
    "target_path",
    "route_mode",
    "upstream_mode",
    "status_code",
    "response_status",
    "error",
    "started_at",
    "duration_ms",
    "stream_event_count",
)


def _log_path() -> Path:
    return Path(config.LOG_FILE)


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _tail_offsets(path: Path, limit: int) -> tuple[list[int], int]:
    if not path.exists():
        return [], 0

    offsets: deque[int] = deque(maxlen=limit)
    total = 0
    with path.open("r", encoding="utf-8") as file:
        while True:
            offset = file.tell()
            line = file.readline()
            if not line:
                break
            total += 1
            offsets.append(offset)
    return list(offsets), total


def _prune_locked(path: Path) -> None:
    if config.LOG_STORE_LIMIT <= 0:
        path.write_text("", encoding="utf-8")
        return

    offsets, total = _tail_offsets(path, config.LOG_STORE_LIMIT)
    if total <= config.LOG_STORE_LIMIT:
        return

    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with path.open("r", encoding="utf-8") as source, tmp_path.open(
        "w", encoding="utf-8"
    ) as target:
        for offset in offsets:
            source.seek(offset)
            target.write(source.readline())
    tmp_path.replace(path)


def store_log(entry: dict) -> None:
    if not config.DASHBOARD_ENABLED:
        return

    path = _log_path()
    payload = json.dumps(entry, ensure_ascii=False, separators=(",", ":"))
    with _LOCK:
        _ensure_parent(path)
        with path.open("a", encoding="utf-8") as file:
            file.write(payload)
            file.write("\n")
        _prune_locked(path)


def read_logs() -> list[dict]:
    if not config.DASHBOARD_ENABLED:
        return []

    return read_log_summaries()


def read_log_summaries() -> list[dict]:
    if not config.DASHBOARD_ENABLED:
        return []

    path = _log_path()
    summaries: deque[dict] = deque(maxlen=max(config.LOG_STORE_LIMIT, 0))
    if config.LOG_STORE_LIMIT <= 0:
        return []

    with _LOCK:
        if not path.exists():
            return []
        offsets, _ = _tail_offsets(path, config.LOG_STORE_LIMIT)
        with path.open("r", encoding="utf-8") as file:
            for offset in offsets:
                file.seek(offset)
                line = file.readline()
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                summaries.append(_summarize_log(entry))

    return list(reversed(summaries))


def read_log_detail(log_id: str) -> dict | None:
    if not config.DASHBOARD_ENABLED:
        return None

    path = _log_path()
    with _LOCK:
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as file:
            for line in file:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if entry.get("id") == log_id:
                    return entry
    return None


def _summarize_log(entry: dict) -> dict:
    return {key: entry.get(key) for key in _SUMMARY_FIELDS if key in entry}


def clear_logs() -> None:
    path = _log_path()
    with _LOCK:
        _ensure_parent(path)
        path.write_text("", encoding="utf-8")
