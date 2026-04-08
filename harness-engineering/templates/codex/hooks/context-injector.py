#!/usr/bin/env python3
"""
Codex UserPromptSubmit hook: inject concise project context.
"""

import json
import subprocess
from pathlib import Path


def emit(payload):
    print(json.dumps(payload, ensure_ascii=False))


def get_git_info():
    info = {}
    try:
        info["branch"] = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL,
            timeout=5,
        ).decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        info["branch"] = "unknown (not a git repo)"

    try:
        info["recent_commits"] = subprocess.check_output(
            ["git", "log", "--oneline", "-5"],
            stderr=subprocess.DEVNULL,
            timeout=5,
        ).decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        info["recent_commits"] = ""

    return info


def get_project_state():
    state = {}
    cwd = Path.cwd()

    specs_dir = cwd / "docs" / "specs"
    if specs_dir.exists():
        specs = list(specs_dir.glob("*.md"))
        if specs:
            state["active_specs"] = [
                p.name for p in sorted(specs, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
            ]

    contracts_dir = cwd / "docs" / "contracts"
    if contracts_dir.exists():
        contracts = [p for p in contracts_dir.glob("*.md") if p.name != "TEMPLATE.md"]
        if contracts:
            state["active_contracts"] = [
                p.name for p in sorted(contracts, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
            ]

    plans_dir = cwd / "docs" / "plans"
    if plans_dir.exists():
        plans = list(plans_dir.glob("*.md"))
        if plans:
            state["active_plans"] = [
                p.name for p in sorted(plans, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
            ]

    return state


def main():
    parts = []

    git_info = get_git_info()
    if git_info.get("branch"):
        parts.append(f"Git branch: {git_info['branch']}")
    if git_info.get("recent_commits"):
        parts.append(f"Recent commits:\n{git_info['recent_commits']}")

    state = get_project_state()
    if state.get("active_specs"):
        parts.append(f"Active specs: {', '.join(state['active_specs'])}")
    if state.get("active_contracts"):
        parts.append(f"Active contracts: {', '.join(state['active_contracts'])}")
    if state.get("active_plans"):
        parts.append(f"Active plans: {', '.join(state['active_plans'])}")

    if not parts:
        emit({})
        return

    message = (
        "Project context:\n"
        + "\n".join(parts)
        + "\n\nUse this context to understand project state. Read only relevant specs/contracts/plans."
    )

    emit(
        {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": message,
            }
        }
    )


if __name__ == "__main__":
    main()
