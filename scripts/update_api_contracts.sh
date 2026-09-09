#!/usr/bin/env bash
set -euo pipefail

repo="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$repo"

python_bin="${CWTV_API_PYTHON:-python}"

"$python_bin" scripts/export_openapi_contract.py
npm run contracts:generate
python scripts/check_contract_foundation.py

printf 'PASS  CWTV.V1.2.6 canonical OpenAPI and TypeScript contracts regenerated\n'
