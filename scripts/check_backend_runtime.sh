#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

python_bin="${CWTV_API_PYTHON:-$repo_root/services/api/.venv/bin/python}"
port="${CWTV_API_TEST_PORT:-8877}"
log_file="${TMPDIR:-/tmp}/cwtv-v123-uvicorn.log"

if [[ ! -x "$python_bin" ]]; then
  printf 'FAIL  backend virtualenv Python not found: %s\n' "$python_bin" >&2
  printf 'Create it with: python -m venv services/api/.venv\n' >&2
  exit 1
fi

"$python_bin" -m compileall -q services/api/cinewatch_api
"$python_bin" -m pytest services/api/tests -q

"$python_bin" -m uvicorn cinewatch_api.main:app \
  --app-dir services/api \
  --host 127.0.0.1 \
  --port "$port" \
  --log-level warning \
  >"$log_file" 2>&1 &
server_pid=$!

cleanup() {
  kill "$server_pid" 2>/dev/null || true
  wait "$server_pid" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

ready=0
for _ in 1 2 3 4 5 6 7 8 9 10; do
  if "$python_bin" - "$port" <<'PY_PROBE' >/dev/null 2>&1
import sys
import urllib.request

port = sys.argv[1]
with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1) as response:
    if response.status != 200:
        raise SystemExit(1)
PY_PROBE
  then
    ready=1
    break
  fi
  sleep 0.5
done

if [[ "$ready" -ne 1 ]]; then
  printf 'FAIL  uvicorn did not become ready; log follows\n' >&2
  cat "$log_file" >&2 || true
  exit 1
fi

"$python_bin" - "$port" <<'PY_VERIFY'
import json
import sys
import urllib.request

port = sys.argv[1]
request_id = "cwtv-v123-runtime-check"
request = urllib.request.Request(
    f"http://127.0.0.1:{port}/health",
    headers={"X-Request-ID": request_id},
)
with urllib.request.urlopen(request, timeout=2) as response:
    payload = json.loads(response.read())
    assert response.status == 200
    assert response.headers["X-Request-ID"] == request_id
    assert payload["status"] == "ok"
    assert payload["service"] == "cinewatch-api"

with urllib.request.urlopen(f"http://127.0.0.1:{port}/status", timeout=2) as response:
    payload = json.loads(response.read())
    assert response.status == 200
    assert payload["status"] == "ready"
    assert payload["api_version"] == "v1"

with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/v1/status", timeout=2) as response:
    payload = json.loads(response.read())
    assert response.status == 200
    assert payload["status"] == "ready"
    assert payload["api_version"] == "v1"

print("PASS  live /health")
print("PASS  request ID propagation")
print("PASS  live /status")
print("PASS  live /api/v1/status")
PY_VERIFY

printf 'PASS  CWTV.V1.2.3 backend runtime smoke\n'
