#!/usr/bin/env bash
set -euo pipefail

if [ -z "${PREFIX:-}" ] || [ ! -d "${PREFIX:-}/bin" ]; then
  printf 'INFO  Termux PREFIX unavailable; command installation skipped\n'
  exit 0
fi

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

install_link() {
  local name="$1"
  local source="$SCRIPT_DIR/$name"
  local target="$PREFIX/bin/$name"

  [ -x "$source" ] || {
    printf 'FAIL  command source is missing or not executable: %s\n' "$source" >&2
    exit 1
  }

  if [ -e "$target" ] && [ ! -L "$target" ]; then
    printf 'FAIL  refusing to replace non-symlink command: %s\n' "$target" >&2
    exit 1
  fi

  ln -sfn "$source" "$target"
  printf 'PASS  installed %s -> %s\n' "$target" "$source"
}

install_link cwtv-session
install_link cwtv-session-status

printf 'PASS  CineWatch Termux convenience commands installed\n'
