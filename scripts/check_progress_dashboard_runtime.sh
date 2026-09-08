#!/usr/bin/env bash
set -euo pipefail

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
python_bin="${CWTV_CHRONICLE_PYTHON:-python}"
port="${CWTV_CHRONICLE_TEST_PORT:-8893}"
expected_current="${CWTV_CHRONICLE_EXPECTED_CURRENT:-}"
dashboard_dir="$repo_root/docs/progress/dashboard"
log_file="${TMPDIR:-/tmp}/cinewatch-chronicle-dashboard-${port}.log"

if ! command -v "$python_bin" >/dev/null 2>&1; then
  printf 'FAIL  Python not found: %s\n' "$python_bin"
  exit 1
fi

"$python_bin" "$repo_root/scripts/build_progress_dashboard.py" --repo "$repo_root" --check

"$python_bin" -m http.server "$port" --bind 127.0.0.1 --directory "$dashboard_dir" >"$log_file" 2>&1 &
server_pid=$!
cleanup() {
  kill "$server_pid" >/dev/null 2>&1 || true
  wait "$server_pid" >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

ready=0
for _ in 1 2 3 4 5 6 7 8 9 10; do
  if "$python_bin" - "$port" <<'PY' >/dev/null 2>&1
import sys
import urllib.request
port = int(sys.argv[1])
with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=1) as response:
    raise SystemExit(0 if response.status == 200 else 1)
PY
  then
    ready=1
    break
  fi
  sleep 0.3
done

if [ "$ready" -ne 1 ]; then
  printf 'FAIL  dashboard HTTP server did not become ready\n'
  cat "$log_file" || true
  exit 1
fi

"$python_bin" - "$port" <<'PY'
import json
import sys
import urllib.request

port = int(sys.argv[1])
base = f"http://127.0.0.1:{port}"

def read(path: str) -> str:
    with urllib.request.urlopen(base + path, timeout=3) as response:
        if response.status != 200:
            raise SystemExit(f"HTTP {response.status} for {path}")
        return response.read().decode("utf-8")

html = read("/")
if "CineWatch TV Engineering Chronicle" not in html:
    raise SystemExit("dashboard title missing")
print("PASS  live dashboard HTML")

data = json.loads(read("/progress-data.json"))
if data["summary"]["tracked_milestones"] < 7:
    raise SystemExit("tracked milestone lineage is incomplete")
if data["summary"]["qualified_milestones"] < 6:
    raise SystemExit("qualified milestone lineage is incomplete")
print("PASS  live progress-data.json")

css = read("/dashboard.css")
js = read("/dashboard.js")
if "progress-bar" not in css or "difficulty" not in js:
    raise SystemExit("dashboard assets incomplete")
print("PASS  live dashboard assets")
PY

if [ -n "$expected_current" ]; then
  "$python_bin" - "$dashboard_dir/progress-data.json" "$expected_current" <<'PY'
import json
import sys
path, expected = sys.argv[1], sys.argv[2]
data = json.load(open(path, encoding='utf-8'))
actual = data['summary']['current_milestone']
if actual != expected:
    raise SystemExit(f'expected current milestone {expected}, got {actual}')
print(f'PASS  expected current milestone {expected}')
PY
fi

printf 'PASS  CWTV.V1.2.5.1 progress dashboard runtime smoke\n'
