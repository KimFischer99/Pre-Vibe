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
4. Use project files, AGENTS guidance, and safe environment evidence before asking the user for facts already available locally.
5. Every blocking question must include why it matters and the recommended answer.
6. Keep `PRE_VIBE_SPEC.md`, `CLAUDE.md` or `PROJECT_CLAUDE.md`, and `PROJECT_INDEX.md` independent from each other; `FIRST_PROMPT.md` may reference the files needed for handoff.
7. Treat online references as evidence for `PRE_VIBE_SPEC.md`; keep `FIRST_PROMPT.md` compact.
8. Never stop after `write_project_starting_documents`. Document writing moves the workflow to approval, not completion.
9. After documents are written, immediately ask the user to approve the `FIRST_PROMPT.md` handoff.
10. After approval, read `FIRST_PROMPT.md` and continue from it as the active execution contract. Do not summarize the generated documents as the final answer.

## Mandatory Sequence

The plugin startup workflow must follow this order:

1. `prepare_project_start`
2. `write_project_starting_documents`
3. Request user approval for the `FIRST_PROMPT.md` handoff — explain that the next steps will be: review FIRST_PROMPT.md, then `/clear` to reset context, then inject FIRST_PROMPT.md as the execution contract.
4. After approval, ask the user to run `/clear`, then read and inject `FIRST_PROMPT.md` as the execution contract.

If Claude Code cannot open native question UI, pause and report that the UI is unavailable. If the user rejects the handoff, stop and ask what should change. The Pre-Vibe run is complete only when the handoff is approved and `FIRST_PROMPT.md` has been injected after `/clear`, or when the user explicitly cancels.

## Document Contract

- `PRE_VIBE_SPEC.md`: beginner-friendly project handbook with Project Language and Evidence.
- `CLAUDE.md`: created only when the project has no root `CLAUDE.md`.
- `PROJECT_CLAUDE.md`: proposal when a root `CLAUDE.md` already exists.
- `FIRST_PROMPT.md`: rewritten fully on each Pre-Vibe handoff as the execution contract.
- `PROJECT_INDEX.md`: architect effort only; indexes project intent, resources, tools, files, environment, and purpose for Claude Code.

## Intensity

Use the configured effort level first, then session override, then auto detection. The user may change effort through Pre-Vibe settings tools without using command-style prompts.
