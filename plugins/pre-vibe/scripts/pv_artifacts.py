"""Artifact validation and writing for Claude Code-authored starting documents."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from pv_models import AWAITING_APPROVAL


ARTIFACT_FILENAMES = {
    "spec": "PRE_VIBE_SPEC.md",
    "agents": "CLAUDE.md",
    "project_agents": "PROJECT_CLAUDE.md",
    "prompt": "FIRST_PROMPT.md",
    "project_index": "PROJECT_INDEX.md",
}

HANDOFF_REQUIRED_NEXT_ACTIONS = [
    "Ask the user to review and approve FIRST_PROMPT.md. Explain that after approval, the next steps are: /clear → inject FIRST_PROMPT.md as execution contract.",
    "After approval, ask the user to run /clear to reset context, then read and inject FIRST_PROMPT.md.",
    "Treat document generation as preparation only; do not end the Pre-Vibe run after writing files.",
]


def estimate_tokens(text: str) -> int:
    cjk_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    other_chars = max(len(text) - cjk_chars, 0)
    return max(1, int(cjk_chars / 1.7 + other_chars / 4))


def redact_secret_like(text: str) -> str:
    patterns = (
        r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*[^\s]+",
        r"(?i)(bearer)\s+[a-z0-9._~+/=-]{20,}",
        r"(?i)(jwt|cookie|session)\s*[:=]\s*[^\s]+",
        r"-----BEGIN [A-Z ]+PRIVATE KEY-----.*?-----END [A-Z ]+PRIVATE KEY-----",
    )
    redacted = text
    for pattern in patterns:
        redacted = re.sub(pattern, "[REDACTED]", redacted, flags=re.DOTALL)
    return redacted


def validate_artifact_contents(contents: dict[str, str], allow_project_index: bool = True) -> None:
    if "spec" not in contents or "prompt" not in contents:
        raise ValueError("contents must include spec and prompt")
    if "agents" not in contents and "project_agents" not in contents:
        raise ValueError("contents must include agents or project_agents")
    if "project_index" in contents and not allow_project_index:
        raise ValueError("project_index is only allowed for architect effort")
    forbidden_by_key = {
        "spec": ("CLAUDE.md", "PROJECT_CLAUDE.md", "PROJECT_INDEX.md"),
        "agents": ("PRE_VIBE_SPEC.md", "PROJECT_INDEX.md"),
        "project_agents": ("PRE_VIBE_SPEC.md", "PROJECT_INDEX.md"),
        "project_index": ("PRE_VIBE_SPEC.md", "CLAUDE.md", "PROJECT_CLAUDE.md"),
    }
    for key, filenames in forbidden_by_key.items():
        text = contents.get(key, "")
        if not text:
            continue
        for forbidden in filenames:
            if re.search(rf"(?i)(^|[/\\]){re.escape(forbidden)}\b|{re.escape(forbidden)}\b", text):
                raise ValueError(f"{ARTIFACT_FILENAMES[key]} must not reference {forbidden}")
    if "agents" in contents and "project_agents" in contents:
        raise ValueError("write either agents or project_agents, not both")
    if "project_index" in contents and "prompt" not in contents:
        raise ValueError("PROJECT_INDEX.md may only be written with FIRST_PROMPT.md")


def ensure_output_dir_inside_project(output_dir: Path, project_root: Path | None = None) -> Path:
    root = (project_root or Path.cwd()).expanduser().resolve()
    output = output_dir.expanduser()
    resolved_output = output.resolve() if output.is_absolute() else (root / output).resolve()
    if resolved_output != root and root not in resolved_output.parents:
        raise ValueError("output_dir must be inside the active project root")
    return resolved_output


def handoff_contract(written: dict[str, str]) -> dict[str, Any]:
    if "prompt" not in written:
        raise ValueError("handoff requires FIRST_PROMPT.md")
    return {
        "workflow_state": AWAITING_APPROVAL,
        "handoff_file": written["prompt"],
        "approval_request": "Please review FIRST_PROMPT.md. Approve if it meets your expectations. After approval, the next step will be /clear (reset context) then inject FIRST_PROMPT.md as the execution contract for Claude Code.",
        "required_next_actions": HANDOFF_REQUIRED_NEXT_ACTIONS,
        "document_generation_is_complete": True,
        "pre_vibe_run_is_complete": False,
    }


def write_artifacts(
    output_dir: Path,
    contents: dict[str, str],
    status: dict[str, Any] | None = None,
    project_root: Path | None = None,
    allow_project_index: bool = True,
) -> dict[str, Any]:
    if status is not None:
        raise ValueError("status is internal context and must not be written to disk")
    output_dir = ensure_output_dir_inside_project(output_dir, project_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}
    validate_artifact_contents(contents, allow_project_index=allow_project_index)
    for key, text in contents.items():
        if key not in ARTIFACT_FILENAMES:
            raise ValueError(f"unsupported artifact key: {key}")
        path = output_dir / ARTIFACT_FILENAMES[key]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(redact_secret_like(text).rstrip() + "\n", encoding="utf-8")
        written[key] = str(path.relative_to(output_dir))
    return {
        "written": written,
        "handoff": handoff_contract(written),
    }
