---
description: Push the branch and open a pull request with a body built from the commits
argument-hint: [title hint]
allowed-tools: [Bash, Read]
---

# /pr

Title hint from the user (may be empty): $ARGUMENTS

## 1. Preconditions — check all of these before touching the network

```
gh auth status
git status --short --branch
```

Stop and explain if any of these hold:
- `gh` is not authenticated → tell the user to run `gh auth login`.
- The current branch is the default branch → a PR needs a topic branch; offer
  `/branch` to move the commits onto one.
- There are no commits ahead of the base → nothing to open a PR for.
- The tree is dirty → say which files are uncommitted and ask whether to commit
  them first. Do not quietly open a PR that omits them.

## 2. Read the branch

```
git log origin/<base>..HEAD --pretty=format:'%h %s%n%b%n---'
git diff origin/<base>...HEAD --stat
```

Read the actual diff too if the stat is small enough to be worth it. The body
must describe what the branch does, not just restate the commit subjects.

## 3. Draft the body

```markdown
## Summary
- 2–4 bullets: what changed and why. Written for a reviewer who has not seen the
  commits.

## Test plan
- How this was verified. Name the commands actually run and their result.
- List anything not covered.
```

If your session has attribution guidance for pull request descriptions, append it
at the end. If it does not, add nothing.

If the repo has `.github/pull_request_template.md`, follow that template's
structure instead of the one above.

## 4. Show it and wait

Print the title and the full body, then **ask for an explicit yes**. Opening a PR
is outward-facing and visible to other people — never create it in the same step
as showing the draft, and never treat an earlier approval as covering this one.

## 5. Open it

```
git push -u origin HEAD
gh pr create --base <base> --title "<title>" --body-file <file>
```

Write the body to a temp file rather than passing it inline, so formatting
survives. Report the PR URL.

**Never** enable auto-merge, never pass `--fill` in place of a real body, and
never mark it ready or request reviewers unless the user asked.
