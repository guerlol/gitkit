"""Scan a staged git diff for secrets and debug leftovers.

Deliberately free of Claude-specific imports: `scan_diff` is a pure function over
diff text, so the same scanner runs as a Claude hook, a git pre-commit hook, or a
CI step.
"""

import os
import re
from dataclasses import dataclass


@dataclass
class Finding:
    blocking: bool
    rule: str
    file: str
    excerpt: str


# Most specific rule first: only the first match on a line is reported, so a
# token that also looks like a generic assignment is named precisely. Secret
# rules precede debug rules, so a line with both is reported as the secret.
RULES = [
    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), True),
    ("anthropic-api-key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}"), True),
    ("openai-api-key", re.compile(r"\bsk-(?!ant-)[A-Za-z0-9]{32,}\b"), True),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36}\b"), True),
    ("aws-access-key-id", re.compile(r"\bAKIA[0-9A-Z]{16}\b"), True),
    (
        "generic-secret",
        re.compile(
            r"""(?ix)
            \b (?: password | passwd | secret | token | api[_-]?key )\b
            \s* [:=] \s*
            (['"]) [^'"]{12,} \1
            """
        ),
        True,
    ),
    (
        "debug-leftover",
        re.compile(
            r"(?x)"
            r"\bconsole\.(?: log | debug | dir ) \s*\("
            r"| \bdebugger\b"
            r"| \bbreakpoint \s*\(\s*\)"
            r"| \bbinding\.pry\b"
            r"| \bpdb\.set_trace \s*\("
        ),
        False,
    ),
]

ENV_FILE_OK = (".example", ".sample", ".template", ".dist")
MAX_EXCERPT = 120


def _is_secret_env_file(path):
    name = os.path.basename(path)
    if name == ".env":
        return True
    return name.startswith(".env.") and not name.endswith(ENV_FILE_OK)


def _mask(line, match):
    """Redact the matched value so the finding can be printed safely."""
    found = match.group(0)
    keep = 4 if len(found) > 8 else 0
    line = line.replace(found, found[:keep] + "…REDACTED")
    line = line.strip()
    return line if len(line) <= MAX_EXCERPT else line[:MAX_EXCERPT] + "…"


def _compile_allow(allow_patterns):
    compiled = []
    for pattern in allow_patterns or []:
        try:
            compiled.append(re.compile(pattern))
        except re.error:
            continue  # a broken allow pattern must never weaken the scan
    return compiled


def scan_diff(diff_text, allow_patterns=None):
    allow = _compile_allow(allow_patterns)
    findings = []
    current_file = "?"

    for raw in diff_text.splitlines():
        if raw.startswith("+++ b/"):
            current_file = raw[len("+++ b/"):].strip()
            if _is_secret_env_file(current_file) and not any(
                a.search(current_file) for a in allow
            ):
                findings.append(
                    Finding(
                        blocking=True,
                        rule="env-file",
                        file=current_file,
                        excerpt="environment file staged for commit",
                    )
                )
            continue

        if not raw.startswith("+") or raw.startswith("+++"):
            continue

        added = raw[1:]
        if any(a.search(added) for a in allow):
            continue

        for name, pattern, blocking in RULES:
            match = pattern.search(added)
            if match:
                findings.append(
                    Finding(
                        blocking=blocking,
                        rule=name,
                        file=current_file,
                        excerpt=_mask(added, match),
                    )
                )
                break

    return findings


ALLOW_FILE = ".gitkit-allow"


def load_allow_patterns(repo_root):
    path = os.path.join(repo_root, ALLOW_FILE)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    return [line.strip() for line in lines if line.strip() and not line.lstrip().startswith("#")]


def render_report(findings):
    """Return (human readable report, exit code). Exit 2 blocks the commit."""
    if not findings:
        return "", 0

    blocking = [f for f in findings if f.blocking]
    warnings = [f for f in findings if not f.blocking]
    out = []

    if blocking:
        noun = "secret" if len(blocking) == 1 else "secrets"
        out.append(f"gitkit: blocked — {len(blocking)} possible {noun} in the staged diff")
        out.append("")
        for f in blocking:
            out.append(f"  [{f.rule}] {f.file}")
            out.append(f"    {f.excerpt}")
        out.append("")
        out.append(
            "Unstage or scrub these, then commit again. If it is a test fixture, "
            f"add a regex for it to {ALLOW_FILE} in the repo root."
        )

    if warnings:
        if blocking:
            out.append("")
        out.append(f"gitkit: {len(warnings)} debug leftover(s) staged (not blocking)")
        for f in warnings:
            out.append(f"  [{f.rule}] {f.file}")
            out.append(f"    {f.excerpt}")

    return "\n".join(out), (2 if blocking else 0)


# `git`, optional global flags (-C <path>, -c k=v, --git-dir=...), then `commit`.
GIT_COMMIT_RE = re.compile(
    r"\bgit\b(?:\s+(?:-[Cc]\s+\S+|--[\w-]+(?:=\S+)?))*\s+commit\b"
)


def is_git_commit_command(command):
    return bool(GIT_COMMIT_RE.search(command or ""))


def _git(args, cwd):
    import subprocess

    try:
        done = subprocess.run(
            ["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=15
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout if done.returncode == 0 else None


def main(argv=None):
    import json
    import sys

    argv = sys.argv[1:] if argv is None else argv
    cwd = os.getcwd()

    if "--hook" in argv:
        try:
            payload = json.load(sys.stdin)
        except (json.JSONDecodeError, ValueError):
            return 0  # malformed payload must never block the user
        if payload.get("tool_name") != "Bash":
            return 0
        if not is_git_commit_command(payload.get("tool_input", {}).get("command", "")):
            return 0
        cwd = payload.get("cwd") or cwd

    diff = _git(["diff", "--cached", "--no-color", "--no-ext-diff"], cwd)
    if not diff or not diff.strip():
        return 0

    root = _git(["rev-parse", "--show-toplevel"], cwd)
    root = root.strip() if root else cwd

    text, code = render_report(scan_diff(diff, load_allow_patterns(root)))
    if text:
        print(text, file=sys.stderr)
    return code


if __name__ == "__main__":
    import sys

    sys.exit(main())
