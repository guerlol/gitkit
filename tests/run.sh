#!/usr/bin/env bash
# Every gitkit test: unit, guard end-to-end, installer end-to-end.
set -uo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fail=0

echo "== unit =="
( cd "$here/.." && python3 -m unittest discover -s tests ) || fail=1

echo
echo "== e2e: PreToolUse guard =="
"$here/e2e.sh" || fail=1

echo
echo "== e2e: git hook installer =="
"$here/e2e-install.sh" || fail=1

echo
[ "$fail" = 0 ] && echo "ALL PASSED" || echo "FAILURES"
exit "$fail"
