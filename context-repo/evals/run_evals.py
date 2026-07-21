#!/usr/bin/env python3
"""Behavioral eval runner (SPEC-008 of AYD-002). No third-party deps.

Cases live in `evals/cases/*.md`: a frontmatter block (`expected_*` fields — the
decision the cascade/agents SHOULD make for the case's "Pedido") plus a second
`---`-fenced block under a `## Observado` heading (`observed_*` fields — what a
replay actually produced). Replaying a case means asking the cascade to TRIAGE
the case's "Pedido" only (no execution, no real fan-out — see evals/README.md)
and writing its decision into that second block.

Reuses the SPEC-001 frontmatter parser for both blocks (same shape, `---`-fenced
key: value) instead of reimplementing YAML-lite parsing here.

Contract (echoes C1's shape, AYD-002 — not a redefinition of C1 itself):
    python3 evals/run_evals.py [--cases-dir PATH] [--strict]
    exit 0 -> no FAIL (and, without --strict, PENDING cases don't count)
    exit 1 -> at least one FAIL, or (with --strict) at least one PENDING
    one line per case on stdout:
        SEVERITY | CASE_ID | message
    SEVERITY: PASS | FAIL | PENDING
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from frontmatter import parse_frontmatter  # noqa: E402

FIELDS = ["level", "align_contrato", "align_fanout", "fanout", "docs_touched"]


def parse_list_value(raw):
    raw = raw.strip()
    if not raw or raw in ("[]", "null"):
        return []
    if raw.startswith("[") and raw.endswith("]"):
        raw = raw[1:-1]
    items = [item.strip() for item in raw.split(",")]
    return [item for item in items if item]


def normalize(field, raw):
    if raw is None:
        return None
    if field == "docs_touched":
        return parse_list_value(raw)
    if field in ("align_contrato", "align_fanout", "fanout"):
        return raw.strip().lower() == "true"
    if field == "level":
        try:
            return int(raw.strip())
        except ValueError:
            return raw.strip()
    return raw.strip()


def parse_case(path):
    """Returns (case_id, expected, observed) or (None, None, None) if unparseable.
    expected/observed are {field: normalized value}; a field absent from the
    observed block stays out of the dict entirely (case not yet replayed)."""
    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    top_fields, _, malformed = parse_frontmatter(lines)
    if malformed or top_fields is None or "id" not in top_fields:
        return None, None, None

    expected = {field: normalize(field, top_fields.get(f"expected_{field}")) for field in FIELDS}

    observed_block = []
    for i, line in enumerate(lines):
        if line.strip() == "## Observado":
            rest = lines[i + 1:]
            j = 0
            while j < len(rest) and rest[j].strip() != "---":
                j += 1
            observed_block = rest[j:]
            break

    observed_fields, _, obs_malformed = parse_frontmatter(observed_block)
    observed_fields = observed_fields or {}
    observed = {
        field: normalize(field, observed_fields.get(f"observed_{field}"))
        for field in FIELDS
        if observed_fields.get(f"observed_{field}") is not None
    }

    return top_fields["id"], expected, observed


def evaluate_case(case_id, expected, observed):
    """Returns (severity, message)."""
    if not observed:
        return "PENDING", "sem bloco ## Observado preenchido — replay pendente"

    mismatches = []
    for field in FIELDS:
        exp = expected.get(field)
        obs = observed.get(field)
        if field not in observed:
            mismatches.append(f"{field}: expected={exp} observed=<ausente>")
        elif exp != obs:
            mismatches.append(f"{field}: expected={exp} observed={obs}")

    if mismatches:
        return "FAIL", "; ".join(mismatches)
    return "PASS", "expected == observed"


def discover_cases(cases_dir):
    if not os.path.isdir(cases_dir):
        return []
    return sorted(
        os.path.join(cases_dir, name)
        for name in os.listdir(cases_dir)
        if name.endswith(".md")
    )


def run(cases_dir):
    results = []
    for path in discover_cases(cases_dir):
        case_id, expected, observed = parse_case(path)
        if case_id is None:
            results.append(("FAIL", os.path.basename(path), "case sem frontmatter/id válido"))
            continue
        severity, message = evaluate_case(case_id, expected, observed)
        results.append((severity, case_id, message))
    return results


def main():
    parser = argparse.ArgumentParser(description="Behavioral eval runner")
    parser.add_argument(
        "--cases-dir",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "cases"),
        help="directory with eval case files (default: evals/cases next to this script)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="treat PENDING cases (not yet replayed) as failures — for CI",
    )
    args = parser.parse_args()

    results = run(args.cases_dir)
    for severity, case_id, message in results:
        print(f"{severity} | {case_id} | {message}")

    has_fail = any(r[0] == "FAIL" for r in results)
    has_pending = any(r[0] == "PENDING" for r in results)
    sys.exit(1 if has_fail or (args.strict and has_pending) else 0)


if __name__ == "__main__":
    main()
