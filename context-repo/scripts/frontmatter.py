#!/usr/bin/env python3
"""Shared YAML-frontmatter reader (SPEC-001 origin; reused by SPEC-002 hooks).

Kept dependency-free and deliberately small: the graph validator
(`validate.py`) and the deterministic guardrail hooks (`.claude/hooks/*`)
both parse frontmatter through here so the FROZEN_DOC hook never
reimplements YAML parsing (SPEC-002, "Contratos consumidos").

CLI (used by block-frozen-doc.sh):
    python3 frontmatter.py --field status <file>
prints the field value (empty line when absent/malformed), exit 0.
"""
import argparse
import re
import sys


def strip_comment(line):
    depth = 0
    for i, c in enumerate(line):
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
        elif c == "#" and depth == 0 and (i == 0 or line[i - 1] in " \t"):
            return line[:i]
    return line


def parse_frontmatter(lines):
    """Returns (fields, field_lines, malformed) with 1-indexed field_lines, or
    (None, None, True) when no/broken frontmatter block is present."""
    if not lines or lines[0].strip() != "---":
        return None, None, False
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return None, None, True

    fields = {}
    field_lines = {}
    try:
        for offset, raw in enumerate(lines[1:end_idx]):
            lineno = offset + 2
            stripped = strip_comment(raw)
            if not stripped.strip():
                continue
            m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", stripped)
            if not m:
                continue
            key, val = m.group(1), m.group(2).strip()
            fields[key] = val
            field_lines[key] = lineno
    except Exception:
        return None, None, True
    return fields, field_lines, False


def read_field(path, field):
    """Return the frontmatter field value of a doc, or None when the file is
    unreadable, has no frontmatter, or the field is absent."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
    except OSError:
        return None
    fields, _, malformed = parse_frontmatter(lines)
    if malformed or fields is None:
        return None
    return fields.get(field)


def main():
    parser = argparse.ArgumentParser(description="Read a frontmatter field")
    parser.add_argument("--field", required=True, help="frontmatter key to read")
    parser.add_argument("file", help="markdown file to inspect")
    args = parser.parse_args()
    value = read_field(args.file, args.field)
    print(value if value is not None else "")


if __name__ == "__main__":
    main()
