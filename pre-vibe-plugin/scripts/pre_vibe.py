#!/usr/bin/env python3
"""pre-vibe workflow utilities.

The module is intentionally not a Markdown template generator. It provides
deterministic helpers that Codex can call while running the pre-vibe workflow:
task routing, intensity selection, safe project scanning, environment inspection,
state gating, and artifact writes for LLM-authored content.
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
    "agents": "INIT_AGENTS.md",
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
        "Light intake for ordinary work, small research, or tiny changes.",
        max_questions=3,
        max_fetches=0,
        max_scanned_files=0,
        allow_default_scan=False,
        allow_fetch=False,
    ),
    "default": IntensityProfile(
        "default",
        "Balanced intake for normal research and coding tasks.",
        max_questions=5,
        max_fetches=2,
        max_scanned_files=10,
        allow_default_scan=True,
        allow_fetch=True,
    ),
    "architect": IntensityProfile(
        "architect",
        "Full staged intake for new projects, refactors, and complex research.",
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
    question: str
    reason: str


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


def inspect_codex_environment() -> CodexEnvironment:
    codex_home = os.environ.get("CODEX_HOME")
    default_codex_home = Path.home() / ".codex"
    global_agents = find_global_agents()
    cache_root = default_codex_home / "plugins" / "cache"
    plugin_cache: list[str] = []
    if cache_root.exists():
        for path in sorted(cache_root.glob("*/*")):
            if path.is_dir():
                plugin_cache.append(str(path))
    marketplace = Path.home() / ".agents" / "plugins" / "marketplace.json"
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
    notes = []
    if not global_agents:
        notes.append("No global AGENTS.md was found.")
    if not marketplace_has_pre_vibe:
        notes.append("pre-vibe is not listed in the default personal marketplace.")
    return CodexEnvironment(
        codex_home=codex_home or str(default_codex_home),
        global_agents_path=str(global_agents) if global_agents else None,
        installed_plugin_cache=plugin_cache,
        local_plugins_path=str(Path.home() / "plugins"),
        marketplace_path=str(marketplace) if marketplace.exists() else None,
        marketplace_has_pre_vibe=marketplace_has_pre_vibe,
        notes=notes,
    )


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
                (
                    "请提供要分析对象的绝对路径、文件/应用名、文件类型，并确认你有权分析它。"
                    if zh
                    else "Provide the target's absolute path, file/app name, type, and confirm you are authorized to analyze it."
                ),
                "The target and authorization determine whether any reverse-analysis workflow is allowed.",
            )
        )
    if scenario in {"coding", "mixed"} and looks_like_new_product_task(task):
        questions.append(
            BlockingQuestion(
                "core_user_flow",
                (
                    "这个版本最核心的用户流程是什么？请用一句话说明用户输入什么、系统处理什么、最终输出什么。"
                    if zh
                    else "What is the core user flow for this version? In one sentence: what does the user input, what does the system process, and what is the final output?"
                ),
                "The core flow determines product scope, UI states, data handling, and acceptance criteria.",
            )
        )
        if any(term in task.lower() for term in ("ai", "简历", "resume", "upload", "上传", "用户", "账号")):
            questions.append(
                BlockingQuestion(
                    "data_and_account_boundary",
                    (
                        "本轮是否需要账号、文件上传/存储、第三方 AI API，还是只做本地/演示版流程？"
                        if zh
                        else "Does this round need accounts, file upload/storage, or a third-party AI API, or should it stay a local/demo flow?"
                    ),
                    "Data, accounts, and AI dependencies change security, privacy, implementation, and verification.",
                )
            )
        questions.append(
            BlockingQuestion(
                "delivery_boundary",
                (
                    "本轮完成标准是可点击原型、可运行 MVP，还是生产可部署版本？"
                    if zh
                    else "Should this round deliver a clickable prototype, runnable MVP, or production-deployable version?"
                ),
                "The delivery level changes implementation depth and validation.",
            )
        )
    if scenario == "research" and intensity != "mini":
        questions.append(
            BlockingQuestion(
                "research_decision",
                (
                    "这次研究最终要支持什么决策？例如选型、市场判断、竞品比较、还是实施方案。"
                    if zh
                    else "What decision should this research support: tool choice, market judgment, competitor comparison, or implementation plan?"
                ),
                "The decision determines source selection and output structure.",
            )
        )
    if scenario in {"coding", "mixed"} and ("deploy" in task.lower() or "部署" in task):
        questions.append(
            BlockingQuestion(
                "deployment_boundary",
                "本轮是否允许真实部署，还是只准备部署方案和本地验证？" if zh else "Is live deployment allowed, or should this only prepare a deployment plan and local verification?",
                "Deployment permissions change risk, approvals, and verification.",
            )
        )
    return questions[: profile.max_questions]


def context_actions_for(
    task: str,
    scenario: str,
    intensity: str,
    project_context: ProjectContext | None = None,
) -> list[ContextAction]:
    profile = INTENSITY_PROFILES[intensity]
    actions: list[ContextAction] = []
    if scenario in {"coding", "mixed"} and profile.allow_default_scan:
        actions.append(
            ContextAction(
                "safe_project_scan",
                "local_scan",
                "Read allowlisted project files and relevant project guidance before writing artifacts.",
            )
        )
    if scenario in {"coding", "mixed"}:
        actions.append(
            ContextAction(
                "codex_environment_check",
                "environment",
                "Check AGENTS.md, installed plugin state, and Codex workflow affordances.",
                required=False,
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
    if project_context and project_context.scanned_files:
        actions = [
            action
            for action in actions
            if action.id != "safe_project_scan"
        ]
    return actions


def artifact_rules_for(language: str) -> list[str]:
    if language in {"zh", "bilingual"}:
        return [
            "三份 Markdown 必须围绕用户任务和项目证据定制写作。",
            "最终产物不得出现 pre-vibe、plugin、skill、MCP 或组件实现相关表述，除非用户任务本身就是开发该工具。",
            "PRE_VIBE_SPEC.md 面向初级用户，是项目 handbook；解释目标、边界、建议、风险和下一步。",
            "INIT_AGENTS.md 和 FIRST_PROMPT.md 面向 Codex；只保留执行规则、约束、文件指针和验收标准。",
            "INIT_AGENTS.md 必须参考全局 AGENTS.md；不得加入与全局指令冲突或削弱全局指令的规则。",
            "信息不足时先询问或补上下文，不得用模板语言填空。",
        ]
    return [
        "All three Markdown files must be custom-written from the user's task and project evidence.",
        "Final artifacts must not mention pre-vibe, plugin, skill, MCP, or implementation internals unless the user is building this tool.",
        "PRE_VIBE_SPEC.md is a beginner-friendly project handbook with goal, scope, suggestions, risks, and next steps.",
        "INIT_AGENTS.md and FIRST_PROMPT.md are agent-facing and should contain only execution rules, constraints, file pointers, and acceptance criteria.",
        "INIT_AGENTS.md must account for global AGENTS.md and must not conflict with or weaken global instructions.",
        "When context is missing, ask or acquire context; never fill gaps with template language.",
    ]


def determine_next_state(
    questions: Iterable[BlockingQuestion],
    actions: Iterable[ContextAction],
    evidence_refs: Iterable[EvidenceRef] | None = None,
) -> str:
    if list(questions):
        return NEEDS_USER_INPUT
    evidence_ids = {evidence.id for evidence in evidence_refs or []}
    for action in actions:
        if action.required and action.id not in evidence_ids:
            return NEEDS_CONTEXT
    return READY_TO_COMPILE


def route_intake(
    task: str,
    project: str | Path = ".",
    *,
    scenario: str = "auto",
    intensity: str = "auto",
    language: str = "auto",
    evidence_refs: Iterable[EvidenceRef] | None = None,
    scan: bool = False,
) -> IntakeDecision:
    selected_scenario = classify_scenario(task, scenario)
    selected_language = choose_language(task, language)
    selected_intensity = choose_intensity(task, selected_scenario, intensity)
    profile = INTENSITY_PROFILES[selected_intensity]
    project_context: ProjectContext | None = None
    if scan and profile.allow_default_scan and not has_ambiguous_external_target(task):
        project_context = safe_walk(Path(project).expanduser().resolve(), profile.max_scanned_files, selected_scenario)
    questions = blocking_questions_for(task, selected_scenario, selected_intensity, selected_language)
    actions = context_actions_for(task, selected_scenario, selected_intensity, project_context)
    evidence = list(evidence_refs or [])
    state = determine_next_state(questions, actions, evidence)
    assumptions = []
    if selected_intensity == "mini":
        assumptions.append("Use the smallest useful intake path unless the user asks for deeper planning.")
    if selected_scenario == "general":
        assumptions.append("No project scan is needed unless the user references project files.")
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


def write_artifacts(output_dir: Path, contents: dict[str, str], status: dict[str, Any] | None = None) -> dict[str, str]:
    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}
    allowed = {key: value for key, value in ARTIFACT_FILENAMES.items() if key != "status"}
    for key, text in contents.items():
        if key not in allowed:
            raise ValueError(f"unsupported artifact key: {key}")
        path = output_dir / allowed[key]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(redact_secret_like(text).rstrip() + "\n", encoding="utf-8")
        written[key] = str(path)
    if status is not None:
        status_path = output_dir / ARTIFACT_FILENAMES["status"]
        status_path.parent.mkdir(parents=True, exist_ok=True)
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written["status"] = str(status_path)
    return written


def to_jsonable(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect pre-vibe intake routing without generating Markdown templates.")
    parser.add_argument("--task", required=True)
    parser.add_argument("--project", default=".")
    parser.add_argument("--scenario", default="auto", choices=("auto", "general", "research", "coding", "mixed"))
    parser.add_argument("--intensity", default="auto", choices=("auto", "mini", "default", "architect"))
    parser.add_argument("--language", default="auto", choices=("auto", "zh", "en", "bilingual"))
    parser.add_argument("--scan", action="store_true", help="Perform the safe allowlist project scan.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    decision = route_intake(
        args.task,
        args.project,
        scenario=args.scenario,
        intensity=args.intensity,
        language=args.language,
        scan=args.scan,
    )
    print(json.dumps(decision, ensure_ascii=False, indent=2, default=to_jsonable))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
