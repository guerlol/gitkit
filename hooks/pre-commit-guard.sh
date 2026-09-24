#!/usr/bin/env bash
# PreToolUse guard: scan the staged diff before a commit goes through.
#
# Runs on every Bash call, so it must stay cheap. The substring test below is a
# pre-filter only — scan_staged.py does the precise match. Anything unexpected
# exits 0: a broken guard must never block the user's work.
set -uo pipefail

payload="$(cat)"

case "$payload" in
  *commit*) ;;
  *) exit 0 ;;
esac

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 >/dev/null 2>&1; then
  py=python3
elif command -v python >/dev/null 2>&1; then
  py=python
else
  exit 0
fi

printf '%s' "$payload" | "$py" "$here/scan_staged.py" --hook
exit $?
