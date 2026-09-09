#!/usr/bin/env bash
set -euo pipefail

REPO="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

fail() {
  printf 'FAIL  %s\n' "$*" >&2
  exit 1
}

[ -n "${PREFIX:-}" ] || fail "CWTV.V1.2.7 runtime qualification must run in native Termux"
case "$PREFIX" in
  *com.termux*) ;;
  *) fail "PREFIX does not identify the qualified Termux host" ;;
esac

cd "$REPO"

python scripts/check_termux_linux_workflow.py

for command_name in tmux proot-distro git gh python node npm psql unzip zip sha256sum; do
  command -v "$command_name" >/dev/null 2>&1 || fail "required native command unavailable: $command_name"
done
printf 'PASS  native Termux engineering tool authority\n'

for secret_name in \
  PGPASSWORD \
  GH_TOKEN \
  GITHUB_TOKEN \
  AWS_ACCESS_KEY_ID \
  AWS_SECRET_ACCESS_KEY \
  AWS_SESSION_TOKEN
do
  if [ -n "${!secret_name:-}" ]; then
    fail "secret variable must not be globally exported during CineWatch qualification: $secret_name"
  fi
done
printf 'PASS  global secret-environment exclusion\n'

command -v cwtv-session >/dev/null 2>&1 || fail "cwtv-session is not installed in Termux PATH"
command -v cwtv-session-status >/dev/null 2>&1 || fail "cwtv-session-status is not installed in Termux PATH"

session_target="$(readlink -f "$(command -v cwtv-session)")"
status_target="$(readlink -f "$(command -v cwtv-session-status)")"
[ "$session_target" = "$REPO/scripts/termux/cwtv-session" ] || fail "cwtv-session does not resolve to repository authority"
[ "$status_target" = "$REPO/scripts/termux/cwtv-session-status" ] || fail "cwtv-session-status does not resolve to repository authority"
printf 'PASS  Termux convenience commands resolve to repository authority\n'

cwtv-session --no-attach
cwtv-session-status
printf 'PASS  governed nine-window tmux session runtime\n'

gh auth status >/dev/null 2>&1 || fail "GitHub CLI persistent authentication unavailable"
printf 'PASS  GitHub persistent authentication authority\n'

if [ -f "$HOME/.pgpass" ]; then
  mode="$(stat -c '%a' "$HOME/.pgpass")"
  [ "$mode" = "600" ] || fail ".pgpass permissions must be 600"
  printf 'PASS  .pgpass permission policy\n'
else
  printf 'INFO  .pgpass reserved until CineWatch cloud PostgreSQL provisioning\n'
fi

if command -v aws >/dev/null 2>&1; then
  printf 'PASS  AWS CLI available for named-profile workflow\n'
else
  printf 'INFO  AWS CLI reserved until cloud provisioning work requires it\n'
fi

printf 'PASS  CWTV.V1.2.7 Termux/Linux engineering workflow runtime qualification\n'
