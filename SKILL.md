---
name: gitkit
description: Use for everyday git work in this repo — writing a commit message, naming and creating a branch, opening a pull request, bringing a branch up to date, or undoing a git operation. Also holds /plainly, which re-says an answer in plain language. Triggers on "commit this", "write a commit message", "make a branch for", "open a PR", "rebase onto main", "undo that commit", "I committed a secret", "say that plainly", "what does that mean".
---

# gitkit

Everyday git, done the way this repo already does it.

## Commands

| Command | For |
|---|---|
| `/commit` | Commit staged work with a message matching the repo's existing style |
| `/branch` | Create a conventionally-named branch from a fresh base |
| `/pr` | Push and open a pull request with a real body |
| `/sync` | Rebase or merge onto the base branch, per repo config |
| `/undo` | Undo the last git operation, after showing what it costs |
| `/guard` | Manage the staged-secret scanner |
| `/plainly` | Re-say something in plain language (not git-specific) |

Each command file holds its own procedure. Read the relevant one rather than
working from memory of how git usually goes.

## Principles these commands share

**Match the repo, don't impose a style.** Before writing a commit message or a
branch name, read what is already there (`git log -30`, `git branch -a`). A repo
with thirty bare lowercase subjects does not want `feat:` prefixes.

**Never stage on your own initiative.** `git add -A` and `git add .` sweep up
local config, scratch files, and secrets. Propose a specific set of paths and ask.

**Name the consequence before a destructive command.** `reset --hard`, `restore
<path>`, force push, and `clean` all discard work. Say in plain words what will
be lost, get a yes to that specific thing, then run it.

**Never bypass a hook.** If a commit is rejected, show the message verbatim and
fix the cause. `--no-verify` is not a fix.

**Pushed history is other people's history.** Prefer `revert` over rewriting
anything already pushed. If a rewrite is genuinely wanted, use
`--force-with-lease`, never `--force`.

## The guard

A PreToolUse hook scans the staged diff before any commit Claude makes. Private
keys, AWS/Anthropic/OpenAI/GitHub tokens, `password = "..."`-style assignments,
and staged `.env` files block the commit (exit 2, with the secret redacted in the
report). `console.log`, `debugger`, and `breakpoint()` warn without blocking.

Per-repo exceptions go in `.gitkit-allow` at the repo root — one regex per line.

`/guard install` additionally installs the same scanner as a git `pre-commit`
hook, covering commits made outside Claude.
