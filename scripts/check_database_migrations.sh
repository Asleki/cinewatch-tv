#!/usr/bin/env bash
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"

API_PYTHON="${CWTV_API_PYTHON:-$ROOT/services/api/.venv/bin/python}"

if [[ "$API_PYTHON" != */* ]]; then
  resolved_python="$(command -v -- "$API_PYTHON" || true)"
  if [[ -n "$resolved_python" ]]; then
    API_PYTHON="$resolved_python"
  fi
fi
if [ ! -x "$API_PYTHON" ]; then
  printf 'FAIL  backend virtualenv Python not found: %s\n' "$API_PYTHON" >&2
  printf 'Set CWTV_API_PYTHON to the qualified Linux backend Python.\n' >&2
  exit 1
fi

# This URL exists only to let Alembic compile PostgreSQL SQL in offline mode.
# Keep it command-scoped: it must never become application/test process state.
OFFLINE_DATABASE_URL="postgresql+psycopg://cinewatch_migration:offline-only@127.0.0.1:5432/cinewatch_dev"

"$API_PYTHON" - <<'PY'
import alembic
import psycopg
import sqlalchemy

assert sqlalchemy.__version__ == "2.0.52", sqlalchemy.__version__
assert alembic.__version__ == "1.19.2", alembic.__version__
assert psycopg.__version__ == "3.3.5", psycopg.__version__
print("PASS  SQLAlchemy 2.0.52 / Alembic 1.19.2 / Psycopg 3.3.5 runtime")
PY

auth_heads="$($API_PYTHON -m alembic -c services/api/alembic.ini heads)"
printf '%s\n' "$auth_heads"
printf '%s\n' "$auth_heads" | grep -q '^0001_postgresql_foundation (head)$'
printf 'PASS  Alembic single-head authority\n'

sql_file="$(mktemp)"
trap 'rm -f "$sql_file"' EXIT
DATABASE_URL="$OFFLINE_DATABASE_URL" \
  "$API_PYTHON" -m alembic -c services/api/alembic.ini upgrade head --sql > "$sql_file"

grep -q 'CREATE TABLE alembic_version' "$sql_file"
grep -q '0001_postgresql_foundation' "$sql_file"
if grep -qi 'sqlite' "$sql_file"; then
  printf 'FAIL  SQLite material appeared in offline migration SQL\n' >&2
  exit 1
fi
printf 'PASS  PostgreSQL offline migration SQL generation\n'

# Database configuration tests must prove startup semantics independently of
# any caller environment or the offline Alembic placeholder above.
env -u DATABASE_URL \
  "$API_PYTHON" -m pytest \
    services/api/tests/test_database_foundation.py \
    services/api/tests/test_migration_foundation.py \
    -q

printf 'PASS  offline migration URL isolated from database settings tests\n'
printf 'PASS  CWTV.V1.2.5 database migration runtime qualification\n'
