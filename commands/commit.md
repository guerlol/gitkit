---
description: Commit staged work with a message that matches this repo's existing style
argument-hint: [what this change is about]
allowed-tools: [Bash, Read, Grep, Glob]
---

# /commit

Hint from the user (may be empty): $ARGUMENTS

Write a commit message that looks like it was written by whoever wrote the last
thirty commits in this repo. Do not impose a house style.

## 1. Check the identity first

```
git config user.email && git config user.name
```

If either is empty, **stop before doing anything else** and tell the user to run:

```
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
```

Never invent an identity or pass `-c user.email=...` to work around this.

## 2. Find out what is staged

```
git status --short
git diff --cached --stat
```

If nothing is staged:
- Show the modified and untracked files.
- Propose a specific set to stage and say why (e.g. "these four are the parser
  change; `notes.txt` looks unrelated").
- Ask before staging. Never `git add -A` or `git add .` on your own — that is how
  stray files and local config end up in history.

## 3. Learn the repo's conventions

```
git log --pretty=format:'%s' -30
git log -5 --pretty=format:'%B%n---'
```

Read these and decide, from evidence rather than habit:
- Conventional-commits prefixes (`feat:`, `fix:`) — used, or not?
- Subject capitalisation, trailing period, typical length.
- Are bodies used at all, and for what kind of change?
- Ticket or issue references, and their format.

A repo with thirty bare lowercase subjects does not want a conventional-commits
prefix. Match what is there.

## 4. Read the actual change

```
git diff --cached
```

If the staged diff contains two or more unrelated logical changes, say so, name
them, and offer to split into separate commits (staging by path with `git reset`
and `git add <paths>`). Make the split only if the user agrees; otherwise write
one honest message covering everything.

## 5. Write it

- Subject: imperative mood ("add", not "added"/"adds"), no trailing period unless
  the repo uses them, within the length the repo actually uses.
- Body only when the change needs it: explain **why**, not what the diff already
  shows. Wrap at 72 columns.
- If your session has attribution guidance for commit messages (a `Co-Authored-By`
  trailer), append it as a trailer. If it does not, add nothing.

## 6. Commit

Use a heredoc so newlines survive:

```
git commit -F - <<'MSG'
<subject>

<body>
MSG
```

Then report the short hash, the subject, and the file count from
`git show --stat --oneline HEAD | head -1`.

If the commit is rejected by a hook, show the hook's message verbatim and fix the
cause. Never retry with `--no-verify` to get past a hook.
