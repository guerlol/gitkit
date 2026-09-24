---
description: Bring this branch up to date with its base, rebase or merge per repo config
allowed-tools: [Bash]
---

# /sync

Update the current branch against the base branch, using whichever integration
style the repo is already configured for.

## 1. Establish the situation

```
git status --short --branch
git config pull.rebase
git symbolic-ref --quiet refs/remotes/origin/HEAD
```

Determine the base branch the same way `/branch` does. If the current branch *is*
the base branch, this is just a fast-forward pull — say so and do that instead.

## 2. Protect uncommitted work

If the tree is dirty, do not proceed silently. Offer to stash
(`git stash push -m "pre-sync"`) and restore afterwards, or to stop so the user
can commit first. If you stash, you are responsible for popping it at the end and
for saying clearly if the pop conflicts.

## 3. Integrate

```
git fetch origin --quiet
```

Rebase when `pull.rebase` is `true`, or when the branch's history is linear and
unpushed. Merge when the repo's history shows merge commits on feature branches,
or when the branch is already pushed and shared. When it is genuinely ambiguous,
ask — rebasing a shared branch rewrites history other people have.

```
git rebase origin/<base>     # or: git merge origin/<base>
```

## 4. On conflict, stop

Do not resolve conflicts on your own initiative here. Report:

```
git diff --name-only --diff-filter=U
```

List the conflicted files, state whether a rebase or merge is in progress, and
give the exact abort command (`git rebase --abort` / `git merge --abort`). Then
ask whether to work through them.

## 5. Report

Say how many commits were integrated, whether the branch is now ahead/behind, and
whether a stash is still waiting to be popped.
