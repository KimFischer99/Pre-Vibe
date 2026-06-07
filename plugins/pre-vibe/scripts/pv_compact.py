"""Compact structured payloads for MCP responses."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from pv_models import CodexEnvironment, EvidenceRef, IntakeDecision, ProjectContext
from pv_questions import native_question_payload, visible_status_for_state


def redact_path_for_context(value: str | None, project_root: str | None = None) -> str | None:
    if not value:
        return value
    path = value
    if project_root and path == project_root:
        return "."
    home = str(Path.home())
    if path.startswith(home):
        return "~" + path[len(home) :]
    return path


def compact_project_context(context: ProjectContext | None) -> dict[str, Any] | None:
    if not context:
        return None
    payload = asdict(context)
    root = context.root
    payload["root"] = "."
    payload["global_agents_path"] = (
        "global AGENTS.md" if context.global_agents_path else None
    )
    payload["project_agents_path"] = (
        "project AGENTS.md" if context.project_agents_path else None
    )
    payload["do_not_touch"] = [
        redact_path_for_context(item, root) or item for item in context.do_not_touch
    ]
    return payload


def compact_codex_environment(environment: CodexEnvironment | None) -> dict[str, Any] | None:
    if not environment:
        return None
    return {
        "global_agents_present": bool(environment.global_agents_path),
        "installed_plugin_cache_count": len(environment.installed_plugin_cache),
        "installed_plugins": environment.installed_plugins,
        "marketplace_plugins": environment.marketplace_plugins,
        "installed_standalone_skills": environment.installed_skills,
        "local_plugins_present": bool(environment.local_plugins_path),
        "marketplace_present": bool(environment.marketplace_path),
        "marketplace_has_pre_vibe": environment.marketplace_has_pre_vibe,
        "notes": environment.notes,
    }


def compact_evidence_ref(ref: EvidenceRef, project_root: str | None = None) -> dict[str, str]:
    return {
        "id": ref.id,
        "source": redact_path_for_context(ref.source, project_root) or ref.source,
        "summary": ref.summary,
    }


def compact_decision(decision: IntakeDecision) -> dict[str, Any]:
    project_root = decision.project_context.root if decision.project_context else None
    evidence_buffer = []
    for item in decision.evidence_buffer:
        payload = asdict(item)
        payload["source"] = redact_path_for_context(item.source, project_root) or item.source
        evidence_buffer.append(payload)
    workflow_contract = {
        "required_order": [
            "prepare_project_start",
            "open_question_dialog when question_request is present",
            "write_project_starting_documents after required answers and evidence are available",
            "request user approval for FIRST_PROMPT.md handoff",
            "after approval, read and inject FIRST_PROMPT.md as the execution contract",
        ],
        "document_generation_is_not_completion": True,
        "completion_condition": "Pre-Vibe is complete only after the FIRST_PROMPT.md handoff is approved and used, or the user explicitly cancels.",
    }
    return {
        "state": decision.state,
        "scenario": decision.scenario,
        "intensity": decision.intensity,
        "language": decision.language,
        "risk": decision.risk,
        "uncertainty": decision.uncertainty,
        "questions": [asdict(question) for question in decision.blocking_questions],
        "context_actions": [asdict(action) for action in decision.context_actions],
        "assumptions": decision.assumptions,
        "document_rules": decision.artifact_rules,
        "evidence_refs": [
            compact_evidence_ref(ref, project_root) for ref in decision.evidence_refs
        ],
        "project_context": compact_project_context(decision.project_context),
        "codex_environment": compact_codex_environment(decision.codex_environment),
        "component_suggestions": decision.component_suggestions,
        "missing_component_suggestions": decision.missing_component_suggestions,
        "evidence_buffer": evidence_buffer,
        "project_language": [asdict(item) for item in decision.project_language],
        "document_output_plan": decision.document_output_plan,
        "agent_guidance_mode": decision.agent_guidance_mode,
        "recovery_action": decision.recovery_action,
        "question_request": native_question_payload(decision),
        "workflow_contract": workflow_contract,
        "user_visible_status": visible_status_for_state(decision.state, decision.language),
    }
