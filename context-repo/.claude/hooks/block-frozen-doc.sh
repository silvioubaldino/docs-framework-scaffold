#!/usr/bin/env bash
# PreToolUse hook — FROZEN_DOC guardrail (SPEC-002, contract C2 of AYD-002).
#
# Blocks Edit/Write on a governed doc whose frontmatter `status` is `approved`
# or `superseded` (frozen). Frozen docs are changed by reopening a new PR
# (draft/review) or by superseding them with a new doc — never edited in place.
#
# Reuses the SPEC-001 frontmatter parser (frontmatter.py) instead of
# reimplementing YAML parsing here (SPEC-002, "Contratos consumidos").
#
# stdin: PreToolUse event JSON.  exit 0 = allow · exit 2 = block (reason on stderr).
set -euo pipefail

input="$(cat)"

# fail-open: without jq we cannot read the event — warn and allow (see ADR-002).
if ! command -v jq >/dev/null 2>&1; then
  echo "FROZEN_DOC: jq not found — guardrail skipped (fail-open)." >&2
  exit 0
fi

file_path="$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty')"
[ -z "$file_path" ] && exit 0
# Only markdown docs carry frontmatter; a Write to a not-yet-existing file has
# nothing to freeze.
case "$file_path" in *.md) ;; *) exit 0 ;; esac
[ -f "$file_path" ] || exit 0

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# The parser lives under scripts/ in each template layout (context-repo/scripts/
# or service-repo/docs/scripts/); pick whichever exists next to this hook.
parser=""
for cand in "$here/../../scripts/frontmatter.py" "$here/../../docs/scripts/frontmatter.py"; do
  if [ -f "$cand" ]; then parser="$cand"; break; fi
done

# fail-open: parser or python3 unavailable — warn and allow (see ADR-002).
if [ -z "$parser" ] || ! command -v python3 >/dev/null 2>&1; then
  echo "FROZEN_DOC: frontmatter parser or python3 unavailable — guardrail skipped (fail-open)." >&2
  exit 0
fi

status="$(python3 "$parser" --field status "$file_path" 2>/dev/null || true)"
case "$status" in
  approved|superseded)
    echo "FROZEN_DOC: '$file_path' has status: $status and is frozen." >&2
    echo "To change it, reopen it in a new PR (status back to draft/review) or supersede it with a new doc — don't edit a frozen doc in place." >&2
    exit 2
    ;;
esac

exit 0
