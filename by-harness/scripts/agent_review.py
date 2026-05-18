#!/usr/bin/env python3
"""Run a Codex/Claude review closeout and emit a normalized QA result."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_SKIP = "SKIP"
GATE_REQUIRED = "required"
GATE_ADVISORY = "advisory"
PRIORITY_RE = re.compile(r"\[P([0-3])\]")
MAX_PROMPT_DIFF_CHARS = 180_000
MAX_TAIL_CHARS = 12_000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run by-harness agent review closeout.")
    parser.add_argument("--target-dir", default=".", help="目标项目目录")
    parser.add_argument("--backend", default=os.environ.get("AGENT_REVIEW_BACKEND", "auto"), choices=("auto", "codex", "claude", "off"))
    parser.add_argument("--mode", default="auto", choices=("auto", "local", "branch", "commit"), help="Review target selection")
    parser.add_argument("--base", default="", help="Base ref for branch review")
    parser.add_argument("--commit", default="", help="Commit ref for commit review")
    parser.add_argument("--gate", default=GATE_ADVISORY, choices=(GATE_ADVISORY, GATE_REQUIRED), help="QA gate level")
    parser.add_argument("--codex-bin", default=os.environ.get("CODEX_BIN", "codex"), help="Codex binary")
    parser.add_argument("--claude-bin", default=os.environ.get("CLAUDE_BIN", "claude"), help="Claude binary")
    parser.add_argument("--full-access", action="store_true", help="Run nested review with permissive local permissions")
    parser.add_argument("--output", default=os.environ.get("AGENT_REVIEW_OUTPUT", ""), help="Save raw review output")
    parser.add_argument("--result-json", default="", help="Save normalized result JSON")
    parser.add_argument("--parallel-tests", default="", help="Run this shell test command concurrently with review")
    parser.add_argument("--dry-run", action="store_true", help="Print selected commands, do not run review")
    return parser.parse_args()


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def repo_root(target_dir: Path) -> Path:
    current = target_dir.resolve()
    if current.name == ".harness":
        current = current.parent
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(current),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return Path(completed.stdout.strip()).resolve()
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"not a git repository: {current}: {exc.stderr.strip()}") from exc


def run_capture(command: list[str], cwd: Path, *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd),
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def git_output(root: Path, *args: str) -> str:
    completed = run_capture(["git", *args], root)
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def command_available(command: str) -> bool:
    return shutil.which(command) is not None


def shell_quote(command: list[str]) -> str:
    return " ".join(shlex_quote(part) for part in command)


def shlex_quote(value: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_@%+=:,./-]+", value):
        return value
    return "'" + value.replace("'", "'\"'\"'") + "'"


def get_pr_base(root: Path) -> tuple[str, str]:
    if not command_available("gh"):
        return "", ""
    completed = run_capture(
        ["gh", "pr", "view", "--json", "baseRefName,url", "--jq", "[.baseRefName, .url] | @tsv"],
        root,
    )
    if completed.returncode != 0:
        return "", ""
    line = completed.stdout.strip()
    if not line:
        return "", ""
    parts = line.split("\t", 1)
    base_name = parts[0].strip()
    pr_url = parts[1].strip() if len(parts) > 1 else ""
    return (f"origin/{base_name}", pr_url) if base_name else ("", pr_url)


def detect_target(root: Path, mode: str, base_ref: str, commit_ref: str) -> dict[str, Any]:
    current_branch = git_output(root, "branch", "--show-current") or "detached"
    dirty = bool(git_output(root, "status", "--porcelain"))
    pr_url = ""
    resolved_base = base_ref
    if not resolved_base and mode != "local":
        resolved_base, pr_url = get_pr_base(root)
    if not resolved_base:
        resolved_base = "origin/main"

    if mode == "local" or (mode == "auto" and dirty):
        kind = "local"
    elif mode == "commit":
        kind = "commit"
    elif mode == "branch" or (mode == "auto" and current_branch != "main" and current_branch != "detached"):
        kind = "branch"
    else:
        kind = "none"

    return {
        "kind": kind,
        "branch": current_branch,
        "dirty": dirty,
        "base": resolved_base,
        "commit": commit_ref or "HEAD",
        "pr_url": pr_url,
    }


def build_codex_command(args: argparse.Namespace, target: dict[str, Any]) -> list[str]:
    command = [args.codex_bin]
    if args.full_access:
        command.append("--dangerously-bypass-approvals-and-sandbox")
    command.append("review")
    kind = target["kind"]
    if kind == "local":
        command.append("--uncommitted")
    elif kind == "branch":
        command.extend(["--base", str(target["base"])])
    elif kind == "commit":
        command.extend(["--commit", str(target["commit"])])
    else:
        raise RuntimeError("no review target: clean main checkout and no forced mode")
    return command


def build_diff_context(root: Path, target: dict[str, Any]) -> str:
    kind = target["kind"]
    if kind == "branch":
        base = str(target["base"])
        parts = [
            f"$ git diff --stat {base}...HEAD\n{git_output(root, 'diff', '--stat', f'{base}...HEAD')}",
            f"$ git diff {base}...HEAD\n{git_output(root, 'diff', f'{base}...HEAD')}",
        ]
    elif kind == "commit":
        commit = str(target["commit"])
        parts = [f"$ git show --stat --patch {commit}\n{git_output(root, 'show', '--stat', '--patch', commit)}"]
    elif kind == "local":
        parts = [
            f"$ git status --porcelain\n{git_output(root, 'status', '--porcelain')}",
            f"$ git diff --cached --stat\n{git_output(root, 'diff', '--cached', '--stat')}",
            f"$ git diff --cached\n{git_output(root, 'diff', '--cached')}",
            f"$ git diff --stat\n{git_output(root, 'diff', '--stat')}",
            f"$ git diff\n{git_output(root, 'diff')}",
        ]
        untracked = git_output(root, "ls-files", "--others", "--exclude-standard")
        for rel in [line for line in untracked.splitlines() if line.strip()]:
            path = root / rel
            if path.is_file():
                try:
                    content = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    content = "<binary or non-utf8 file omitted>"
                parts.append(f"$ untracked file: {rel}\n{content[:20_000]}")
    else:
        parts = ["No review target."]
    diff = "\n\n".join(parts)
    if len(diff) > MAX_PROMPT_DIFF_CHARS:
        diff = diff[:MAX_PROMPT_DIFF_CHARS] + "\n\n[diff truncated by agent_review.py]"
    return diff


def build_claude_prompt(root: Path, target: dict[str, Any]) -> str:
    return f"""You are reviewing code changes for a by-harness QA closeout.
This is a SINGLE-PASS review — list ALL findings at once, sorted by priority (P0 > P1 > P2 > P3).
There will be no follow-up review round; the developer will fix everything from this one report.

Review only for concrete correctness, regression, data loss, security, concurrency, compatibility, or missing-test risks.
Do not propose broad refactors, style-only changes, or speculative edge cases.

For each finding, provide enough context so the developer can fix it without re-running the review:
[P1] path/to/file.ext:123 - Brief title
  Problem: what is concretely wrong
  Fix: the specific change to make

If there are no accepted/actionable findings, respond exactly:
agent-review clean: no accepted/actionable findings reported

Target metadata:
{json.dumps(target, ensure_ascii=False, indent=2)}

Diff/context from {root}:

{build_diff_context(root, target)}
"""


def build_claude_command(args: argparse.Namespace, target: dict[str, Any], root: Path) -> tuple[list[str], str | None]:
    command = [args.claude_bin, "--print", "--output-format", "text", "--no-session-persistence"]
    if args.full_access:
        command.append("--dangerously-skip-permissions")
    return command, build_claude_prompt(root, target)


def fetch_existing_refs(root: Path, target: dict[str, Any]) -> str:
    if target["kind"] != "branch":
        return ""
    completed = run_capture(["git", "fetch", "origin", "--quiet"], root)
    if completed.returncode != 0:
        return f"warning: git fetch origin failed; reviewing with existing refs: {completed.stderr.strip()}"
    return ""


def output_has_priority_findings(text: str) -> bool:
    return bool(PRIORITY_RE.search(text or ""))


def extract_text_findings(text: str) -> list[dict[str, Any]]:
    findings = []
    lines = (text or "").splitlines()
    for index, line in enumerate(lines):
        match = PRIORITY_RE.search(line)
        if not match:
            continue
        findings.append(
            {
                "priority": f"P{match.group(1)}",
                "title": line.strip(),
                "line_index": index + 1,
            }
        )
    return findings


def extract_json_findings(payload: Any) -> list[dict[str, Any]]:
    candidates: list[Any] = []
    if isinstance(payload, list):
        candidates.extend(payload)
    elif isinstance(payload, dict):
        for key in ("bugs", "findings", "issues", "results"):
            value = payload.get(key)
            if isinstance(value, list):
                candidates.extend(value)
    findings = []
    for item in candidates:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or item.get("summary") or item.get("description") or "Claude review finding")
        severity = str(item.get("priority") or item.get("severity") or item.get("level") or "P2")
        priority_match = PRIORITY_RE.search(severity) or re.search(r"\bP([0-3])\b", severity)
        priority = f"P{priority_match.group(1)}" if priority_match else "P2"
        path = item.get("file") or item.get("path") or item.get("filename") or ""
        line = item.get("line") or item.get("line_number") or ""
        findings.append({"priority": priority, "title": title, "file": path, "line": line, "raw": item})
    return findings


def extract_findings(output: str) -> list[dict[str, Any]]:
    text = output or ""
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        payload = None
    if payload is not None:
        json_findings = extract_json_findings(payload)
        if json_findings:
            return json_findings
        if isinstance(payload, dict) and any(key in payload for key in ("bugs", "findings", "issues", "results")):
            return []
    return extract_text_findings(text)


def run_process(command: list[str], cwd: Path, input_text: str | None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd),
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def run_parallel(
    command: list[str],
    cwd: Path,
    input_text: str | None,
    parallel_tests: str,
) -> tuple[subprocess.CompletedProcess[str], int, str, str]:
    with subprocess.Popen(
        command,
        cwd=str(cwd),
        text=True,
        stdin=subprocess.PIPE if input_text is not None else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as review_proc, subprocess.Popen(
        parallel_tests,
        cwd=str(cwd),
        shell=True,
        executable="/bin/bash",
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as tests_proc:
        review_stdout, review_stderr = review_proc.communicate(input=input_text)
        tests_stdout, tests_stderr = tests_proc.communicate()
        review_completed = subprocess.CompletedProcess(
            command,
            review_proc.returncode,
            review_stdout or "",
            review_stderr or "",
        )
        return review_completed, int(tests_proc.returncode or 0), tests_stdout or "", tests_stderr or ""


def write_raw_output(path: str, content: str) -> None:
    if not path:
        return
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def tail(text: str, limit: int = MAX_TAIL_CHARS) -> str:
    return (text or "")[-limit:]


def make_result(
    *,
    backend: str,
    gate: str,
    target: dict[str, Any],
    command: list[str],
    output_path: str,
    status: str,
    exit_code: int | None,
    summary: str,
    stdout: str = "",
    stderr: str = "",
    findings: list[dict[str, Any]] | None = None,
    tests_exit_code: int | None = None,
) -> dict[str, Any]:
    result = {
        "schema_version": 1,
        "generated_by": "agent_review.py",
        "generated_at": now_text(),
        "backend": backend,
        "gate": gate,
        "status": status,
        "exit_code": exit_code,
        "summary": summary,
        "target": target,
        "command": command,
        "output_path": output_path,
        "accepted_findings": findings or [],
        "rejected_findings": [],
        "stdout_tail": tail(stdout),
        "stderr_tail": tail(stderr),
    }
    if tests_exit_code is not None:
        result["parallel_tests_exit_code"] = tests_exit_code
    return result


def write_result(path: str, result: dict[str, Any]) -> None:
    if not path:
        return
    result_path = Path(path)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def print_selection(backend: str, target: dict[str, Any], command: list[str], args: argparse.Namespace) -> None:
    print(f"agent-review backend: {backend}")
    print(f"agent-review target: {target.get('kind')}")
    print(f"branch: {target.get('branch')}")
    if target.get("pr_url"):
        print(f"pr: {target.get('pr_url')}")
    print("review:", shell_quote(command))
    if args.parallel_tests:
        print(f"tests: {args.parallel_tests}")
    if target.get("kind") == "branch":
        print("fetch: git fetch origin --quiet")
    if args.output:
        print(f"output: {args.output}")
    if args.result_json:
        print(f"result_json: {args.result_json}")


def choose_backend(args: argparse.Namespace) -> str:
    if args.backend != "auto":
        return args.backend
    if command_available(args.codex_bin):
        return "codex"
    if command_available(args.claude_bin):
        return "claude"
    return "off"


def run_review(args: argparse.Namespace, root: Path) -> dict[str, Any]:
    backend = choose_backend(args)
    target = detect_target(root, args.mode, args.base, args.commit)

    if backend == "off":
        status = STATUS_FAIL if args.gate == GATE_REQUIRED else STATUS_SKIP
        exit_code = 1 if status == STATUS_FAIL else 0
        summary = (
            "no agent review backend available for required gate"
            if status == STATUS_FAIL
            else "agent review disabled"
        )
        result = make_result(
            backend=backend,
            gate=args.gate,
            target=target,
            command=[],
            output_path=args.output,
            status=status,
            exit_code=exit_code,
            summary=summary,
        )
        return result

    binary = args.codex_bin if backend == "codex" else args.claude_bin
    if not command_available(binary):
        status = STATUS_FAIL if args.gate == GATE_REQUIRED else STATUS_SKIP
        exit_code = 1 if status == STATUS_FAIL else 0
        return make_result(
            backend=backend,
            gate=args.gate,
            target=target,
            command=[binary],
            output_path=args.output,
            status=status,
            exit_code=exit_code,
            summary=f"{backend} binary not found: {binary}",
        )

    try:
        if backend == "codex":
            command = build_codex_command(args, target)
            input_text = None
        else:
            if target["kind"] == "none":
                raise RuntimeError("no review target: clean main checkout and no forced mode")
            command, input_text = build_claude_command(args, target, root)
    except RuntimeError as exc:
        return make_result(
            backend=backend,
            gate=args.gate,
            target=target,
            command=[binary],
            output_path=args.output,
            status=STATUS_FAIL,
            exit_code=1,
            summary=str(exc),
            stderr=str(exc),
        )

    print_selection(backend, target, command, args)
    if args.dry_run:
        return make_result(
            backend=backend,
            gate=args.gate,
            target=target,
            command=command,
            output_path=args.output,
            status=STATUS_SKIP,
            exit_code=0,
            summary="dry-run: review not executed",
        )

    fetch_warning = fetch_existing_refs(root, target)
    if fetch_warning:
        print(fetch_warning, file=sys.stderr)

    started_at = datetime.now()
    if args.parallel_tests:
        completed, tests_status, tests_stdout, tests_stderr = run_parallel(command, root, input_text, args.parallel_tests)
    else:
        completed = run_process(command, root, input_text)
        tests_status = None
        tests_stdout = ""
        tests_stderr = ""
    elapsed = int((datetime.now() - started_at).total_seconds())

    review_text = completed.stdout or ""
    raw_output = review_text + (completed.stderr or "")
    write_raw_output(args.output, raw_output)
    findings = extract_findings(review_text)

    status = STATUS_PASS
    reasons = []
    if completed.returncode != 0:
        status = STATUS_FAIL
        reasons.append(f"review exit {completed.returncode}")
    if tests_status not in (None, 0):
        status = STATUS_FAIL
        reasons.append(f"parallel tests exit {tests_status}")
    if not raw_output.strip():
        status = STATUS_FAIL
        reasons.append("review produced no output")
    if findings or output_has_priority_findings(review_text):
        if not findings:
            findings = extract_text_findings(review_text)
        status = STATUS_FAIL
        reasons.append("accepted/actionable findings reported")

    if status == STATUS_PASS:
        summary = "no accepted/actionable findings reported"
        print(f"agent-review complete after {elapsed}s")
        print("agent-review clean: no accepted/actionable findings reported")
    else:
        summary = "; ".join(reasons) if reasons else "review failed"
        print(f"agent-review complete after {elapsed}s")
        print(f"agent-review findings: {summary}")
    if tests_status is not None:
        print(f"agent-review exit: {completed.returncode}")
        print(f"tests exit: {tests_status}")

    stdout = (completed.stdout or "") + ("\n" + tests_stdout if tests_stdout else "")
    stderr = (completed.stderr or "") + ("\n" + tests_stderr if tests_stderr else "")
    return make_result(
        backend=backend,
        gate=args.gate,
        target=target,
        command=command,
        output_path=args.output,
        status=status,
        exit_code=0 if status == STATUS_PASS else 1,
        summary=summary,
        stdout=stdout,
        stderr=stderr,
        findings=findings,
        tests_exit_code=tests_status,
    )


def main() -> None:
    args = parse_args()
    try:
        root = repo_root(Path(args.target_dir))
        result = run_review(args, root)
    except Exception as exc:  # noqa: BLE001
        result = make_result(
            backend=args.backend,
            gate=args.gate,
            target={"kind": "unknown"},
            command=[],
            output_path=args.output,
            status=STATUS_FAIL,
            exit_code=1,
            summary=str(exc),
            stderr=str(exc),
        )
        print(f"agent-review error: {exc}", file=sys.stderr)
    write_result(args.result_json, result)
    exit_code = 0 if result.get("status") in {STATUS_PASS, STATUS_SKIP} else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
