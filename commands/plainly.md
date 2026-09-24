---
description: Say it again in plain language — same facts, none of the decoding
argument-hint: [a term, some pasted text, or nothing to redo the last answer]
allowed-tools: [Read, Grep, Glob]
---

# /plainly

What to put plainly (may be empty): $ARGUMENTS

## Which mode you are in

| What came in | What to do |
|---|---|
| Nothing | Rewrite **your own previous response**. Not a summary of it — the same answer, said properly. |
| A term or short phrase (`reflog`, `PreToolUse`, `--force-with-lease`) | Explain that one thing, in the context of the work in progress. |
| A longer block of pasted text | Rewrite that text. It may be yours, someone else's, or a tool's output. |

## The standard

**Plain is not simplified.** Every fact, number, caveat, and limitation in the
original survives. If you cannot say something plainly without dropping a caveat,
keep the caveat and spend an extra sentence on it. Losing information is a failed
rewrite, however readable the result.

**Plain is not longer.** The rewrite should be the same length or shorter.
Padding, throat-clearing, and "let me walk you through this" are the opposite of
what was asked for. If your rewrite grew by half, you explained instead of
translating — cut it back.

**Translate, then name.** Keep every technical term, but put a plain sentence in
front of the first load-bearing use, so the reader ends up able to *use* the word,
not just avoid it. Stripping the vocabulary out entirely leaves someone unable to
search for the thing or talk to anyone else about it.

**Purpose before definition.** Say what something is *for* before saying what it
*is*. People place a new idea by its job much faster than by its category.

**Exact things stay exact.** Commands, file paths, flags, version numbers, error
strings, and code blocks are copied verbatim. Never paraphrase something the
reader is going to run or search for.

**No decorative analogies.** An analogy earns its place only when it carries the
actual mechanism. "A rebase replays your commits one at a time onto a newer
starting point" is a real explanation. "Think of branches like tree branches!" is
noise that makes the reader feel talked down to. When in doubt, describe the
mechanism directly.

**Keep the uncertainty.** If the original hedged because something genuinely was
not known or not verified, the rewrite hedges too. Smoothing a hedge into
confidence is the worst way to fail this command.

## Worked example

Before:

> First-match-wins per line, rules ordered most-specific first, so
> `api_key="sk-ant-…"` reports as `anthropic-api-key` rather than doubling up as
> a generic secret.

After:

> If one line sets off two alarms, you only get told once — about the more
> specific one. `api_key="sk-ant-…"` looks like an Anthropic key *and* like a
> generic `api_key = "..."` assignment, so it is reported as the Anthropic key
> and the generic match is dropped.

Same facts, same length, nothing left to decode. Note what did **not** happen:
the rule name `anthropic-api-key` stayed, because that is the string that appears
in the actual report.

And a failed rewrite of the same line, for contrast:

> The scanner is smart about not repeating itself.

True, useless, and it threw away every fact in the original.

## Before you answer

Read your rewrite once and ask: could someone act on this without going back to
the original? If not, you dropped something. Put it back.
