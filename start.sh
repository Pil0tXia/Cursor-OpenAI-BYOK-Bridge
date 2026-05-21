#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_DIR="${ROOT_DIR}/.run"
LOG_DIR="${ROOT_DIR}/logs"
BRIDGE_PID_FILE="${RUN_DIR}/bridge.pid"

mkdir -p "${RUN_DIR}" "${LOG_DIR}"
: > "${LOG_DIR}/bridge.log"

fail() {
  echo "Error: $*" >&2
  exit 1
}

is_running() {
  [[ -f "${BRIDGE_PID_FILE}" ]] && kill -0 "$(cat "${BRIDGE_PID_FILE}")" >/dev/null 2>&1
}

[[ -f "${ROOT_DIR}/.env" ]] || fail "missing ${ROOT_DIR}/.env"
[[ -x "${ROOT_DIR}/.venv/bin/python" ]] || fail "missing ${ROOT_DIR}/.venv/bin/python"

if is_running; then
  echo "bridge already running: pid $(cat "${BRIDGE_PID_FILE}")"
else
  (
    cd "${ROOT_DIR}"
    nohup "${ROOT_DIR}/.venv/bin/python" run.py > "${LOG_DIR}/bridge.log" 2>&1 &
    echo $! > "${BRIDGE_PID_FILE}"
  )
  echo "bridge started: pid $(cat "${BRIDGE_PID_FILE}")"
fi

PORT="${PORT:-8082}"

echo
echo "Cursor OpenAI BYOK Bridge started in background."
echo "Local dashboard: http://127.0.0.1:${PORT}/"
echo
echo "Logs:"
echo "  Bridge: ${LOG_DIR}/bridge.log"
echo
echo "Stop with: ${ROOT_DIR}/stop.sh"
