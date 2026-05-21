"""
Dashboard routes for logs and observability.
"""
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

from .. import config
from ..log_store import clear_logs, read_log_detail, read_log_summaries
from ..proxy import is_authorized, unauthorized_response

TEMPLATE_PATH = Path(__file__).parent / "templates" / "index.html"


def _load_dashboard_html() -> str:
    """Load and render the dashboard HTML template."""
    html = TEMPLATE_PATH.read_text(encoding="utf-8")
    return html.replace("{{ title }}", config.DASHBOARD_TITLE)


def register_routes(app: FastAPI) -> None:
    """Register dashboard and logs API routes."""

    @app.get("/")
    async def dashboard():
        if config.DASHBOARD_ENABLED:
            return HTMLResponse(_load_dashboard_html())
        from fastapi.responses import JSONResponse
        return JSONResponse({"service": "Cursor OpenAI BYOK Bridge", "ok": True})

    if config.DASHBOARD_ENABLED:
        @app.get("/api/logs")
        async def get_logs(req: Request):
            if not is_authorized(req):
                return unauthorized_response()
            return {"logs": read_log_summaries()}

        @app.get("/api/logs/{log_id}")
        async def get_log_detail(log_id: str, req: Request):
            if not is_authorized(req):
                return unauthorized_response()
            log = read_log_detail(log_id)
            if log is None:
                return JSONResponse(
                    status_code=404,
                    content={"error": {"message": "Log not found", "type": "not_found"}},
                )
            return {"log": log}

        @app.delete("/api/logs")
        async def delete_logs(req: Request):
            if not is_authorized(req):
                return unauthorized_response()
            clear_logs()
            return {"ok": True}
