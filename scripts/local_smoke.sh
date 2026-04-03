#!/usr/bin/env bash
# Quick local checks before submit: imports, HTTP /health, /act (no-HTML wait path).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PORT="${LOCAL_SMOKE_PORT:-8765}"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck source=/dev/null
source .venv/bin/activate
pip install -q -r requirements.txt

python3 -m compileall -q -x '.venv' .
python3 -c "import main, agent, action_builder, navigation, state_tracker; print('imports OK')"

if command -v curl >/dev/null 2>&1; then
  uvicorn main:app --host 127.0.0.1 --port "$PORT" &
  PID=$!
  trap 'kill "$PID" 2>/dev/null || true' EXIT
  for _ in $(seq 1 30); do
    if curl -sS -o /dev/null "http://127.0.0.1:${PORT}/health" 2>/dev/null; then
      break
    fi
    sleep 0.2
  done
  curl -sS "http://127.0.0.1:${PORT}/health" | python3 -m json.tool
  curl -sS -X POST "http://127.0.0.1:${PORT}/act" \
    -H 'Content-Type: application/json' \
    -d '{"task_id":"local-smoke","task_prompt":"test","url":"http://localhost:8013/?seed=1","step_index":0,"snapshot_html":""}' \
    | python3 -m json.tool
  echo "HTTP smoke OK"
else
  echo "curl not found; skipped HTTP checks (imports + compileall passed)"
fi
