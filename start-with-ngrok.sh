#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_DIR="${ROOT_DIR}/.run"
LOG_DIR="${ROOT_DIR}/logs"
BRIDGE_PID_FILE="${RUN_DIR}/bridge.pid"
NGROK_PID_FILE="${RUN_DIR}/ngrok.pid"
PORT=8082
NGROK_LOG_FILE="${LOG_DIR}/ngrok-agent.log"

mkdir -p "${RUN_DIR}" "${LOG_DIR}"
: > "${LOG_DIR}/bridge.log"
: > "${LOG_DIR}/ngrok-agent.log"
: > "${LOG_DIR}/ngrok.stdout.log"

fail() {
  echo "Error: $*" >&2
  exit 1
}

is_running() {
  local pid_file="$1"
  [[ -f "${pid_file}" ]] && kill -0 "$(cat "${pid_file}")" >/dev/null 2>&1
}

start_bg() {
  local pid_file="$1"
  local log_file="$2"
  shift 2

  if is_running "${pid_file}"; then
    echo "$(basename "${pid_file}" .pid) already running: pid $(cat "${pid_file}")"
    return
  fi

  nohup "$@" > "${log_file}" 2>&1 &
  echo $! > "${pid_file}"
  echo "$(basename "${pid_file}" .pid) started: pid $(cat "${pid_file}")"
}

[[ -f "${ROOT_DIR}/.env" ]] || fail "missing ${ROOT_DIR}/.env"
[[ -x "${ROOT_DIR}/.venv/bin/python" ]] || fail "missing ${ROOT_DIR}/.venv/bin/python"
command -v ngrok >/dev/null 2>&1 || fail "ngrok not found in PATH"

(
  cd "${ROOT_DIR}"
  start_bg "${BRIDGE_PID_FILE}" "${LOG_DIR}/bridge.log" "${ROOT_DIR}/.venv/bin/python" run.py
)

start_bg "${NGROK_PID_FILE}" "${LOG_DIR}/ngrok.stdout.log" \
  ngrok http "${PORT}" --log "${NGROK_LOG_FILE}" --log-format logfmt --log-level info

echo
echo "Cursor OpenAI BYOK Bridge started in background."
echo "Local dashboard: http://127.0.0.1:${PORT}/"
echo "ngrok: started on your configured static domain"
echo
echo "Logs:"
echo "  Bridge: ${LOG_DIR}/bridge.log"
echo "  ngrok:  ${NGROK_LOG_FILE}"
echo "  ngrok stdout/stderr: ${LOG_DIR}/ngrok.stdout.log"
echo
echo "Stop with: ${ROOT_DIR}/stop-with-ngrok.sh"
