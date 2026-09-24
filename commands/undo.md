---
description: Undo the last git operation, after showing exactly what will be lost
argument-hint: [what you want undone]
allowed-tools: [Bash]
---

# /undo

What the user wants undone (may be empty — infer from the reflog): $ARGUMENTS

Undo is the command most likely to destroy work. The order is always: read the
state, state the consequence in plain words, get a yes, then act.

## 1. Read the state

```
git reflog -10 --date=relative
git status --short
git log --oneline -5
```

Work out what the last operation actually was: a commit, an amend, a merge, a
rebase, a reset, a branch switch, a pull.

## 2. Check for uncommitted work

If the working tree is dirty, say so explicitly and name the files. An undo that
would discard uncommitted changes requires the user to say yes to *that specific
consequence* — not a general "go ahead".

## 3. State the plan before running it

Say, in plain words, what will happen. For example:

> This undoes commit `a1b2c3d` ("add retry logic"). The changes stay in your
> working tree as uncommitted edits. Nothing is lost.

versus

> This discards commit `a1b2c3d` **and** its changes. The only way back is the
> reflog, for about 90 days.

Then pick the right tool:

| Situation | Command | Loses work? |
|---|---|---|
| Undo last commit, keep changes staged | `git reset --soft HEAD~1` | no |
| Undo last commit, keep changes unstaged | `git reset --mixed HEAD~1` | no |
| Undo last commit and its changes | `git reset --hard HEAD~1` | **yes** |
| Undo an amend | `git reset --soft HEAD@{1}` | no |
| Abort an in-progress rebase/merge | `git rebase --abort` / `git merge --abort` | no |
| Unstage a file | `git restore --staged <path>` | no |
| Discard edits to a file | `git restore <path>` | **yes** |
| Undo a pushed commit | `git revert <sha>` | no |

## 4. Guard rails

- If the commit has been pushed, prefer `git revert`. Rewriting pushed history
  requires a force push, which breaks other people's clones — only do it if the
  user explicitly says the branch is theirs alone, and use
  `--force-with-lease`, never `--force`.
- Never run `git reset --hard`, `git clean`, or a force push without a yes to
  that exact command.
- Never `git stash drop` or `git reflog expire` as part of an undo.

## 5. After

Show `git log --oneline -3` and `git status --short` so the user can see where
they landed. If anything recoverable was moved, tell them the reflog entry that
gets it back.
