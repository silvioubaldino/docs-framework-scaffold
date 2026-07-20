#!/usr/bin/env bash
# PreToolUse hook — SHARED_READONLY guardrail (SPEC-002, contract C2 of AYD-002).
#
# Blocks Edit/Write into the read-only mirror `*/docs/shared/**`. The shared
# layer is owned by the context-repo and mirrored into service repos; it must
# be changed at the source and re-synced, never edited in the mirror.
#
# stdin: PreToolUse event JSON.  exit 0 = allow · exit 2 = block (reason on stderr).
set -euo pipefail

input="$(cat)"

# fail-open: without jq we cannot read the event — warn and allow (see ADR-002).
if ! command -v jq >/dev/null 2>&1; then
  echo "SHARED_READONLY: jq not found — guardrail skipped (fail-open)." >&2
  exit 0
fi

file_path="$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty')"
[ -z "$file_path" ] && exit 0

# Normalize relative vs absolute so the glob matches either form.
case "$file_path" in
  docs/shared/*|*/docs/shared/*)
    echo "SHARED_READONLY: '$file_path' is inside the read-only mirror (docs/shared/**)." >&2
    echo "The shared context changes only in the context-repo, then re-syncs here. Edit it there, don't edit the mirror." >&2
    exit 2
    ;;
esac

exit 0
