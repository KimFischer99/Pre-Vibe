---
name: "pre-vibe"
description: "Prepare project starting context before implementation. Use when the user runs /pre-vibe, asks to set up a new project session, needs a project handbook, or wants to turn a rough request into structured starting documents. Coordinates MCP tools for safe project scanning, blocking questions, and FIRST_PROMPT.md handoff."
---

# Pre-Vibe Workflow

This skill is bundled with the Pre-Vibe plugin as workflow guidance for Claude Code. Users enable Pre-Vibe from the Claude Code plugin picker and describe their rough task naturally.

## Operating Rules

1. Start with `prepare_project_start`.
2. If the structured result contains `question_request`, Claude Code opens native question UI automatically. Do not call any MCP tool for this.
3. If existing Pre-Vibe documents are detected, ask whether to reuse/update, regenerate, or compare before writing.
4. Use project files, existing AGENTS/CLAUDE guidance, safe environment evidence, installed plugins and skills, git state, and past session context before asking the user for facts already available locally.
5. Every blocking question must include why it matters and the recommended answer.
6. Keep `PRE_VIBE_SPEC.md`, `CLAUDE.md` or `PROJECT_CLAUDE.md`, and `PROJECT_INDEX.md` independent from each other; `FIRST_PROMPT.md` may reference the files needed for handoff.
7. **PRE_VIBE_SPEC.md must focus on engineering execution details, not background knowledge.** Document the project's env vars, language/framework stack, installed plugins/skills, project structure, git state, component inventory, and past session history. Give actionable suggestions for component usage and integration. Avoid lengthy domain introductions or generic technology overviews.
8. Never stop after `write_project_starting_documents`. Document writing moves the workflow to approval, not completion.
9. After documents are written, present `FIRST_PROMPT.md` for user review as a plan audit. Wait for explicit approval before proceeding.
10. After explicit user approval, execute `/clear` to reset context, then read `FIRST_PROMPT.md` and continue from it as the active execution contract. Do not summarize the generated documents as the final answer.

## Mandatory Sequence

The plugin startup workflow must follow this order:

1. `prepare_project_start`
2. `write_project_starting_documents`
3. Present `FIRST_PROMPT.md` for user review — wait for explicit approval like a plan audit. Do not proceed without user confirmation.
4. After explicit user approval: execute `/clear`, read `FIRST_PROMPT.md`, and inject it as the execution contract. Begin real implementation work immediately.

The `/clear` and prompt injection are performed **by Claude Code**, not by the user. This is a strict rule. The user's only role in this step is auditing and approving the generated documents.

If the user rejects the handoff, stop and ask what should change. The Pre-Vibe run is complete only after explicit user approval, `/clear` is executed, and `FIRST_PROMPT.md` has been injected as the execution contract — or when the user explicitly cancels.

## Document Contract

- `PRE_VIBE_SPEC.md`: Engineering-focused project handbook. Must contain: env vars, stack/language, installed plugins & skills, project component inventory, git state, past session context, file structure pointers, and actionable integration suggestions. Minimize generic background information — focus on what matters for implementation.
- `CLAUDE.md`: created only when the project has no root `CLAUDE.md`.
- `PROJECT_CLAUDE.md`: proposal when a root `CLAUDE.md` already exists.
- `FIRST_PROMPT.md`: rewritten fully on each Pre-Vibe handoff as the execution contract.
- `PROJECT_INDEX.md`: architect effort only; indexes project intent, resources, tools, files, environment, and purpose for Claude Code.

## Evidence & Context Rules

- **Local-first**: env vars, git state, project files, installed plugins, installed skills, past session context, and project structure are the primary evidence sources. Use these before any external reference.
- **Online references**: treat as secondary evidence only when directly relevant to implementation decisions (e.g., API docs, version-specific syntax). Do not include general background articles or Wikipedia-style introductions in SPEC.
- **SPEC suggestions**: every suggestion in PRE_VIBE_SPEC.md must be actionable and tied to a concrete engineering decision. Prefer "Use the installed X plugin for Y" over "X is a popular tool for Y."

## Intensity

Use the configured effort level first, then session override, then auto detection. The user may change effort through Pre-Vibe settings tools without using command-style prompts.
