#!/usr/bin/env python3
"""pre-vibe workflow utilities.

The module is intentionally not a Markdown template generator. It provides
deterministic helpers that Codex can call while running the pre-vibe workflow:
task routing, intensity selection, safe project scanning, environment inspection,
state gating, question UI payloads, and document writes for LLM-authored content.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable


INTAKE_STARTED = "INTAKE_STARTED"
NEEDS_USER_INPUT = "NEEDS_USER_INPUT"
NEEDS_CONTEXT = "NEEDS_CONTEXT"
READY_TO_COMPILE = "READY_TO_COMPILE"
AWAITING_APPROVAL = "AWAITING_APPROVAL"
READY_TO_INJECT = "READY_TO_INJECT"
DONE = "DONE"

ARTIFACT_FILENAMES = {
    "spec": "PRE_VIBE_SPEC.md",
    "agents": "PROJECT_AGENTS.md",
    "prompt": "FIRST_PROMPT.md",
    "status": ".pre-vibe/status.json",
    "context_index": ".pre-vibe/context-index.md",
    "decisions": ".pre-vibe/decisions.md",
}

SECRET_PATTERNS = (
    ".env",
    ".pem",
    ".key",
    ".p12",
    ".pfx",
    "id_rsa",
    "id_ed25519",
    "token",
    "secret",
    "credential",
    "credentials",
    "database.sqlite",
    ".sqlite",
    ".db",
    ".dump",
    ".log",
)

ALLOWLIST_FILENAMES = {
    "README.md",
    "README.zh.md",
    "README.en.md",
    "AGENTS.md",
    "PROJECT_AGENTS.md",
    "CLAUDE.md",
    "package.json",
    "pnpm-lock.yaml",
    "package-lock.json",
    "yarn.lock",
    "pyproject.toml",
    "requirements.txt",
    "Cargo.toml",
    "go.mod",
    "Makefile",
}

ALLOWLIST_SUFFIXES = {
    ".md",
    ".toml",
    ".json",
}

SKIP_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    ".next",
    ".cache",
}

CODING_TERMS = (
    "code",
    "repo",
    "bug",
    "fix",
    "api",
    "frontend",
    "backend",
    "test",
    "deploy",
    "plugin",
    "mvp",
    "reverse",
    "reverse-engineer",
    "decompile",
    "disassemble",
    "binary analysis",
    "代码",
    "仓库",
    "项目",
    "修复",
    "前端",
    "后端",
    "测试",
    "部署",
    "插件",
    "逆向",
    "反编译",
    "反汇编",
    "拆包",
)

RESEARCH_TERMS = (
    "research",
    "compare",
    "sources",
    "paper",
    "market",
    "docs",
    "investigate",
    "调研",
    "研究",
    "比较",
    "竞品",
    "资料",
    "论文",
    "文档",
)

REVERSE_TERMS = (
    "reverse",
    "reverse-engineer",
    "decompile",
    "disassemble",
    "binary analysis",
    "逆向",
    "反编译",
    "反汇编",
    "拆包",
)

AMBIGUOUS_TARGET_TERMS = (
    "desktop",
    "on my desktop",
    "this thing",
    "this app",
    "this file",
    "桌面",
    "这个东西",
    "这个应用",
    "这个app",
    "这个文件",
)

ARCHITECT_TERMS = (
    "architecture",
    "architect",
    "system design",
    "refactor",
    "new project",
    "rewrite",
    "workflow",
    "架构",
    "系统设计",
    "重构",
    "新项目",
    "完整",
)

TARGET_PATH_RE = re.compile(
    r"(`[^`]+`|[/~][^\s]+|[A-Za-z]:\\[^\s]+|\b[\w .@()-]+\."
    r"(app|exe|dmg|pkg|zip|asar|apk|ipa|bin|dll|dylib|so|jar|class)\b)",
    re.IGNORECASE,
)


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


def has_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def choose_language(task: str, requested: str = "auto") -> str:
    if requested != "auto":
        return requested
    return "zh" if has_cjk(task) else "en"


def classify_scenario(task: str, requested: str = "auto") -> str:
    if requested != "auto":
        return requested
    lower = task.lower()
    coding_hit = any(token in lower for token in CODING_TERMS)
    research_hit = any(token in lower for token in RESEARCH_TERMS)
    if coding_hit and research_hit:
        return "mixed"
    if coding_hit:
        return "coding"
    if research_hit:
        return "research"
    return "general"


def is_reverse_engineering_task(task: str) -> bool:
    lower = task.lower()
    return any(term in lower for term in REVERSE_TERMS)


def extract_target_paths(task: str) -> list[str]:
    paths: list[str] = []
    for match in TARGET_PATH_RE.finditer(task):
        value = match.group(0).strip("`")
        paths.append(value)
    return paths


def has_target_path(task: str) -> bool:
    return bool(extract_target_paths(task))


def has_ambiguous_external_target(task: str) -> bool:
    lower = task.lower()
    return (
        is_reverse_engineering_task(task)
        and any(term in lower for term in AMBIGUOUS_TARGET_TERMS)
        and not has_target_path(task)
    )


def looks_like_new_product_task(task: str) -> bool:
    lower = task.lower()
    return any(
        term in lower
        for term in (
            "build",
            "create",
            "make",
            "mvp",
            "app",
            "website",
            "site",
            "做一个",
            "搭建",
            "开发",
            "网站",
            "应用",
            "小程序",
        )
    )


def choose_intensity(task: str, scenario: str, requested: str = "auto") -> str:
    if requested != "auto":
        if requested not in INTENSITY_PROFILES:
            raise ValueError(f"unknown intensity: {requested}")
        return requested
    lower = task.lower()
    if scenario == "general":
        return "mini"
    if any(term in lower for term in ARCHITECT_TERMS):
        return "architect"
    if scenario in {"coding", "mixed"} and any(term in lower for term in ("mvp", "新项目", "完整")):
        return "architect"
    return "default"


def assess_risk(task: str, scenario: str) -> str:
    lower = task.lower()
    high_terms = (
        "deploy",
        "production",
        "migration",
        "delete",
        "payment",
        "auth",
        "逆向",
        "反编译",
        "部署",
        "生产",
        "迁移",
        "删除",
        "支付",
        "权限",
    )
    if is_reverse_engineering_task(task) or any(term in lower for term in high_terms):
        return "high"
    if scenario in {"coding", "mixed", "research"}:
        return "medium"
    return "low"


def assess_uncertainty(task: str) -> str:
    lower = task.lower()
    vague_terms = (
        "something",
        "stuff",
        "this thing",
        "whatever",
        "make it better",
        "优化一下",
        "搞一下",
        "这个东西",
        "随便",
        "不太清楚",
    )
    if has_ambiguous_external_target(task) or any(term in lower for term in vague_terms):
        return "high"
    if len(task.strip()) < 40:
        return "medium"
    return "low"


def is_secret_like(path: Path) -> bool:
    lowered = path.name.lower()
    full = str(path).lower()
    return any(pattern in lowered or pattern in full for pattern in SECRET_PATTERNS)


def summarize_agents(path: Path | None, max_lines: int = 18) -> list[str]:
    if not path or not path.exists() or is_secret_like(path):
        return []
    lines: list[str] = []
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line:
            continue
        line = line.lstrip("#").strip()
        if not line:
            continue
        line = re.sub(r"\s+", " ", line)
        lines.append(line[:180])
        if len(lines) >= max_lines:
            break
    return lines


def find_global_agents() -> Path | None:
    candidates: list[Path] = []
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        candidates.append(Path(codex_home) / "AGENTS.md")
    candidates.append(Path.home() / ".codex" / "AGENTS.md")
    for path in candidates:
        if path.exists():
            return path
    return None


def safe_walk(
    root: Path,
    max_files: int,
    scenario: str,
    skip_reason: str = "scan skipped by intensity profile",
) -> ProjectContext:
    scanned: list[str] = []
    skipped: list[str] = []
    dirs: list[str] = []
    signals: dict[str, str] = {}
    pointers: list[str] = []
    do_not_touch: list[str] = []
    global_agents = find_global_agents()
    project_agents = root / "AGENTS.md"

    if not root.exists():
        return ProjectContext(
            str(root),
            False,
            "project root missing",
            [],
            [],
            [],
            {"warning": "project root not found"},
            [],
            [],
            str(global_agents) if global_agents else None,
            summarize_agents(global_agents),
            None,
            [],
        )

    if max_files <= 0:
        return ProjectContext(
            str(root),
            False,
            skip_reason,
            [],
            [],
            [],
            {"scan": skip_reason},
            [],
            ["secret files", "generated files", "vendor/dependency directories"],
            str(global_agents) if global_agents else None,
            summarize_agents(global_agents),
            str(project_agents) if project_agents.exists() else None,
            summarize_agents(project_agents if project_agents.exists() else None),
        )

    for entry in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if entry.name in SKIP_DIRS:
            do_not_touch.append(entry.name + "/")
            continue
        if is_secret_like(entry):
            skipped.append(entry.name)
            do_not_touch.append(entry.name)
            continue
        if entry.is_dir():
            dirs.append(entry.name)
            if entry.name in {"src", "app", "lib", "tests", "test", "docs", "components", ".claude"}:
                signals[f"dir:{entry.name}"] = "present"
                pointers.append(f"{entry.name}/ - inspect only if the task points there")
            continue
        if entry.name in ALLOWLIST_FILENAMES or entry.suffix in ALLOWLIST_SUFFIXES:
            scanned.append(entry.name)
            if entry.name == "package.json":
                signals["stack"] = "JavaScript/TypeScript"
                pointers.append("package.json - scripts and dependencies")
            elif entry.name == "pyproject.toml":
                signals["stack"] = "Python"
                pointers.append("pyproject.toml - Python package metadata")
            elif entry.name == "AGENTS.md":
                signals["agents_guidance"] = "project AGENTS.md present"
                pointers.append("AGENTS.md - project agent guidance")
            elif entry.name == "CLAUDE.md":
                signals["claude_memory"] = "CLAUDE.md present"
                pointers.append("CLAUDE.md - Claude Code memory")
            elif entry.name.lower().startswith("readme"):
                pointers.append(f"{entry.name} - project overview")
            elif "prd" in entry.name.lower() or "spec" in entry.name.lower():
                pointers.append(f"{entry.name} - product or task requirements")
        if len(scanned) >= max_files:
            signals["scan_limit"] = f"stopped after {max_files} files"
            break

    return ProjectContext(
        str(root),
        True,
        f"allowlist root scan up to {max_files} files",
        scanned,
        skipped,
        dirs[:40],
        signals,
        pointers[:16],
        do_not_touch[:16],
        str(global_agents) if global_agents else None,
        summarize_agents(global_agents),
        str(project_agents) if project_agents.exists() else None,
        summarize_agents(project_agents if project_agents.exists() else None),
    )


def collect_skill_names(roots: Iterable[Path], limit: int = 80) -> list[str]:
    skills: list[str] = []
    seen: set[str] = set()
    for root in roots:
        if not root.exists():
            continue
        for skill_md in sorted(root.glob("*/SKILL.md")):
            if len(skills) >= limit:
                return skills
            name = skill_md.parent.name
            try:
                text = skill_md.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                text = ""
            match = re.search(r"(?m)^name:\s*['\"]?([^'\"\n]+)", text[:1000])
            if match:
                name = match.group(1).strip()
            if name and name not in seen:
                seen.add(name)
                skills.append(name)
    return skills


def clean_header(value: str, fallback: str = "Question") -> str:
    value = re.sub(r"\s+", " ", value).strip() or fallback
    return value[:12]


def option_objects(question: BlockingQuestion) -> list[dict[str, str]]:
    options = list(question.options[:3])
    if len(options) < 2:
        options.extend(["Use best default", "Ask later"][len(options) :])
    return [
        {
            "label": option[:36],
            "description": question.reason[:140] or "Choose this option to continue.",
        }
        for option in options[:3]
    ]


def native_question_payload(decision: IntakeDecision) -> dict[str, Any] | None:
    if not decision.blocking_questions:
        return None
    questions = [
        {
            "header": clean_header(question.header),
            "id": question.id,
            "question": question.question,
            "options": option_objects(question),
        }
        for question in decision.blocking_questions
    ]
    return {
        "preferred_surface": "codex_native_question_ui",
        "codex_request_user_input": {
            "questions": questions,
        },
        "mcp_elicitation": {
            "method": "elicitation/create",
            "message": "Please answer the key questions so Codex can build the project starting context.",
            "requestedSchema": {
                "type": "object",
                "properties": {
                    question.id: {
                        "type": "string",
                        "title": clean_header(question.header),
                        "description": question.question,
                    }
                    for question in decision.blocking_questions
                },
                "required": [question.id for question in decision.blocking_questions],
            },
        },
        "fallback_policy": "If this Codex surface cannot open native question UI or MCP elicitation, pause and report that native question UI is unavailable instead of printing backend fields.",
    }


def visible_status_for_state(state: str, language: str = "auto") -> str:
    zh = language in {"zh", "bilingual", "auto"}
    if state == NEEDS_CONTEXT:
        return "正在读取项目结构和 Codex 环境。" if zh else "Reading the project and Codex environment."
    if state == NEEDS_USER_INPUT:
        return "正在打开关键问题确认窗口。" if zh else "Opening the key-question dialog."
    if state == READY_TO_COMPILE:
        return "正在构建项目初始文档。" if zh else "Building the project starting documents."
    if state == AWAITING_APPROVAL:
        return "项目初始文档已准备好，正在等待确认。" if zh else "The project starting documents are ready for approval."
    if state == READY_TO_INJECT:
        return "正在准备清理上下文并注入首轮提示。" if zh else "Preparing to clear context and inject the first prompt."
    if state == DONE:
        return "项目启动上下文已完成。" if zh else "The project starting context is complete."
    return "正在准备项目启动上下文。" if zh else "Preparing the project starting context."


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
        "question_request": native_question_payload(decision),
        "user_visible_status": visible_status_for_state(decision.state, decision.language),
    }


def prepare_project_start(
    task: str,
    project: str | Path = ".",
    *,
    scenario: str = "auto",
    intensity: str = "auto",
    language: str = "auto",
    evidence_refs: Iterable[EvidenceRef] | None = None,
    scan: bool = True,
) -> dict[str, Any]:
    decision = route_intake(
        task,
        project,
        scenario=scenario,
        intensity=intensity,
        language=language,
        evidence_refs=evidence_refs,
        scan=scan,
    )
    return compact_decision(decision)


def collect_configured_plugins(config_path: Path) -> list[str]:
    if not config_path.exists():
        return []
    try:
        lines = config_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    current: str | None = None
    enabled: dict[str, bool] = {}
    header_re = re.compile(r'^\[plugins\."([^"]+)"\]\s*$')
    for raw in lines:
        line = raw.strip()
        header = header_re.match(line)
        if header:
            current = header.group(1)
            enabled.setdefault(current, True)
            continue
        if line.startswith("["):
            current = None
            continue
        if current and re.match(r"^enabled\s*=\s*false\b", line, re.IGNORECASE):
            enabled[current] = False
    configured: list[str] = []
    for name, is_enabled in enabled.items():
        if is_enabled:
            configured.append(name)
    return sorted(configured)


def collect_plugin_names(cache_root: Path, marketplace_path: Path) -> tuple[list[str], list[str], list[str]]:
    cache_entries: list[str] = []
    cached: set[str] = set()
    marketplace_plugins: set[str] = set()
    if cache_root.exists():
        for path in sorted(cache_root.glob("*/*/*")):
            if path.is_dir():
                cache_entries.append(str(path))
                parts = path.relative_to(cache_root).parts
                if len(parts) >= 2:
                    cached.add(f"{parts[1]}@{parts[0]}")
    if marketplace_path.exists():
        try:
            payload = json.loads(marketplace_path.read_text(encoding="utf-8"))
            for item in payload.get("plugins", []):
                if isinstance(item, dict) and isinstance(item.get("name"), str):
                    marketplace_plugins.add(f"{item['name']}@marketplace")
        except json.JSONDecodeError:
            pass
    return cache_entries, sorted(cached), sorted(marketplace_plugins)


def inspect_codex_environment() -> CodexEnvironment:
    codex_home = os.environ.get("CODEX_HOME")
    default_codex_home = Path.home() / ".codex"
    global_agents = find_global_agents()
    cache_root = default_codex_home / "plugins" / "cache"
    marketplace = Path.home() / ".agents" / "plugins" / "marketplace.json"
    plugin_cache, cached_plugins, marketplace_plugins = collect_plugin_names(cache_root, marketplace)
    configured_plugins = collect_configured_plugins(default_codex_home / "config.toml")
    installed_plugins = configured_plugins or cached_plugins
    marketplace_has_pre_vibe = False
    if marketplace.exists():
        try:
            payload = json.loads(marketplace.read_text(encoding="utf-8"))
            marketplace_has_pre_vibe = any(
                isinstance(item, dict) and item.get("name") == "pre-vibe"
                for item in payload.get("plugins", [])
            )
        except json.JSONDecodeError:
            marketplace_has_pre_vibe = False
    skill_roots = [
        default_codex_home / "skills",
        Path.home() / ".agents" / "skills",
    ]
    notes = []
    if not global_agents:
        notes.append("No global AGENTS.md was found.")
    if not marketplace_has_pre_vibe:
        notes.append("pre-vibe is not listed in the default personal marketplace.")
    return CodexEnvironment(
        codex_home=codex_home or str(default_codex_home),
        global_agents_path=str(global_agents) if global_agents else None,
        installed_plugin_cache=plugin_cache,
        installed_plugins=installed_plugins,
        marketplace_plugins=marketplace_plugins,
        installed_skills=collect_skill_names(skill_roots),
        local_plugins_path=str(Path.home() / "plugins"),
        marketplace_path=str(marketplace) if marketplace.exists() else None,
        marketplace_has_pre_vibe=marketplace_has_pre_vibe,
        notes=notes,
    )


def component_suggestions_for(
    task: str,
    scenario: str,
    environment: CodexEnvironment,
) -> tuple[list[str], list[str]]:
    lower = task.lower()
    installed = {name.lower() for name in environment.installed_skills + environment.installed_plugins}
    suggestions: list[str] = []
    missing: list[str] = []

    if scenario in {"coding", "mixed"}:
        suggestions.append("Use project AGENTS guidance, repo-local scripts, and built-in code review before final handoff.")

    if scenario in {"research", "mixed"}:
        suggestions.append("Use live web/source lookup for current facts and cite primary sources in the handbook.")

    if "openai" in lower or "codex" in lower or "plugin" in lower:
        if any("openai-docs" in name for name in installed):
            suggestions.append("Use the installed openai-docs skill for official OpenAI/Codex behavior before making product claims.")
        else:
            missing.append("Search official OpenAI/Codex docs and consider installing an OpenAI-docs helper before relying on product behavior.")

    if any(term in lower for term in ("ui", "frontend", "界面", "前端", "dashboard", "landing", "web app")):
        if any("ui-ux" in name or "ui-styling" in name for name in installed):
            suggestions.append("Use the installed UI/UX styling guidance for layout, responsive states, and accessibility checks.")
        else:
            missing.append("Consider installing a UI/UX or frontend design skill/plugin if the task needs polished interface decisions.")

    if any(term in lower for term in ("image", "banner", "logo", "brand", "视觉", "图片", "海报", "品牌")):
        if any("imagegen" in name or "design" in name or "brand" in name for name in installed):
            suggestions.append("Use installed image/design guidance only for visual assets that the task explicitly needs.")
        else:
            missing.append("Consider a design/image generation component if the deliverable needs visual assets.")

    if is_reverse_engineering_task(task):
        suggestions.append("Use only read-only target identification first; require explicit target path and authorization before deeper analysis.")

    return suggestions[:10], missing[:10]


def blocking_questions_for(task: str, scenario: str, intensity: str, language: str) -> list[BlockingQuestion]:
    profile = INTENSITY_PROFILES[intensity]
    if profile.max_questions <= 0:
        return []
    zh = language in {"zh", "bilingual"}
    questions: list[BlockingQuestion] = []
    if has_ambiguous_external_target(task):
        questions.append(
            BlockingQuestion(
                "target_path_and_authorization",
                "目标确认" if zh else "Target",
                (
                    "请提供要分析对象的绝对路径、文件/应用名、文件类型，并确认你有权分析它。"
                    if zh
                    else "Provide the target's absolute path, file/app name, type, and confirm you are authorized to analyze it."
                ),
                "The target and authorization determine whether any reverse-analysis workflow is allowed.",
                ["提供路径和授权确认", "仅做通用方法说明", "暂停逆向任务"] if zh else ["Provide path and authorization", "General method only", "Pause reverse task"],
            )
        )
    if scenario in {"coding", "mixed"} and looks_like_new_product_task(task):
        questions.append(
            BlockingQuestion(
                "core_user_flow",
                "核心流程" if zh else "Core Flow",
                (
                    "这个版本最核心的用户流程是什么？请用一句话说明用户输入什么、系统处理什么、最终输出什么。"
                    if zh
                    else "What is the core user flow for this version? In one sentence: what does the user input, what does the system process, and what is the final output?"
                ),
                "The core flow determines product scope, UI states, data handling, and acceptance criteria.",
                ["一句话说明核心流程", "由现有文档推断", "先做最小可运行流程"] if zh else ["Describe the core flow", "Infer from docs", "Start with the smallest runnable flow"],
            )
        )
        if any(term in task.lower() for term in ("ai", "简历", "resume", "upload", "上传", "用户", "账号")):
            questions.append(
                BlockingQuestion(
                    "data_and_account_boundary",
                    "数据边界" if zh else "Data Boundary",
                    (
                        "本轮是否需要账号、文件上传/存储、第三方 AI API，还是只做本地/演示版流程？"
                        if zh
                        else "Does this round need accounts, file upload/storage, or a third-party AI API, or should it stay a local/demo flow?"
                    ),
                    "Data, accounts, and AI dependencies change security, privacy, implementation, and verification.",
                    ["本地/演示版", "需要上传/存储", "需要账号或第三方 API"] if zh else ["Local/demo only", "Needs upload/storage", "Needs account or API"],
                )
            )
        questions.append(
            BlockingQuestion(
                "delivery_boundary",
                "交付标准" if zh else "Delivery",
                (
                    "本轮完成标准是可点击原型、可运行 MVP，还是生产可部署版本？"
                    if zh
                    else "Should this round deliver a clickable prototype, runnable MVP, or production-deployable version?"
                ),
                "The delivery level changes implementation depth and validation.",
                ["可运行 MVP", "可点击原型", "生产可部署版本"] if zh else ["Runnable MVP", "Clickable prototype", "Production-deployable"],
            )
        )
    if scenario == "research" and intensity != "mini":
        questions.append(
            BlockingQuestion(
                "research_decision",
                "研究决策" if zh else "Decision",
                (
                    "这次研究最终要支持什么决策？例如选型、市场判断、竞品比较、还是实施方案。"
                    if zh
                    else "What decision should this research support: tool choice, market judgment, competitor comparison, or implementation plan?"
                ),
                "The decision determines source selection and output structure.",
                ["实施方案", "选型判断", "竞品/市场比较"] if zh else ["Implementation plan", "Tool choice", "Market/competitor comparison"],
            )
        )
    if scenario in {"coding", "mixed"} and ("deploy" in task.lower() or "部署" in task):
        questions.append(
            BlockingQuestion(
                "deployment_boundary",
                "部署权限" if zh else "Deploy",
                "本轮是否允许真实部署，还是只准备部署方案和本地验证？" if zh else "Is live deployment allowed, or should this only prepare a deployment plan and local verification?",
                "Deployment permissions change risk, approvals, and verification.",
                ["只准备方案和本地验证", "允许真实部署", "先询问每个部署动作"] if zh else ["Plan and local verify only", "Live deploy allowed", "Ask before each deploy action"],
            )
        )
    return questions[: profile.max_questions]


def context_actions_for(
    task: str,
    scenario: str,
    intensity: str,
    project_context: ProjectContext | None = None,
    codex_environment: CodexEnvironment | None = None,
) -> list[ContextAction]:
    profile = INTENSITY_PROFILES[intensity]
    actions: list[ContextAction] = []
    if not project_context or not project_context.scan_performed:
        actions.append(
            ContextAction(
                "project_execution_index",
                "local_scan",
                "Build a safe project execution index before asking blocking questions.",
            )
        )
    if not codex_environment:
        actions.append(
            ContextAction(
                "codex_component_index",
                "environment",
                "Inspect AGENTS guidance and installed Codex components before asking questions.",
            )
        )
    if scenario in {"research", "mixed"} and profile.allow_fetch:
        actions.append(
            ContextAction(
                "source_map",
                "fetch_plan",
                "Create or perform a source map only when external facts materially change the task.",
                required=False,
            )
        )
    if is_reverse_engineering_task(task) and has_target_path(task):
        actions.append(
            ContextAction(
                "reverse_target_identification",
                "local_inspection",
                "Run read-only target identification such as path, size, file type, hash, and platform metadata.",
            )
        )
    return actions


def artifact_rules_for(language: str) -> list[str]:
    if language in {"zh", "bilingual"}:
        return [
            "三份 Markdown 必须围绕用户任务和项目证据定制写作。",
            "最终产物不得出现 pre-vibe、插件实现、MCP server 或 workflow 内部表述，除非用户任务本身就是开发该工具。",
            "PRE_VIBE_SPEC.md 面向初级用户，是项目 handbook；包含目标、用户场景、范围、需求、验收、边界、风险、建议、组件使用建议和下一步。",
            "PROJECT_AGENTS.md 和 FIRST_PROMPT.md 面向 Codex；只保留执行规则、约束、文件指针、验收标准和必要操作边界。",
            "PROJECT_AGENTS.md 必须参考全局 AGENTS.md；不得加入与全局指令冲突或削弱全局指令的规则。",
            "PRE_VIBE_SPEC.md 与 PROJECT_AGENTS.md 必须彼此独立；任一文件不得出现另一文件的文件名或路径。FIRST_PROMPT.md 可以引用必要文件。",
            "问题必须通过 Codex 原生提问/审批 UI 展示；不得把阻塞问题直接写在普通聊天消息中。",
            "信息不足时先询问或补上下文，不得用模板语言填空。",
        ]
    return [
        "All three Markdown files must be custom-written from the user's task and project evidence.",
        "Final artifacts must not mention pre-vibe, plugin implementation, MCP server, or workflow internals unless the user is building this tool.",
        "PRE_VIBE_SPEC.md is a beginner-friendly project handbook with goal, user scenarios, scope, requirements, acceptance criteria, boundaries, risks, suggestions, component recommendations, and next steps.",
        "PROJECT_AGENTS.md and FIRST_PROMPT.md are agent-facing and should contain only execution rules, constraints, file pointers, acceptance criteria, and necessary operation boundaries.",
        "PROJECT_AGENTS.md must account for global AGENTS.md and must not conflict with or weaken global instructions.",
        "PRE_VIBE_SPEC.md and PROJECT_AGENTS.md must be standalone; neither file may mention the other file's filename or path. FIRST_PROMPT.md may reference necessary files.",
        "Blocking questions must be shown through Codex's native question/approval UI, not as ordinary chat text.",
        "When context is missing, ask or acquire context; never fill gaps with template language.",
    ]


def determine_next_state(
    questions: Iterable[BlockingQuestion],
    actions: Iterable[ContextAction],
    evidence_refs: Iterable[EvidenceRef] | None = None,
) -> str:
    evidence_ids = {evidence.id for evidence in evidence_refs or []}
    for action in actions:
        if action.required and action.id not in evidence_ids:
            return NEEDS_CONTEXT
    if list(questions):
        return NEEDS_USER_INPUT
    return READY_TO_COMPILE


def route_intake(
    task: str,
    project: str | Path = ".",
    *,
    scenario: str = "auto",
    intensity: str = "auto",
    language: str = "auto",
    evidence_refs: Iterable[EvidenceRef] | None = None,
    scan: bool = True,
) -> IntakeDecision:
    selected_scenario = classify_scenario(task, scenario)
    selected_language = choose_language(task, language)
    selected_intensity = choose_intensity(task, selected_scenario, intensity)
    profile = INTENSITY_PROFILES[selected_intensity]
    project_context: ProjectContext | None = None
    if scan and profile.allow_default_scan:
        project_context = safe_walk(Path(project).expanduser().resolve(), profile.max_scanned_files, selected_scenario)
    codex_environment = inspect_codex_environment()
    suggestions, missing_suggestions = component_suggestions_for(
        task,
        selected_scenario,
        codex_environment,
    )
    questions = blocking_questions_for(task, selected_scenario, selected_intensity, selected_language)
    actions = context_actions_for(
        task,
        selected_scenario,
        selected_intensity,
        project_context,
        codex_environment,
    )
    evidence = list(evidence_refs or [])
    evidence_ids = {item.id for item in evidence}
    if project_context and project_context.scan_performed and "project_execution_index" not in evidence_ids:
        evidence.append(
            EvidenceRef(
                "project_execution_index",
                project_context.root,
                f"Scanned {len(project_context.scanned_files)} allowlisted files and {len(project_context.key_dirs)} top-level directories.",
            )
        )
        evidence_ids.add("project_execution_index")
    if codex_environment and "codex_component_index" not in evidence_ids:
        evidence.append(
            EvidenceRef(
                "codex_component_index",
                codex_environment.codex_home or "Codex home",
                f"Indexed {len(codex_environment.installed_plugins)} plugins and {len(codex_environment.installed_skills)} standalone skills.",
            )
        )
    state = determine_next_state(questions, actions, evidence)
    assumptions = []
    if selected_intensity == "mini":
        assumptions.append("Use the smallest useful preparation path unless the user asks for deeper planning.")
    return IntakeDecision(
        raw_input=task,
        scenario=selected_scenario,
        intensity=selected_intensity,
        language=selected_language,
        risk=assess_risk(task, selected_scenario),
        uncertainty=assess_uncertainty(task),
        state=state,
        blocking_questions=questions,
        context_actions=actions,
        assumptions=assumptions,
        artifact_rules=artifact_rules_for(selected_language),
        evidence_refs=evidence,
        project_context=project_context,
        codex_environment=codex_environment,
        component_suggestions=suggestions,
        missing_component_suggestions=missing_suggestions,
    )


def can_compile_artifacts(decision: IntakeDecision) -> bool:
    return decision.state == READY_TO_COMPILE


def estimate_tokens(text: str) -> int:
    cjk_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    other_chars = max(len(text) - cjk_chars, 0)
    return max(1, int(cjk_chars / 1.7 + other_chars / 4))


def redact_secret_like(text: str) -> str:
    patterns = (
        r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*[^\s]+",
        r"-----BEGIN [A-Z ]+PRIVATE KEY-----.*?-----END [A-Z ]+PRIVATE KEY-----",
    )
    redacted = text
    for pattern in patterns:
        redacted = re.sub(pattern, "[REDACTED]", redacted, flags=re.DOTALL)
    return redacted


def validate_artifact_contents(contents: dict[str, str]) -> None:
    for key, text in contents.items():
        if key in {"spec", "agents", "prompt"} and "INIT_AGENTS.md" in text:
            raise ValueError("artifact content must not reference the retired INIT_AGENTS.md filename")
    spec_text = contents.get("spec", "")
    agents_text = contents.get("agents", "")
    if re.search(r"(?i)(^|[/\\])PROJECT_AGENTS\.md\b|PROJECT_AGENTS\.md\b", spec_text):
        raise ValueError("PRE_VIBE_SPEC.md must not reference PROJECT_AGENTS.md")
    if re.search(r"(?i)(^|[/\\])PRE_VIBE_SPEC\.md\b|PRE_VIBE_SPEC\.md\b", agents_text):
        raise ValueError("PROJECT_AGENTS.md must not reference PRE_VIBE_SPEC.md")


def write_artifacts(output_dir: Path, contents: dict[str, str], status: dict[str, Any] | None = None) -> dict[str, str]:
    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}
    allowed = {key: value for key, value in ARTIFACT_FILENAMES.items() if key != "status"}
    validate_artifact_contents(contents)
    for key, text in contents.items():
        if key not in allowed:
            raise ValueError(f"unsupported artifact key: {key}")
        path = output_dir / allowed[key]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(redact_secret_like(text).rstrip() + "\n", encoding="utf-8")
        written[key] = str(path.relative_to(output_dir))
    if status is not None:
        status_path = output_dir / ARTIFACT_FILENAMES["status"]
        status_path.parent.mkdir(parents=True, exist_ok=True)
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written["status"] = str(status_path.relative_to(output_dir))
    return written


def to_jsonable(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect Pre-Vibe routing without generating Markdown templates.")
    parser.add_argument("--task", required=True)
    parser.add_argument("--project", default=".")
    parser.add_argument("--scenario", default="auto", choices=("auto", "general", "research", "coding", "mixed"))
    parser.add_argument("--intensity", default="auto", choices=("auto", "mini", "default", "architect"))
    parser.add_argument("--language", default="auto", choices=("auto", "zh", "en", "bilingual"))
    parser.add_argument("--no-scan", action="store_true", help="Skip the safe project scan; route_intake will return NEEDS_CONTEXT.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    decision = route_intake(
        args.task,
        args.project,
        scenario=args.scenario,
        intensity=args.intensity,
        language=args.language,
        scan=not args.no_scan,
    )
    print(json.dumps(decision, ensure_ascii=False, indent=2, default=to_jsonable))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
