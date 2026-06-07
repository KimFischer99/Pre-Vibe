"""Task routing, question selection, and workflow state decisions."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from pv_environment import inspect_codex_environment
from pv_models import (
    INTENSITY_PROFILES,
    NEEDS_CONTEXT,
    NEEDS_USER_INPUT,
    READY_TO_COMPILE,
    BlockingQuestion,
    CodexEnvironment,
    ContextAction,
    EvidenceRef,
    EvidenceItem,
    IntakeDecision,
    ProjectContext,
    ProjectLanguageItem,
)
from pv_scan import safe_walk
from pv_settings import resolve_requested_intensity
from pv_terms import (
    AMBIGUOUS_TARGET_TERMS,
    ARCHITECT_TERMS,
    CODING_TERMS,
    RESEARCH_TERMS,
    REVERSE_TERMS,
    TARGET_PATH_RE,
)


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
            "营造",
            "构建",
            "页面",
            "在线",
            "实现",
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


def document_output_plan_for(
    project_context: ProjectContext | None,
    intensity: str,
    project_root: Path | None = None,
) -> tuple[dict[str, str], str]:
    has_root_agents = bool(project_context and project_context.project_agents_path)
    if not has_root_agents and project_context is None and project_root is not None:
        has_root_agents = (project_root / "CLAUDE.md").exists()
    plan = {
        "spec": "PRE_VIBE_SPEC.md",
        "prompt": "FIRST_PROMPT.md",
    }
    if has_root_agents:
        plan["project_agents"] = "PROJECT_CLAUDE.md"
        mode = "proposal"
    else:
        plan["agents"] = "CLAUDE.md"
        mode = "create"
    if intensity == "architect":
        plan["project_index"] = "PROJECT_INDEX.md"
    return plan, mode


def evidence_buffer_for(evidence_refs: Iterable[EvidenceRef]) -> list[EvidenceItem]:
    return [
        EvidenceItem(
            id=ref.id,
            source=ref.source,
            summary=ref.summary,
            confidence=ref.confidence,
            used_in=ref.used_in or ["PRE_VIBE_SPEC.md"],
        )
        for ref in evidence_refs
    ]


def project_language_for(task: str, language: str) -> list[ProjectLanguageItem]:
    lower = task.lower()
    items: list[ProjectLanguageItem] = []
    if any(term in lower for term in ("account", "账号", "账户", "user", "用户")):
        items.append(
            ProjectLanguageItem(
                "User" if language != "zh" else "用户",
                "The person who signs in or operates the product.",
                ["Account", "Customer"] if language != "zh" else ["账号", "客户"],
                "Confirm billing or workspace ownership later if the product needs it.",
            )
        )
    if any(term in lower for term in ("plugin", "插件", "claude")):
        items.append(
            ProjectLanguageItem(
                "Claude Code plugin" if language != "zh" else "Claude Code 插件",
                "A Claude Code extension package that can bundle MCP tools and workflow guidance.",
                ["skill", "slash command"] if language != "zh" else ["skill", "slash 命令"],
                "Use this term when describing Pre-Vibe-style integrations.",
            )
        )
    if any(term in lower for term in ("project", "项目", "mvp", "app", "应用")):
        items.append(
            ProjectLanguageItem(
                "Project" if language != "zh" else "项目",
                "The active workspace and deliverable being prepared for Claude Code execution.",
                ["task dump"] if language != "zh" else ["临时任务堆"],
                "Keep this term tied to the current workspace, not the Pre-Vibe implementation.",
            )
        )
    return items[:6]


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

    if "anthropic" in lower or "claude" in lower or "plugin" in lower:
        if any("anthropic-docs" in name for name in installed):
            suggestions.append("Use the installed anthropic-docs skill for official Anthropic/Claude Code behavior before making product claims.")
        else:
            missing.append("Search official Anthropic/Claude Code docs and consider installing an Anthropic-docs helper before relying on product behavior.")

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
                "Target path and authorization determine whether reverse-analysis can proceed. Without this, only general methodology is possible.",
                ["提供路径和授权，开始分析", "只做通用方法论说明", "暂停，稍后提供"] if zh else ["Provide path & authorization, begin analysis", "General methodology only", "Pause, I'll provide details later"],
                "提供路径和授权，开始分析" if zh else "Provide path & authorization, begin analysis",
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
                "The core flow determines product scope, UI design, data handling, and what 'done' looks like for this round.",
                ["输入→处理→输出，一句话说清", "从已有文档推断", "先做可运行的最小原型"] if zh else ["Input → process → output in one sentence", "Infer from existing project docs", "Start with smallest runnable prototype"],
                "先做可运行的最小原型" if zh else "Start with smallest runnable prototype",
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
                    "Data persistence, user accounts, and external API calls each add significant engineering complexity and change the implementation approach.",
                    ["本地演示版，无外部依赖", "需要文件上传/存储", "需要用户账号或第三方 API"] if zh else ["Local demo — no external dependencies", "Needs file upload/storage", "Needs user accounts or external API"],
                    "本地演示版，无外部依赖" if zh else "Local demo — no external dependencies",
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
                "The delivery level determines implementation depth, error handling, testing rigor, and how much engineering quality is needed.",
                ["可运行 MVP — 核心功能可用", "可点击原型 — 验证交互流程", "生产部署版本 — 完整工程质量"] if zh else ["Runnable MVP — core features working", "Clickable prototype — validate UX flow", "Production-deployable — full engineering quality"],
                "可运行 MVP — 核心功能可用" if zh else "Runnable MVP — core features working",
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
                "The type of decision determines which sources matter, how deep to go, and what format the output should take.",
                ["实施方案 — 给我可执行的步骤", "技术选型 — 比较并推荐方案", "竞品/市场比较 — 提供对比分析"] if zh else ["Implementation plan — give me executable steps", "Tool/framework choice — compare and recommend", "Market/competitor comparison — provide analysis"],
                "实施方案 — 给我可执行的步骤" if zh else "Implementation plan — give me executable steps",
            )
        )
    if scenario in {"coding", "mixed"} and ("deploy" in task.lower() or "部署" in task):
        questions.append(
            BlockingQuestion(
                "deployment_boundary",
                "部署权限" if zh else "Deploy",
                "本轮是否允许真实部署，还是只准备部署方案和本地验证？" if zh else "Is live deployment allowed, or should this only prepare a deployment plan and local verification?",
                "Deployment changes risk profile: live deploys affect real environments, while plan-only keeps work safely contained.",
                ["只准备方案，本地验证", "允许真实部署到线上", "每个部署操作前询问"] if zh else ["Plan only — local verification", "Live deploy to production allowed", "Ask before each deploy action"],
                "只准备方案，本地验证" if zh else "Plan only — local verification",
            )
        )
    # Fallback: ensure at least one baseline question is always asked.
    # The user cannot generate meaningful documents without answering what they want.
    if not questions:
        questions.append(
            BlockingQuestion(
                "baseline_scope",
                "任务范围" if zh else "Scope",
                "请用一两句话描述你想做什么：最终产出是什么、给谁用、最核心的功能是什么？" if zh else "In one or two sentences: what do you want to build, who is it for, and what is the single most important feature?",
                "Without at least a basic scope, SPEC/CLAUDE/FIRST_PROMPT cannot be written with any useful precision.",
                ["先说核心目标和用户", "已有详细 PRD，从文档推断", "只是探索，不给具体目标"] if zh else ["Describe core goal and audience", "Already have a detailed PRD — infer from docs", "Just exploring — no concrete goal yet"],
                "先说核心目标和用户" if zh else "Describe core goal and audience",
                requires_native_ui=True,
            )
        )
    return questions[: profile.max_questions]


def context_actions_for(
    task: str,
    scenario: str,
    intensity: str,
    project_context: ProjectContext | None = None,
    codex_environment: CodexEnvironment | None = None,
    inspect_codex_environment_enabled: bool = True,
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
    if inspect_codex_environment_enabled and not codex_environment:
        actions.append(
            ContextAction(
                "codex_component_index",
                "environment",
                "Inspect AGENTS guidance and installed Claude Code components before asking questions.",
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
            "三份文档必须围绕用户任务和项目实际证据定制写作，彼此零重合。",
            "最终产物不得出现 pre-vibe、插件实现、MCP server 或 workflow 内部表述。",
            "PRE_VIBE_SPEC.md 独占内容（这些只能出现在 SPEC，不得出现在 CLAUDE.md 或 FIRST_PROMPT.md）：环境变量清单、语言/框架栈、已安装 plugins 和 skills 列表及建议用途、项目组件清单、git 状态、文件结构摘要、可执行的集成建议。",
            "PRE_VIBE_SPEC.md 禁止内容：通用技术科普、行业背景介绍、Wikipedia 式定义、与其他文档重合的执行规则或合约条款。",
            "CLAUDE.md / PROJECT_CLAUDE.md 独占内容（只在这里写，不得在 SPEC 或 FIRST_PROMPT.md 重复）：执行规则、文件指针、操作边界、验收标准、与全局 CLAUDE.md 的兼容声明。",
            "CLAUDE.md / PROJECT_CLAUDE.md 禁止内容：环境变量、plugins/skills 列表（属于 SPEC）、交付合约条款（属于 FIRST_PROMPT.md）。",
            "FIRST_PROMPT.md 独占内容（只在这里写，不得在 SPEC 或 CLAUDE.md 重复）：Completion Contract、停止询问条件、验证门、交付物定义。",
            "FIRST_PROMPT.md 禁止内容：环境变量、组件清单、执行规则——这些属于 SPEC 和 CLAUDE.md。",
            "architect 档可额外生成 PROJECT_INDEX.md；FIRST_PROMPT.md 可以引用 PROJECT_INDEX.md。",
            "问题必须通过 Claude Code 原生提问/审批 UI 展示；不得把阻塞问题直接写在普通聊天消息中。",
            "每个阻塞问题必须包含推荐答案；能从项目文件推断的信息不得重复询问用户。",
            "信息不足时先询问或补上下文，不得用模板语言填空。",
        ]
    return [
        "All three documents must be custom-written from project evidence with ZERO content overlap between them.",
        "Final artifacts must not mention pre-vibe, plugin implementation, MCP server, or workflow internals.",
        "PRE_VIBE_SPEC.md EXCLUSIVE content (ONLY here, NOT in CLAUDE.md or FIRST_PROMPT.md): env vars, language/framework stack, installed plugins & skills with suggested usage, project component inventory, git state, file structure summary, actionable integration suggestions.",
        "PRE_VIBE_SPEC.md FORBIDDEN content: generic tech introductions, industry background, Wikipedia-style definitions, execution rules (those belong in CLAUDE.md), contract terms (those belong in FIRST_PROMPT.md).",
        "CLAUDE.md / PROJECT_CLAUDE.md EXCLUSIVE content (ONLY here): execution rules, file pointers, operation boundaries, acceptance criteria, global CLAUDE.md compatibility statement.",
        "CLAUDE.md / PROJECT_CLAUDE.md FORBIDDEN content: env vars, plugins/skills list (belongs in SPEC), delivery contract terms (belongs in FIRST_PROMPT.md).",
        "FIRST_PROMPT.md EXCLUSIVE content (ONLY here): Completion Contract, stop/ask conditions, verification gates, deliverable definition.",
        "FIRST_PROMPT.md FORBIDDEN content: env vars, component inventory, execution rules — those belong in SPEC and CLAUDE.md respectively.",
        "Architect effort may also produce PROJECT_INDEX.md; FIRST_PROMPT.md may reference PROJECT_INDEX.md.",
        "Blocking questions must be shown through Claude Code's native question/approval UI, not as ordinary chat text.",
        "Every blocking question must include a recommended answer; do not ask for facts already inferable from project files.",
        "When context is missing, ask or acquire context; never fill gaps with template language.",
    ]


def recovery_questions_for(project_context: ProjectContext | None, language: str) -> list[BlockingQuestion]:
    existing = project_context.existing_context if project_context else None
    if not existing or not existing.recovery_options:
        return []
    zh = language in {"zh", "bilingual"}
    return [
        BlockingQuestion(
            "existing_context_recovery",
            "上下文恢复" if zh else "Recovery",
            (
                "检测到已有 Pre-Vibe 启动文档。本轮要复用更新、重新生成，还是先比较旧上下文？"
                if zh
                else "Existing Pre-Vibe starting documents were found. Should this run reuse, regenerate, or compare them first?"
            ),
            "Existing context changes whether SPEC/AGENTS are updated and FIRST_PROMPT is fully rewritten.",
            existing.recovery_options,
            existing.recovery_options[0],
        )
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
    project_root = Path(project).expanduser().resolve()
    intensity_request, settings = resolve_requested_intensity(project_root, intensity)
    selected_intensity = choose_intensity(task, selected_scenario, intensity_request)
    if intensity_request == "auto" and not settings.allow_auto_upgrade and selected_intensity == "architect":
        selected_intensity = "default"
    profile = INTENSITY_PROFILES[selected_intensity]
    project_context: ProjectContext | None = None
    if scan and profile.allow_default_scan:
        project_context = safe_walk(project_root, profile.max_scanned_files, selected_scenario)
    codex_environment = inspect_codex_environment() if settings.inspect_codex_environment else None
    if codex_environment:
        suggestions, missing_suggestions = component_suggestions_for(
            task,
            selected_scenario,
            codex_environment,
        )
    else:
        suggestions, missing_suggestions = [], []
    questions = recovery_questions_for(project_context, selected_language)
    questions.extend(blocking_questions_for(task, selected_scenario, selected_intensity, selected_language))
    questions = questions[: profile.max_questions]
    actions = context_actions_for(
        task,
        selected_scenario,
        selected_intensity,
        project_context,
        codex_environment,
        settings.inspect_codex_environment,
    )
    evidence = list(evidence_refs or [])
    evidence_ids = {item.id for item in evidence}
    if project_context and project_context.scan_performed and "project_execution_index" not in evidence_ids:
        evidence.append(
            EvidenceRef(
                "project_execution_index",
                project_context.root,
                f"Scanned {len(project_context.scanned_files)} allowlisted files and {len(project_context.key_dirs)} top-level directories.",
                "high",
                ["PRE_VIBE_SPEC.md", "CLAUDE.md", "FIRST_PROMPT.md"],
            )
        )
        evidence_ids.add("project_execution_index")
    if codex_environment and "codex_component_index" not in evidence_ids:
        evidence.append(
            EvidenceRef(
                "codex_component_index",
                codex_environment.codex_home or "Claude Code home",
                f"Indexed {len(codex_environment.installed_plugins)} plugins and {len(codex_environment.installed_skills)} standalone skills.",
                "high",
                ["CLAUDE.md", "FIRST_PROMPT.md"],
            )
        )
    output_plan, agent_guidance_mode = document_output_plan_for(project_context, selected_intensity, project_root)
    if selected_intensity != "architect" or not settings.architect_project_index:
        output_plan.pop("project_index", None)
    state = determine_next_state(questions, actions, evidence)
    assumptions = []
    if selected_intensity == "mini":
        assumptions.append("Use the smallest useful preparation path unless the user asks for deeper planning.")
    if settings.session_intensity:
        assumptions.append(f"Use session intensity override: {settings.session_intensity}.")
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
        evidence_buffer=evidence_buffer_for(evidence),
        project_language=project_language_for(task, selected_language),
        document_output_plan=output_plan,
        agent_guidance_mode=agent_guidance_mode,
        recovery_action=project_context.existing_context.recommended_action if project_context and project_context.existing_context else None,
    )


def prepare_project_start(
    task: str,
    project: str | Path = ".",
    *,
    scenario: str = "auto",
    intensity: str = "auto",
    language: str = "auto",
    evidence_refs: Iterable[EvidenceRef] | None = None,
    scan: bool = True,
) -> dict[str, object]:
    from pv_compact import compact_decision

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


def can_compile_artifacts(decision: IntakeDecision) -> bool:
    return decision.state == READY_TO_COMPILE
