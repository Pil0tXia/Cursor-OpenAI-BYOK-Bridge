#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_DIR="${ROOT_DIR}/.run"
LOG_DIR="${ROOT_DIR}/logs"

stop_one() {
  local name="$1"
  local pid_file="${RUN_DIR}/${name}.pid"

  if [[ ! -f "${pid_file}" ]]; then
    echo "${name}: not running"
    return
  fi

  local pid
  pid="$(cat "${pid_file}")"
  if kill -0 "${pid}" >/dev/null 2>&1; then
    kill "${pid}"
    for _ in $(seq 1 50); do
      if ! kill -0 "${pid}" >/dev/null 2>&1; then
        echo "${name}: stopped pid ${pid}"
        rm -f "${pid_file}"
        return
      fi
      sleep 0.2
    done

    kill -9 "${pid}" >/dev/null 2>&1 || true
    echo "${name}: force stopped pid ${pid} after 10s"
  else
    echo "${name}: stale pid ${pid}"
  fi

  rm -f "${pid_file}"
}

stop_one bridge
stop_one ngrok

echo
echo "Cursor OpenAI BYOK Bridge and ngrok stopped."
echo "Logs remain under: ${LOG_DIR}"
