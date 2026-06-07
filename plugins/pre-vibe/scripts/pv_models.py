"""Shared data models and workflow constants for Pre-Vibe."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


INTAKE_STARTED = "INTAKE_STARTED"
NEEDS_USER_INPUT = "NEEDS_USER_INPUT"
NEEDS_CONTEXT = "NEEDS_CONTEXT"
READY_TO_COMPILE = "READY_TO_COMPILE"
AWAITING_APPROVAL = "AWAITING_APPROVAL"
READY_TO_INJECT = "READY_TO_INJECT"
DONE = "DONE"


@dataclass(frozen=True)
class IntensityProfile:
    name: str
    description: str
    max_questions: int
    max_fetches: int
    max_scanned_files: int
    allow_default_scan: bool
    allow_fetch: bool
    staged: bool = False


INTENSITY_PROFILES = {
    "mini": IntensityProfile(
        "mini",
        "Light preparation for ordinary work, small research, or tiny changes.",
        max_questions=3,
        max_fetches=0,
        max_scanned_files=8,
        allow_default_scan=True,
        allow_fetch=False,
    ),
    "default": IntensityProfile(
        "default",
        "Balanced preparation for normal research and coding tasks.",
        max_questions=5,
        max_fetches=2,
        max_scanned_files=10,
        allow_default_scan=True,
        allow_fetch=True,
    ),
    "architect": IntensityProfile(
        "architect",
        "Full staged preparation for new projects, refactors, and complex research.",
        max_questions=10,
        max_fetches=6,
        max_scanned_files=60,
        allow_default_scan=True,
        allow_fetch=True,
        staged=True,
    ),
}


@dataclass
class BlockingQuestion:
    id: str
    header: str
    question: str
    reason: str
    options: list[str] = field(default_factory=list)
    recommended_answer: str | None = None
    requires_native_ui: bool = True


@dataclass
class ContextAction:
    id: str
    kind: str
    description: str
    required: bool = True


@dataclass
class EvidenceRef:
    id: str
    source: str
    summary: str
    confidence: str = "medium"
    used_in: list[str] = field(default_factory=list)


@dataclass
class EvidenceItem:
    id: str
    source: str
    summary: str
    confidence: str = "medium"
    used_in: list[str] = field(default_factory=list)


@dataclass
class ProjectLanguageItem:
    preferred_term: str
    definition: str
    avoid_terms: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class ExistingContext:
    existing_files: list[str]
    missing_files: list[str]
    has_pre_vibe_docs: bool
    has_partial_pre_vibe_docs: bool
    recommended_action: str
    recovery_options: list[str]


@dataclass
class AgentInstructionRef:
    path: str
    scope: str
    priority: str
    kind: str


@dataclass
class ProjectContext:
    root: str
    scan_performed: bool
    scan_scope: str
    scanned_files: list[str]
    skipped_secret_like: list[str]
    key_dirs: list[str]
    signals: dict[str, str]
    relevant_pointers: list[str]
    do_not_touch: list[str]
    global_agents_path: str | None
    global_agents_summary: list[str]
    project_agents_path: str | None
    project_agents_summary: list[str]
    agent_instruction_map: list[AgentInstructionRef] = field(default_factory=list)
    existing_context: ExistingContext | None = None
    git_state: str = "unknown"


@dataclass
class CodexEnvironment:
    codex_home: str | None
    global_agents_path: str | None
    installed_plugin_cache: list[str]
    installed_plugins: list[str]
    marketplace_plugins: list[str]
    installed_skills: list[str]
    local_plugins_path: str | None
    marketplace_path: str | None
    marketplace_has_pre_vibe: bool
    notes: list[str] = field(default_factory=list)


@dataclass
class IntakeDecision:
    raw_input: str
    scenario: str
    intensity: str
    language: str
    risk: str
    uncertainty: str
    state: str
    blocking_questions: list[BlockingQuestion]
    context_actions: list[ContextAction]
    assumptions: list[str]
    artifact_rules: list[str]
    evidence_refs: list[EvidenceRef]
    project_context: ProjectContext | None = None
    codex_environment: CodexEnvironment | None = None
    component_suggestions: list[str] = field(default_factory=list)
    missing_component_suggestions: list[str] = field(default_factory=list)
    evidence_buffer: list[EvidenceItem] = field(default_factory=list)
    project_language: list[ProjectLanguageItem] = field(default_factory=list)
    document_output_plan: dict[str, str] = field(default_factory=dict)
    agent_guidance_mode: str = "proposal"
    recovery_action: str | None = None


@dataclass
class PreVibeSettings:
    default_intensity: str = "auto"
    allow_auto_upgrade: bool = True
    architect_project_index: bool = True
    inspect_codex_environment: bool = True
    session_intensity: str | None = None


def to_jsonable(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")
