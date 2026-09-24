---
description: Create a branch named in this repo's convention, from a fresh base
argument-hint: <what you are about to work on>
allowed-tools: [Bash]
---

# /branch

What the user is about to work on: $ARGUMENTS

If that is empty, ask what the work is before doing anything — a branch name is
worthless without it.

## 1. Learn the naming convention

```
git branch -a --format='%(refname:short)' | head -40
```

Infer the prefix actually in use: `feat/`, `feature/`, `fix/`, `bug/`,
`<initials>/`, or no prefix at all. Match the majority. Do not introduce a prefix
the repo has never used.

## 2. Find the base branch

```
git symbolic-ref --quiet refs/remotes/origin/HEAD
```

If that is unset, fall back to whichever of `origin/main` or `origin/master`
exists (`git rev-parse --verify`). If neither does, ask.

## 3. Check the working tree

```
git status --short
```

If it is dirty, say so and ask which the user wants:
- carry the changes onto the new branch (plain `git switch -c` does this), or
- stash them first (`git stash push -m "pre-branch"`), or
- commit them on the current branch first.

Do not decide this silently — carrying changes across branches surprises people.

## 4. Create it

```
git fetch origin --quiet
git switch -c <prefix><slug> origin/<default-branch>
```

Slug rules: lowercase, hyphen-separated, drop filler words, aim for 3–5 words and
never exceed 50 characters. `"fix the crash when a user uploads an empty csv"`
becomes `fix/crash-on-empty-csv-upload`.

Report the new branch name and what it was branched from. If a branch with that
name already exists, say so and propose an alternative rather than switching to
the existing one.
