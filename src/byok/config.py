"""Small env-based configuration for the relay."""

from __future__ import annotations

import os


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    normalized = value.strip().lower()
    if normalized in ("1", "true", "yes", "on"):
        return True
    if normalized in ("0", "false", "no", "off"):
        return False
    return default


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    try:
        return int(value.strip())
    except ValueError:
        return default


def _get_csv_set(name: str) -> set[str]:
    value = os.getenv(name, "")
    return {item.strip() for item in value.split(",") if item.strip()}


# Server
HOST = os.getenv("HOST", "0.0.0.0")
PORT = _get_int("PORT", 8082)

# Upstream (OpenAI-compatible Responses API)
UPSTREAM_RESPONSES_API_URL = os.getenv("UPSTREAM_RESPONSES_API_URL", "").rstrip("/")
UPSTREAM_API_KEY = os.getenv("UPSTREAM_API_KEY", "")
UPSTREAM_API_KEY_HEADER = (
    os.getenv("UPSTREAM_API_KEY_HEADER", "authorization").strip().lower()
)

# Relay auth
RELAY_API_KEY = os.getenv("RELAY_API_KEY", "")

# Responses API reasoning overrides
REASONING_EFFORT = os.getenv("REASONING_EFFORT", "").strip().lower()
REASONING_MODELS = _get_csv_set("REASONING_MODELS")
REASONING_OVERRIDE = _get_bool("REASONING_OVERRIDE", False)

# Logging & Dashboard
LOG_BODY_LIMIT = _get_int("LOG_BODY_LIMIT", 20000)
LOG_STORE_LIMIT = _get_int("LOG_STORE_LIMIT", 200)
DASHBOARD_ENABLED = _get_bool("DASHBOARD_ENABLED", True)
DASHBOARD_TITLE = os.getenv("DASHBOARD_TITLE", "BYOK Relay Logs")
