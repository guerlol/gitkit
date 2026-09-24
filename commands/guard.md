---
description: Inspect, test, or install gitkit's staged-secret guard in this repo
argument-hint: [check|install|uninstall|run]
allowed-tools: [Bash, Read, Edit]
---

# /guard

Requested action (default `check`): $ARGUMENTS

gitkit always guards commits **made through Claude** via its PreToolUse hook.
This command manages the optional second half: a real git `pre-commit` hook, so
commits you type in your own terminal are scanned too.

| Action | What to run |
|---|---|
| `check` | `"${CLAUDE_PLUGIN_ROOT}/hooks/install-git-hook.sh" check` |
| `install` | `"${CLAUDE_PLUGIN_ROOT}/hooks/install-git-hook.sh" install` |
| `uninstall` | `"${CLAUDE_PLUGIN_ROOT}/hooks/install-git-hook.sh" uninstall` |
| `run` | `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/scan_staged.py"` — scan what is staged right now and report |

Run these from the repo root. `install` is per-repo and deliberately never
automatic — tell the user which repo you are installing into and confirm first.
If a pre-commit hook from something else is already there, the installer refuses
rather than clobbering it; relay that and offer to call the scanner from inside
their existing hook instead.

## When a commit is blocked

The report names a rule and shows the offending line with the secret redacted.
Handle it in this order:

1. **It is a real secret.** Remove it from the file, put it in the environment or
   a secret store, `git add` the fix, commit again. If it was already committed
   earlier in this branch's history, say so plainly — the value must be rotated,
   because rewriting history does not un-leak it.
2. **It is a test fixture or an example.** Add a regex matching it to
   `.gitkit-allow` in the repo root, one per line, `#` for comments. Keep the
   pattern narrow — `AKIAIOSFODNN7EXAMPLE`, not `AKIA.*`.
3. **It is a false positive worth fixing properly.** The rules live in
   `hooks/scan_staged.py`. Change them with a failing test first
   (`tests/test_scan_staged.py`), then run `tests/run.sh`.

Never suggest `--no-verify` to get past the guard. If the user explicitly wants
to bypass it for a specific commit, tell them `git commit --no-verify` exists and
what it skips, but do not run it for them.
