#!/usr/bin/env bash
# End-to-end: drive the PreToolUse guard against a real repo with a planted key.
set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
guard="$here/../hooks/pre-commit-guard.sh"
repo="$(mktemp -d)"
trap 'rm -rf "$repo"' EXIT

git -C "$repo" init -q
git -C "$repo" config user.email test@example.com
git -C "$repo" config user.name "Test"

payload() {
  printf '{"tool_name":"Bash","cwd":"%s","tool_input":{"command":"git commit -m x"}}' "$repo"
}

fail=0
check() { # name expected_code actual_code
  if [ "$2" = "$3" ]; then
    echo "  ok   $1 (exit $3)"
  else
    echo "  FAIL $1 (expected exit $2, got $3)"
    fail=1
  fi
}

echo "e2e: staged secret must block"
printf 'AWS_KEY = "AKIAIOSFODNN7EXAMPLE"\n' > "$repo/config.py"
git -C "$repo" add config.py
out="$(payload | "$guard" 2>&1)"; check "planted AWS key blocks" 2 "$?"
case "$out" in *aws-access-key-id*) echo "  ok   report names the rule" ;; *) echo "  FAIL report missing rule: $out"; fail=1 ;; esac
case "$out" in *AKIAIOSFODNN7EXAMPLE*) echo "  FAIL report leaked the secret"; fail=1 ;; *) echo "  ok   secret is redacted in the report" ;; esac

echo "e2e: allowlisted fixture must pass"
printf 'AKIAIOSFODNN7EXAMPLE\n' > "$repo/.gitkit-allow"
payload | "$guard" >/dev/null 2>&1; check "allowlisted key passes" 0 "$?"
rm "$repo/.gitkit-allow"

echo "e2e: clean diff must pass"
git -C "$repo" reset -q
printf 'def add(a, b):\n    return a + b\n' > "$repo/config.py"
git -C "$repo" add config.py
payload | "$guard" >/dev/null 2>&1; check "clean diff passes" 0 "$?"

echo "e2e: debug leftover warns but does not block"
printf 'console.log("here")\n' > "$repo/app.js"
git -C "$repo" add app.js
out="$(payload | "$guard" 2>&1)"; check "debug leftover does not block" 0 "$?"
case "$out" in *debug-leftover*) echo "  ok   warning is reported" ;; *) echo "  FAIL warning missing: $out"; fail=1 ;; esac

echo "e2e: non-commit bash command is ignored"
printf '{"tool_name":"Bash","cwd":"%s","tool_input":{"command":"npm test"}}' "$repo" | "$guard" >/dev/null 2>&1
check "npm test ignored" 0 "$?"

echo "e2e: nothing staged is ignored"
git -C "$repo" reset -q
payload | "$guard" >/dev/null 2>&1; check "empty staging area passes" 0 "$?"

[ "$fail" = 0 ] && echo "e2e: all passed" || echo "e2e: FAILURES"
exit "$fail"
