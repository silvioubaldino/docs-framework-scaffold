#!/usr/bin/env python3
"""Doc-graph integrity validator (SPEC-001 of AYD-002). No third-party deps.

Contract C1 (AYD-002): scripts/validate.py [--repo-root PATH]
  exit 0 -> graph OK
  exit 1 -> violations found, one line each on stdout:
    SEVERITY | RULE_ID | file:line | message
  SEVERITY: ERROR | WARN
  RULE_IDs: FRONTMATTER_MISSING, PARENT_CHILD_ASYMMETRY, SPEC_WITHOUT_AYD,
            INVALID_STATUS, BROKEN_REF, AC_WITHOUT_TEST (SPEC-005/C4: a SPEC's
            `AC-N` scenario without a `SPEC-NNN/AC-N` test reference anywhere
            in the repo — WARN while draft/review, ERROR once approved)
"""
import argparse
import os
import re
import sys

from frontmatter import parse_frontmatter

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
# SPEC-005 AC-2: test references (SPEC-NNN/AC-N) can live in any stack's test
# files, so the scan for them walks the whole tree by content, not by a fixed
# test path — these dirs are excluded as vendor/build noise, never test code.
AC_SCAN_EXCLUDED_DIR_NAMES = EXCLUDED_DIR_NAMES | {
    "dist", "build", "vendor", "venv", ".venv", "target", "coverage",
    ".next", ".turbo", "__pycache__",
}
AC_SCAN_MAX_BYTES = 2_000_000

AC_MARKER_RE = re.compile(r"^\s*#\s*AC-(\d+)\s*$")
AC_REF_RE = re.compile(r"\b(SPEC-\d+)/AC-(\d+)\b")


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
        self.ac_ids = {}   # {ac_num: line} — SPEC-005/C4, only populated for type=="spec"


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


def parse_list_value(raw):
    raw = raw.strip()
    if not raw or raw in ("[]", "null"):
        return []
    if raw.startswith("[") and raw.endswith("]"):
        raw = raw[1:-1]
    items = [item.strip() for item in raw.split(",")]
    return [item for item in items if item]


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
        if doc.type == "spec":
            doc.ac_ids = parse_ac_ids(lines)
        docs.append(doc)
    return docs


def parse_ac_ids(lines):
    """`# AC-N` comment lines (Gherkin scenario ids, SPEC-005/C4) -> {N: line}."""
    ac_ids = {}
    for i, raw in enumerate(lines):
        m = AC_MARKER_RE.match(raw)
        if m:
            ac_ids[int(m.group(1))] = i + 1
    return ac_ids


def collect_ac_references(repo_root):
    """Walk repo_root for `SPEC-NNN/AC-N` mentions in file content (SPEC-005
    edge case: tests can live anywhere, matched by content, not a fixed path).
    Governed docs are excluded — a SPEC mentioning its own AC in prose is not
    a test. Returns {spec_id: {ac_num: [(file, line), ...]}}."""
    refs = {}
    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = [d for d in dirnames if d not in AC_SCAN_EXCLUDED_DIR_NAMES]
        for name in filenames:
            path = os.path.join(dirpath, name)
            if name.endswith(".md") and is_governed(repo_root, path):
                continue
            try:
                if os.path.getsize(path) > AC_SCAN_MAX_BYTES:
                    continue
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
            except (OSError, UnicodeDecodeError):
                continue
            rel = os.path.relpath(path, repo_root)
            for lineno, line in enumerate(content.splitlines(), start=1):
                for m in AC_REF_RE.finditer(line):
                    spec_id, ac_num = m.group(1), int(m.group(2))
                    refs.setdefault(spec_id, {}).setdefault(ac_num, []).append((rel, lineno))
    return refs


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


def check_ac_without_test(doc, ac_refs, violations):
    if doc.type != "spec" or not doc.ac_ids:
        return
    covered = ac_refs.get(doc.id, {})
    severity = "ERROR" if doc.status == "approved" else "WARN"
    for ac_num, line in sorted(doc.ac_ids.items()):
        if ac_num not in covered:
            violations.append(Violation(
                severity, "AC_WITHOUT_TEST", doc.file, line, f"AC-{ac_num} sem teste"))


def check_broken_ac_refs(index, ac_refs, violations):
    for spec_id, acs in ac_refs.items():
        spec_doc = index.get(spec_id)
        for ac_num, locations in acs.items():
            if spec_doc is not None and ac_num in spec_doc.ac_ids:
                continue
            for rel, lineno in locations:
                violations.append(Violation(
                    "ERROR", "BROKEN_REF", rel, lineno,
                    f"{spec_id}/AC-{ac_num} inexistente"))


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

    ac_refs = collect_ac_references(repo_root)
    for doc in docs:
        check_ac_without_test(doc, ac_refs, violations)
    check_broken_ac_refs(index, ac_refs, violations)

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
