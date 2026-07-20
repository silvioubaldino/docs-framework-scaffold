#!/usr/bin/env bash
# PreToolUse hook — GIT_SAFETY guardrail (SPEC-002, contract C2 of AYD-002).
#
# Requires explicit human approval for destructive git: `git push`,
# `git reset --hard`, and any `--force`/`-f`. The block is intentional and has
# no silent bypass — a human confirms and re-runs the command themselves.
#
# stdin: PreToolUse event JSON.  exit 0 = allow · exit 2 = block (reason on stderr).
set -euo pipefail

input="$(cat)"

# fail-open: without jq we cannot read the event — warn and allow (see ADR-002).
if ! command -v jq >/dev/null 2>&1; then
  echo "GIT_SAFETY: jq not found — guardrail skipped (fail-open)." >&2
  exit 0
fi

command="$(printf '%s' "$input" | jq -r '.tool_input.command // empty')"
[ -z "$command" ] && exit 0

# Only inspect commands that actually invoke git.
case "$command" in *git*) ;; *) exit 0 ;; esac

if printf '%s' "$command" \
  | grep -Eq 'git[[:space:]]+push|reset[[:space:]]+--hard|--force([[:space:]=]|$)|[[:space:]]-f([[:space:]]|$)'; then
  echo "GIT_SAFETY: destructive git detected (push / reset --hard / --force / -f)." >&2
  echo "This needs explicit human approval — ask the human to confirm and let them run it. Do not bypass this guardrail." >&2
  exit 2
fi

exit 0
