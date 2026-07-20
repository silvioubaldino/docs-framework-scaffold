#!/usr/bin/env python3
"""Doc-graph integrity validator (SPEC-001 of AYD-002). No third-party deps.

Contract C1 (AYD-002): scripts/validate.py [--repo-root PATH]
  exit 0 -> graph OK
  exit 1 -> violations found, one line each on stdout:
    SEVERITY | RULE_ID | file:line | message
  SEVERITY: ERROR | WARN
  RULE_IDs: FRONTMATTER_MISSING, PARENT_CHILD_ASYMMETRY, SPEC_WITHOUT_AYD,
            INVALID_STATUS, BROKEN_REF, AC_WITHOUT_TEST (reserved, WARN, not
            emitted until SPEC-005 defines AC-N ids)
"""
import argparse
import os
import re
import sys

REQUIRED_FIELDS = ["id", "type", "title", "status", "updated"]
VALID_STATUSES = {"draft", "review", "approved", "superseded", "deprecated"}
LIST_FIELDS = ["parents", "children", "related"]
NON_DOC_REF_TOKENS = {"GLO"}

GOVERNED_DIRS = {
    "design", "product_decisions", "architecture_decisions",
    "specs", "plans", "technical_decisions", "conventions", "_framework",
}
GOVERNED_SINGLETON_BASENAMES = {
    "requirements.md", "roadmap.md", "architecture.md", "changelog.md",
}
EXCLUDED_DIR_NAMES = {".git", "node_modules", ".claude", "shared"}


class Violation:
    def __init__(self, severity, rule_id, file, line, message):
        self.severity = severity
        self.rule_id = rule_id
        self.file = file
        self.line = line
        self.message = message

    def sort_key(self):
        return (self.file, self.line, self.rule_id, self.message)

    def __str__(self):
        return f"{self.severity} | {self.rule_id} | {self.file}:{self.line} | {self.message}"


class Doc:
    def __init__(self, file):
        self.file = file
        self.fields = {}
        self.field_lines = {}
        self.id = None
        self.type = None
        self.status = None
        self.parents = []
        self.children = []
        self.related = []


def is_governed(repo_root, path):
    if os.path.basename(path) in GOVERNED_SINGLETON_BASENAMES:
        return True
    # Check the full absolute directory chain (not just relative to repo-root)
    # so this still matches when --repo-root is pointed directly at e.g. design/.
    dirpath = os.path.dirname(os.path.abspath(path))
    parts = dirpath.split(os.sep)
    return any(p in GOVERNED_DIRS for p in parts)


def discover_files(repo_root):
    found = []
    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIR_NAMES]
        for name in filenames:
            if name.endswith(".md"):
                path = os.path.join(dirpath, name)
                if is_governed(repo_root, path):
                    found.append(path)
    return sorted(found)


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


def parse_list_value(raw):
    raw = raw.strip()
    if not raw or raw in ("[]", "null"):
        return []
    if raw.startswith("[") and raw.endswith("]"):
        raw = raw[1:-1]
    items = [item.strip() for item in raw.split(",")]
    return [item for item in items if item]


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


def split_ref(ref):
    if "@" in ref:
        base, repo = ref.split("@", 1)
        return base.strip(), repo.strip()
    return ref.strip(), None


def collect_docs(repo_root, files, violations):
    docs = []
    for path in files:
        rel = os.path.relpath(path, repo_root)
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()

        fields, field_lines, malformed = parse_frontmatter(lines)
        if malformed or fields is None:
            for field in REQUIRED_FIELDS:
                violations.append(Violation(
                    "ERROR", "FRONTMATTER_MISSING", rel, 1, field))
            continue

        doc_id = fields.get("id", "")
        if "NNN" in doc_id:
            continue  # template placeholder — not a real graph node

        missing = [f for f in REQUIRED_FIELDS if not fields.get(f)]
        for field in missing:
            violations.append(Violation(
                "ERROR", "FRONTMATTER_MISSING", rel, 1, field))
        if not doc_id:
            continue  # can't index without an id

        doc = Doc(rel)
        doc.fields = fields
        doc.field_lines = field_lines
        doc.id = doc_id
        doc.type = fields.get("type", "")
        doc.status = fields.get("status", "")
        doc.parents = parse_list_value(fields.get("parents", ""))
        doc.children = parse_list_value(fields.get("children", ""))
        doc.related = parse_list_value(fields.get("related", ""))
        docs.append(doc)
    return docs


def check_status(doc, violations):
    if doc.status and doc.status not in VALID_STATUSES:
        line = doc.field_lines.get("status", 1)
        violations.append(Violation(
            "ERROR", "INVALID_STATUS", doc.file, line, doc.status))


def check_spec_without_ayd(doc, index, violations):
    if doc.type != "spec":
        return
    for ref in doc.parents:
        base_id, repo = split_ref(ref)
        if repo:
            if base_id.startswith("AYD-"):
                return
        else:
            node = index.get(base_id)
            if node is not None and node.type == "design":
                return
    line = doc.field_lines.get("parents", 1)
    violations.append(Violation(
        "ERROR", "SPEC_WITHOUT_AYD", doc.file, line, "spec sem AYD parent"))


def check_parent_child_asymmetry(doc, index, violations):
    for ref in doc.children:
        cid, repo = split_ref(ref)
        if repo:
            continue
        child = index.get(cid)
        if child is None:
            continue
        parent_ids = [split_ref(p)[0] for p in child.parents]
        if doc.id not in parent_ids:
            line = child.field_lines.get("parents", 1)
            violations.append(Violation(
                "ERROR", "PARENT_CHILD_ASYMMETRY", child.file, line,
                f"falta parent {doc.id}"))
    for ref in doc.parents:
        pid, repo = split_ref(ref)
        if repo:
            continue
        parent = index.get(pid)
        if parent is None:
            continue
        child_ids = [split_ref(c)[0] for c in parent.children]
        if doc.id not in child_ids:
            line = parent.field_lines.get("children", 1)
            violations.append(Violation(
                "ERROR", "PARENT_CHILD_ASYMMETRY", parent.file, line,
                f"falta child {doc.id}"))


def check_broken_refs(doc, index, violations):
    # AC-5 also mentions `ID@repo` mentions in the body, but any such ref is by
    # definition cross-repo — unresolvable from a single --repo-root scan (AC-8) —
    # so only the frontmatter fields (parents/children/related) are checkable here.
    for field_name in LIST_FIELDS:
        line = doc.field_lines.get(field_name, 1)
        for ref in getattr(doc, field_name):
            base_id, repo = split_ref(ref)
            if repo or base_id in NON_DOC_REF_TOKENS:
                continue
            if base_id not in index:
                violations.append(Violation(
                    "ERROR", "BROKEN_REF", doc.file, line, f"{base_id} inexistente"))


def validate(repo_root):
    files = discover_files(repo_root)
    violations = []
    docs = collect_docs(repo_root, files, violations)
    index = {d.id: d for d in docs}

    for doc in docs:
        check_status(doc, violations)
        check_spec_without_ayd(doc, index, violations)
    for doc in docs:
        check_parent_child_asymmetry(doc, index, violations)
    for doc in docs:
        check_broken_refs(doc, index, violations)

    violations.sort(key=lambda v: v.sort_key())
    return violations


def main():
    parser = argparse.ArgumentParser(description="Doc-graph integrity validator")
    parser.add_argument("--repo-root", default=".", help="root to scan (default: cwd)")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    violations = validate(repo_root)
    for v in violations:
        print(v)

    has_error = any(v.severity == "ERROR" for v in violations)
    sys.exit(1 if has_error else 0)


if __name__ == "__main__":
    main()
