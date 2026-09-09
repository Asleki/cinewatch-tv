#!/usr/bin/env bash
set -euo pipefail

repo="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$repo"

python_bin="${CWTV_API_PYTHON:-python}"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT INT TERM

"$python_bin" - <<'PY'
from importlib.metadata import version
expected = {
    "fastapi": "0.141.1",
    "pydantic": "2.13.5",
    "pydantic-settings": "2.15.0",
}
for name, wanted in expected.items():
    actual = version(name)
    if actual != wanted:
        raise SystemExit(f"FAIL  {name} expected {wanted} but found {actual}")
print("PASS  schema-producing Python dependency versions")
PY

node --version | grep -qx 'v24.18.0' || {
  printf 'FAIL  Node 24.18.0 is required for contract generation\n' >&2
  exit 1
}
npm --version | grep -qx '12.0.2' || {
  printf 'FAIL  npm 12.0.2 is required for contract generation\n' >&2
  exit 1
}

tool_version="$(
  npm exec --workspace @cinewatch/contracts -- \
    openapi-typescript --version 2>/dev/null | tr -d '\r'
)"
case "$tool_version" in
  *7.13.0*)
    printf 'PASS  openapi-typescript 7.13.0 workspace runtime authority\n'
    ;;
  *)
    printf 'FAIL  openapi-typescript expected 7.13.0 but reported: %s\n' "$tool_version" >&2
    exit 1
    ;;
esac

"$python_bin" scripts/export_openapi_contract.py --check

npm exec --workspace @cinewatch/contracts -- \
  openapi-typescript \
  "$repo/packages/contracts/openapi/cinewatch-v1.openapi.json" \
  -o "$tmp/openapi.d.ts" >/dev/null

cmp -s \
  packages/contracts/src/generated/openapi.d.ts \
  "$tmp/openapi.d.ts" || {
    printf 'FAIL  generated TypeScript OpenAPI contract is stale\n' >&2
    printf 'NEXT  run: npm run contracts:update\n' >&2
    exit 1
  }
printf 'PASS  generated TypeScript contract matches canonical OpenAPI\n'

"$python_bin" -m pytest \
  services/api/tests/test_openapi.py \
  services/api/tests/test_contract_snapshot.py \
  -q
printf 'PASS  backend OpenAPI contract tests\n'

npm run typecheck:web
printf 'PASS  frontend consumes governed TypeScript contract package\n'

printf 'PASS  CWTV.V1.2.6 OpenAPI and typed contract runtime qualification\n'
