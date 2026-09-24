#!/usr/bin/env bash
# Install gitkit's scanner as a real git pre-commit hook, so commits typed in a
# terminal are checked too — not only the ones made through Claude.
#
# Usage: install-git-hook.sh {install|uninstall|check} [repo-path]
set -uo pipefail

MARKER="gitkit-guard"
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
scanner="$here/scan_staged.py"

action="${1:-check}"
repo="${2:-$PWD}"

if ! git -C "$repo" rev-parse --git-dir >/dev/null 2>&1; then
  echo "gitkit: $repo is not a git repository" >&2
  exit 1
fi

hooks_dir="$(git -C "$repo" config --get core.hooksPath || true)"
if [ -n "$hooks_dir" ]; then
  case "$hooks_dir" in /*) ;; *) hooks_dir="$repo/$hooks_dir" ;; esac
else
  git_dir="$(git -C "$repo" rev-parse --absolute-git-dir)"
  hooks_dir="$git_dir/hooks"
fi
hook="$hooks_dir/pre-commit"

is_ours() { [ -f "$hook" ] && grep -q "$MARKER" "$hook"; }

case "$action" in
  install)
    if [ -f "$hook" ] && ! is_ours; then
      echo "gitkit: $hook already exists and was not installed by gitkit." >&2
      echo "gitkit: refusing to overwrite it. Move it aside, or call the scanner" >&2
      echo "gitkit: from inside it:  \"$scanner\"" >&2
      exit 1
    fi
    mkdir -p "$hooks_dir"
    cat > "$hook" <<HOOK
#!/usr/bin/env bash
# $MARKER — installed by gitkit. Remove with:
#   "$here/install-git-hook.sh" uninstall
# Fails open: if the scanner is gone, the commit proceeds.
scanner="$scanner"
[ -f "\$scanner" ] || exit 0
if command -v python3 >/dev/null 2>&1; then py=python3
elif command -v python >/dev/null 2>&1; then py=python
else exit 0; fi
exec "\$py" "\$scanner"
HOOK
    chmod +x "$hook"
    echo "gitkit: installed pre-commit guard at $hook"
    ;;
  uninstall)
    if [ ! -f "$hook" ]; then
      echo "gitkit: no pre-commit hook at $hook"
      exit 0
    fi
    if ! is_ours; then
      echo "gitkit: $hook was not installed by gitkit — leaving it alone" >&2
      exit 1
    fi
    rm -f "$hook"
    echo "gitkit: removed $hook"
    ;;
  check)
    if is_ours; then
      echo "gitkit: guard installed at $hook"
    elif [ -f "$hook" ]; then
      echo "gitkit: a different pre-commit hook is installed at $hook"
      exit 1
    else
      echo "gitkit: no pre-commit hook installed"
      exit 1
    fi
    ;;
  *)
    echo "usage: install-git-hook.sh {install|uninstall|check} [repo-path]" >&2
    exit 64
    ;;
esac
