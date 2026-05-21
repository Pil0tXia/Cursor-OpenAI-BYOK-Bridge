# MODULE KNOWLEDGE BASE: src/byok/dashboard

## OVERVIEW
Dashboard module exposes UI and log-management endpoints, gated by relay API key checks.

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add dashboard page behaviour | `src/byok/dashboard/templates/index.html` | client-side rendering only |
| Change route wiring | `src/byok/dashboard/routes.py` | `register_routes` defines all dashboard endpoints |
| Change auth gate | `src/byok/dashboard/routes.py` | delegates to `proxy.is_authorized` |
| Change log payload shape | `src/byok/dashboard/routes.py` | `/api/logs` returns summaries; `/api/logs/{id}` returns one full log |

## CONVENTIONS
- Dashboard routes are registered from core app via `register_routes(app)`.
- Root `/` returns HTML only when `DASHBOARD_ENABLED=true`; otherwise JSON health-like payload.
- Logs API (`GET` and `DELETE`) exists only when `DASHBOARD_ENABLED=true`.
- Keep `/api/logs` lightweight; do not include request/response bodies in the list endpoint.

## ANTI-PATTERNS
- Do not bypass `unauthorized_response()` for `/api/logs` endpoints.
- Do not access request logs through ad hoc paths; source of truth is `byok.log_store`.
- Do not hardcode dashboard title; render from `config.DASHBOARD_TITLE`.

## LOCAL GOTCHAS
- This module imports from `..proxy`; avoid circular import expansion beyond current pattern.
- Template loader is plain file read; missing template fails at request time.
