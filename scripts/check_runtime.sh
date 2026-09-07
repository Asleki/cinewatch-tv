#!/usr/bin/env bash
set -eu

fail() {
  printf 'FAIL  %s\n' "$1" >&2
  exit 1
}

pass() {
  printf 'PASS  %s\n' "$1"
}

command -v python >/dev/null 2>&1 || fail 'python is required'
command -v node >/dev/null 2>&1 || fail 'node is required'
command -v npm >/dev/null 2>&1 || fail 'npm is required'
command -v git >/dev/null 2>&1 || fail 'git is required'

python_version="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")')"
python_line="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
[ "$python_line" = '3.14' ] || fail "Python 3.14 required; found $python_version"
pass "Python $python_version"

node_version="$(node --version)"
node_major="$(node -p 'process.versions.node.split(".")[0]')"
[ "$node_major" = '24' ] || fail "Node 24 required; found $node_version"
pass "Node $node_version"

npm_version="$(npm --version)"
npm_major="${npm_version%%.*}"
[ "$npm_major" = '12' ] || fail "npm 12 required; found $npm_version"
pass "npm $npm_version"

pass "$(git --version)"

if command -v psql >/dev/null 2>&1; then
  pass "$(psql --version)"
else
  printf 'INFO  psql is not installed; database client qualification is handled separately\n'
fi

if command -v gh >/dev/null 2>&1; then
  pass "$(gh --version | head -n 1)"
else
  printf 'INFO  GitHub CLI is optional for generic Linux qualification\n'
fi

printf 'PASS  CineWatch V1.2 runtime policy\n'
