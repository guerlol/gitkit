#!/usr/bin/env bash
# End-to-end: installing the scanner as a real git pre-commit hook.
set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
installer="$here/../hooks/install-git-hook.sh"
repo="$(mktemp -d)"
trap 'rm -rf "$repo"' EXIT

git -C "$repo" init -q
git -C "$repo" config user.email test@example.com
git -C "$repo" config user.name "Test"

fail=0
check() { if [ "$2" = "$3" ]; then echo "  ok   $1 (exit $3)"; else echo "  FAIL $1 (expected $2, got $3)"; fail=1; fi; }

echo "install: creates an executable pre-commit hook"
"$installer" install "$repo" >/dev/null 2>&1; check "install succeeds" 0 "$?"
[ -x "$repo/.git/hooks/pre-commit" ] && echo "  ok   hook is executable" || { echo "  FAIL hook not executable"; fail=1; }

echo "install: the installed hook blocks a real commit"
printf 'KEY = "AKIAIOSFODNN7EXAMPLE"\n' > "$repo/c.py"
git -C "$repo" add c.py
out="$(git -C "$repo" commit -m "add config" 2>&1)"; check "commit blocked by git hook" 1 "$?"
case "$out" in *aws-access-key-id*) echo "  ok   git printed the scanner report" ;; *) echo "  FAIL report missing: $out"; fail=1 ;; esac

echo "install: a clean commit still goes through"
printf 'x = 1\n' > "$repo/c.py"
git -C "$repo" add c.py
git -C "$repo" commit -q -m "add config" >/dev/null 2>&1; check "clean commit succeeds" 0 "$?"

echo "install: refuses to clobber a foreign hook"
"$installer" uninstall "$repo" >/dev/null 2>&1
printf '#!/bin/sh\necho mine\n' > "$repo/.git/hooks/pre-commit"
chmod +x "$repo/.git/hooks/pre-commit"
"$installer" install "$repo" >/dev/null 2>&1; check "refuses to overwrite" 1 "$?"
grep -q "echo mine" "$repo/.git/hooks/pre-commit" && echo "  ok   foreign hook untouched" || { echo "  FAIL foreign hook overwritten"; fail=1; }

echo "install: uninstall removes only our hook"
rm "$repo/.git/hooks/pre-commit"
"$installer" install "$repo" >/dev/null 2>&1
"$installer" uninstall "$repo" >/dev/null 2>&1; check "uninstall succeeds" 0 "$?"
[ -e "$repo/.git/hooks/pre-commit" ] && { echo "  FAIL hook still present"; fail=1; } || echo "  ok   hook removed"

[ "$fail" = 0 ] && echo "install: all passed" || echo "install: FAILURES"
exit "$fail"
