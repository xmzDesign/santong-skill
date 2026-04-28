#!/usr/bin/env python3
"""
Claude hook/CLI: check Java/MyBatis SQL conventions on changed files.
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

JAVA_EXTENSIONS = {".java"}
SQL_EXTENSIONS = {".xml", ".sql"}
IGNORED_PARTS = {".git", ".idea", ".vscode", "target", "build", "dist", "node_modules", ".harness"}

SQL_RULE_CARD = [
    "SQL/ORM guardrails:",
    "1. SQL belongs in XML Mapper; Java annotation SQL is forbidden.",
    "2. Query columns must be explicit; select * is forbidden.",
    "3. XML parameters must use #{}; ${} is forbidden.",
    "4. Return mappings must use resultMap; resultClass is forbidden.",
    "5. Row count must use count(*); count(column) and count(constant) are forbidden.",
    "6. sum() results must be NULL-safe with IFNULL/COALESCE.",
    "7. Updated records must maintain update_time.",
    "8. Foreign keys, cascade, and stored procedures are forbidden.",
]


@dataclass
class Finding:
    severity: str
    rule: str
    path: str
    line: int
    message: str
    snippet: str

    def to_dict(self):
        return {
            "severity": self.severity,
            "rule": self.rule,
            "path": self.path,
            "line": self.line,
            "message": self.message,
            "snippet": self.snippet,
        }


def repo_root() -> Path:
    try:
        output = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
        return Path(output.decode().strip())
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return Path.cwd()


def is_relevant(path: Path) -> bool:
    return path.suffix.lower() in (JAVA_EXTENSIONS | SQL_EXTENSIONS)


def is_ignored(path: Path) -> bool:
    return any(part in IGNORED_PARTS for part in path.parts)


def git_changed_files(root: Path) -> list[Path]:
    commands = [
        ["git", "diff", "--name-only", "--diff-filter=ACMRT", "HEAD"],
        ["git", "diff", "--name-only", "--cached", "--diff-filter=ACMRT", "HEAD"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ]
    seen = set()
    files = []
    for command in commands:
        try:
            output = subprocess.check_output(command, cwd=root, stderr=subprocess.DEVNULL, timeout=10)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            continue
        for raw in output.decode().splitlines():
            rel = raw.strip()
            if not rel or rel in seen:
                continue
            seen.add(rel)
            path = root / rel
            if path.is_file() and is_relevant(path) and not is_ignored(path):
                files.append(path)
    return files


def all_relevant_files(root: Path) -> list[Path]:
    files = []
    for path in root.rglob("*"):
        if not path.is_file() or not is_relevant(path):
            continue
        if is_ignored(path):
            continue
        files.append(path)
    return files


def rel_path(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def add_finding(findings: list[Finding], severity: str, rule: str, root: Path, path: Path, line_no: int, message: str, line: str):
    findings.append(
        Finding(
            severity=severity,
            rule=rule,
            path=rel_path(root, path),
            line=line_no,
            message=message,
            snippet=line.strip()[:180],
        )
    )


def scan_java(root: Path, path: Path, findings: list[Finding]):
    text = read_text(path)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if re.search(r"@(Select|Update|Insert|Delete)\s*\(", line):
            add_finding(findings, "fail", "JAVA_ANNOTATION_SQL", root, path, line_no, "MyBatis SQL must be written in XML Mapper, not Java annotations.", line)
        if re.search(r"\bqueryForList\s*\([^;\n]+,\s*[^,\n]+,\s*[^)\n]+\)", line):
            add_finding(findings, "fail", "IBATIS_MEMORY_PAGING", root, path, line_no, "Do not use iBATIS queryForList(statementName, start, size); push paging into SQL.", line)
        if re.search(r"\b(HashMap|Hashtable)\s*<", line) and re.search(r"\b(Mapper|Dao|DAO|Repository)\b", path.name + " " + line):
            add_finding(findings, "fail", "MAP_RESULT_OUTPUT", root, path, line_no, "Do not expose HashMap/Hashtable as database query result output; define DO/DTO and resultMap.", line)


def contains_mapper_sql(text: str, path: Path) -> bool:
    lowered = text.lower()
    return (
        path.suffix.lower() == ".sql"
        or "mapper" in str(path).lower()
        or "<mapper" in lowered
        or "<select" in lowered
        or "<update" in lowered
        or "<insert" in lowered
        or "<delete" in lowered
    )


def scan_sql(root: Path, path: Path, findings: list[Finding]):
    text = read_text(path)
    if path.suffix.lower() == ".xml" and not contains_mapper_sql(text, path):
        return
    for line_no, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()
        if re.search(r"\bselect\s+\*", lowered):
            add_finding(findings, "fail", "SQL_SELECT_STAR", root, path, line_no, "Query fields must be explicit; select * is forbidden.", line)
        if "${" in line:
            add_finding(findings, "fail", "SQL_DOLLAR_PARAM", root, path, line_no, "Use #{} for XML SQL parameters; ${} is forbidden.", line)
        if re.search(r"\bresultclass\s*=", lowered):
            add_finding(findings, "fail", "MYBATIS_RESULT_CLASS", root, path, line_no, "Use explicit <resultMap>; resultClass is forbidden.", line)
        if re.search(r"\bcount\s*\(\s*(?!\*\s*\)|distinct\b)[^)]*\)", lowered):
            add_finding(findings, "fail", "SQL_COUNT_NOT_STAR", root, path, line_no, "Use count(*) for row counts; count(column/constant) is forbidden.", line)
        if re.search(r"\b(foreign\s+key|references\s+\w+|on\s+(delete|update)\s+cascade)\b", lowered):
            add_finding(findings, "fail", "SQL_FOREIGN_KEY_OR_CASCADE", root, path, line_no, "Database foreign keys and cascade actions are forbidden; enforce relationships in application/domain logic.", line)
        if re.search(r"\b(create\s+procedure|create\s+function|call\s+\w+)\b", lowered):
            add_finding(findings, "fail", "SQL_STORED_PROCEDURE", root, path, line_no, "Stored procedures/functions are forbidden for business logic.", line)
        if re.search(r"\btruncate\s+table\b", lowered):
            add_finding(findings, "warn", "SQL_TRUNCATE_TABLE", root, path, line_no, "TRUNCATE TABLE is risky in application code; confirm approval, backup, and rollback path.", line)
        if re.search(r"\bsum\s*\(", lowered) and not re.search(r"\b(ifnull|coalesce)\s*\([^;\n]*sum\s*\(", lowered):
            add_finding(findings, "warn", "SQL_SUM_NULL_SAFE", root, path, line_no, "sum() can return NULL; wrap with IFNULL/COALESCE unless caller explicitly handles NULL.", line)
        if re.search(r"\bis\s+null\b|\bis\s+not\s+null\b", lowered):
            add_finding(findings, "warn", "SQL_NULL_CHECK", root, path, line_no, "Prefer ISNULL(column) / NOT ISNULL(column) for NULL checks per project convention.", line)
        if re.search(r"\bupdate\s+\w+", lowered) and "update_time" not in lowered:
            add_finding(findings, "warn", "SQL_UPDATE_TIME", root, path, line_no, "Record updates must also maintain update_time; verify this update is exempt or add update_time.", line)


def scan_files(root: Path, files: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for path in files:
        suffix = path.suffix.lower()
        if suffix in JAVA_EXTENSIONS:
            scan_java(root, path, findings)
        elif suffix in SQL_EXTENSIONS:
            scan_sql(root, path, findings)
    return findings


def format_text(findings: list[Finding], files: list[Path]) -> str:
    if not findings:
        return f"Convention check passed ({len(files)} changed relevant files scanned)."
    fails = [item for item in findings if item.severity == "fail"]
    warns = [item for item in findings if item.severity == "warn"]
    lines = []
    lines.extend(SQL_RULE_CARD)
    lines.append("")
    lines.append(f"Convention check found {len(fails)} fail(s), {len(warns)} warn(s) in {len(files)} relevant file(s).")
    for item in findings[:60]:
        label = "FAIL" if item.severity == "fail" else "WARN"
        lines.append(f"- [{label}] {item.path}:{item.line} {item.rule}: {item.message}")
        if item.snippet:
            lines.append(f"  `{item.snippet}`")
    if len(findings) > 60:
        lines.append(f"- ... {len(findings) - 60} more finding(s) omitted.")
    if fails:
        lines.append("")
        lines.append("Do not finish yet. Fix FAIL items, rerun the check, then continue.")
    if warns:
        lines.append("WARN items require either a fix or an explicit explanation in the final response.")
    return "\n".join(lines)


def emit_hook(findings: list[Finding], files: list[Path]):
    text = format_text(findings, files)
    fails = [item for item in findings if item.severity == "fail"]
    warns = [item for item in findings if item.severity == "warn"]
    if fails:
        print(json.dumps({"decision": "block", "reason": text}, ensure_ascii=False))
        return
    if warns:
        print(json.dumps({"systemMessage": text}, ensure_ascii=False))
        return
    print(json.dumps({}))


def parse_args():
    parser = argparse.ArgumentParser(description="Check Java/MyBatis SQL coding conventions.")
    parser.add_argument("--changed-only", action="store_true", help="scan changed files only")
    parser.add_argument("--format", choices=["text", "json", "hook"], default="text")
    return parser.parse_args()


def should_run_hook() -> bool:
    raw = sys.stdin.read()
    if not raw.strip():
        return True
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return True
    if payload.get("hook_event_name") == "Stop":
        return True
    if payload.get("tool_name") == "TaskUpdate":
        tool_input = payload.get("tool_input", {})
        return isinstance(tool_input, dict) and tool_input.get("status") == "completed"
    return True


def main():
    args = parse_args()
    if args.format == "hook" and not should_run_hook():
        print(json.dumps({}))
        return
    root = repo_root()
    files = git_changed_files(root) if args.changed_only else all_relevant_files(root)
    findings = scan_files(root, files)

    if args.format == "json":
        print(
            json.dumps(
                {
                    "files_scanned": [rel_path(root, path) for path in files],
                    "findings": [item.to_dict() for item in findings],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    elif args.format == "hook":
        emit_hook(findings, files)
    else:
        print(format_text(findings, files))

    if args.format != "hook" and any(item.severity == "fail" for item in findings):
        sys.exit(1)


if __name__ == "__main__":
    main()
