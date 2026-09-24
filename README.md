# gitkit

Everyday git workflow for Claude Code, plus a guard that stops secrets reaching
a commit.

## Commands

| Command | For |
|---|---|
| `/commit [hint]` | Commit staged work. Reads the last 30 commits and matches their style instead of imposing one. Flags a diff that is really two changes. |
| `/branch <desc>` | Branch named in the repo's existing convention, from a freshly fetched base. |
| `/pr [hint]` | Push and open a PR with a body built from the commits. Shows the body and waits for a yes. |
| `/sync` | Rebase or merge onto the base branch, following the repo's `pull.rebase`. Stops on conflict. |
| `/undo [what]` | Undo the last operation after stating in plain words what it discards. |
| `/guard [check\|install\|uninstall\|run]` | Manage the staged-secret scanner. |
| `/plainly [text]` | Say something again in plain language. Not git-specific — it lives here because this is the utility plugin. |

## /plainly

With no argument it rewrites the previous answer; given a term it explains that
term; given pasted text it rewrites that. The rules it follows: keep every fact
and caveat, keep the technical vocabulary (with a plain sentence in front of it),
copy commands and paths verbatim, and come out the same length or shorter. A
rewrite that is vaguer, longer, or more confident than the original has failed.

## The guard

A `PreToolUse` hook scans `git diff --cached` before any commit Claude makes.

**Blocks** (exit 2): private-key headers, `AKIA…` AWS keys, `sk-ant-…`, `sk-…`,
`ghp_`/`gho_`/`ghu_`/`ghs_`/`ghr_` tokens, `password|secret|token|api_key = "12+ chars"`,
and staged `.env` files (`.env.example` and friends are fine).

**Warns only**: `console.log(`, `debugger`, `breakpoint()`, `binding.pry`,
`pdb.set_trace(`.

Secrets are redacted in the report, so the value is not echoed into your
terminal or transcript.

### Per-repo exceptions

`.gitkit-allow` in the repo root, one regex per line, `#` for comments:

```
# fixtures use a documented fake key
AKIAIOSFODNN7EXAMPLE
```

### Covering terminal commits too

The PreToolUse hook only sees commits made through Claude. For commits you type
yourself:

```bash
~/.claude/skills/gitkit/hooks/install-git-hook.sh install
```

Per repo, never automatic, and it refuses to overwrite an existing pre-commit
hook. `uninstall` removes only its own.

The scanner has no Claude-specific imports, so `python3 hooks/scan_staged.py`
also works as a plain CI step: exit 2 means blocking findings.

## Tests

```bash
~/.claude/skills/gitkit/tests/run.sh
```

30 unit tests over the scanner plus two end-to-end suites that drive real git
repos.
