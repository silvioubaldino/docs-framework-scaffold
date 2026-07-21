#!/usr/bin/env bash
# PostToolUse hook — EVAL_REMINDER (SPEC-008, AYD-002).
#
# When a skill or agent file changes, judgment-level behavior may have shifted
# (triage level, ALIGN gate, fan-out). Nudges the human/agent to replay the
# affected evals/cases/*.md and run evals/run_evals.py before the change is
# approved (AC-6). This is a reminder, not a guardrail: running an eval for
# real needs an LLM to triage the case, which a PostToolUse hook can't do by
# itself — so it never blocks (always exit 0).
#
# stdin: PostToolUse event JSON.
set -euo pipefail

input="$(cat)"

# fail-open: without jq we cannot read the event — skip silently.
if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

file_path="$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty')"
[ -z "$file_path" ] && exit 0

case "$file_path" in
  */.claude/skills/*|.claude/skills/*|*/.claude/agents/*|.claude/agents/*)
    echo "EVAL_REMINDER: '$file_path' changed — behavior may have shifted." >&2
    echo "Replay the affected evals/cases/*.md and run 'python3 evals/run_evals.py --strict' before approving this change (see evals/README.md)." >&2
    ;;
esac

exit 0
