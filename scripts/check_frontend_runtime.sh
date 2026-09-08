#!/usr/bin/env bash
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"

NODE_BIN="${CWTV_WEB_NODE:-node}"
NPM_BIN="${CWTV_WEB_NPM:-npm}"
PORT="${CWTV_WEB_PORT:-3100}"
HOST="127.0.0.1"
LOG="${TMPDIR:-/tmp}/cinewatch-v1.2.4-web-runtime.log"
SERVER_PID=""

fail() {
  printf 'FAIL  %s\n' "$1" >&2
  exit 1
}

cleanup() {
  if [ -n "$SERVER_PID" ] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

node_version="$($NODE_BIN --version 2>/dev/null || true)"
npm_version="$($NPM_BIN --version 2>/dev/null || true)"
case "$node_version" in
  v24.*) ;;
  *) fail "Node 24 required for frontend runtime qualification; found ${node_version:-missing}" ;;
esac
case "$npm_version" in
  12.*) ;;
  *) fail "npm 12 required for frontend runtime qualification; found ${npm_version:-missing}" ;;
esac

[ -d node_modules ] || fail "node_modules missing; run npm ci in the qualified Linux runtime first"

"$NPM_BIN" run lint:web
printf 'PASS  frontend lint\n'

"$NPM_BIN" run typecheck:web
printf 'PASS  frontend typecheck\n'

"$NPM_BIN" run build:web
printf 'PASS  frontend production build\n'

: > "$LOG"
"$NPM_BIN" run start -w @cinewatch/web -- --hostname "$HOST" --port "$PORT" >"$LOG" 2>&1 &
SERVER_PID=$!

for _ in $(seq 1 60); do
  if curl -fsS "http://$HOST:$PORT/" >/dev/null 2>&1; then
    break
  fi
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    cat "$LOG" >&2 || true
    fail "Next.js server exited before becoming ready"
  fi
  sleep 1
done

curl -fsS "http://$HOST:$PORT/" | grep -Fq 'CineWatch TV' || fail "frontend root smoke response missing CineWatch TV"
printf 'PASS  live /\n'

robots="$(curl -fsS "http://$HOST:$PORT/robots.txt")"
printf '%s\n' "$robots" | grep -Fq 'Disallow: /' || fail "robots.txt does not disallow private-beta indexing"
printf 'PASS  live /robots.txt private-beta policy\n'

manifest="$(curl -fsS "http://$HOST:$PORT/manifest.webmanifest")"
printf '%s\n' "$manifest" | grep -Fq '"name":"CineWatch TV"' || fail "manifest.webmanifest missing CineWatch TV identity"
printf 'PASS  live /manifest.webmanifest\n'

printf 'PASS  CWTV.V1.2.4 frontend runtime smoke\n'
