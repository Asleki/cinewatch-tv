#!/usr/bin/env bash
set -euo pipefail

REPO="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"

fail() {
  printf 'FAIL  %s\n' "$*" >&2
  exit 1
}

case "$(uname -s)" in
  Linux) ;;
  *) fail "CI/security runtime qualification requires Linux" ;;
esac

command -v python >/dev/null 2>&1 || fail "python is unavailable"
command -v node >/dev/null 2>&1 || fail "node is unavailable"
command -v npm >/dev/null 2>&1 || fail "npm is unavailable"

python scripts/check_ci_security_quality.py --scan-repository

python -m pip check
printf 'PASS  Python dependency consistency\n'

npm audit --omit=dev --audit-level=high
printf 'PASS  production npm dependency vulnerability gate\n'

printf 'INFO  full npm advisory report follows; dev/tooling advisories are reported but do not block V1.2.8\n'
if npm audit --audit-level=high; then
  printf 'PASS  full npm advisory report has no high-severity findings\n'
else
  printf 'INFO  full npm advisory report contains a dev/tooling finding; no package surgery is performed in V1.2.8\n'
fi

AUDIT_ROOT="$(mktemp -d)"
trap 'rm -rf "$AUDIT_ROOT"' EXIT

python -m venv "$AUDIT_ROOT/venv"
PIP_NO_CACHE_DIR=1 \
  "$AUDIT_ROOT/venv/bin/python" -m pip install \
  --disable-pip-version-check \
  --no-cache-dir \
  -q \
  'pip-audit==2.10.1'

"$AUDIT_ROOT/venv/bin/python" -m pip_audit --strict services/api
printf 'PASS  Python vulnerability audit\n'

git diff --check
printf 'PASS  whitespace integrity\n'

printf 'PASS  CWTV.V1.2.8 CI/security runtime qualification\n'
