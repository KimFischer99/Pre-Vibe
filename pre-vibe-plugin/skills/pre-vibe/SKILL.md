---
name: pre-vibe
description: Use for vague or first-session requests that need a Codex intake workflow before work starts. Clarifies user intent, inspects safe project/environment context, and writes task-specific PRE_VIBE_SPEC.md, INIT_AGENTS.md, and FIRST_PROMPT.md. For general work, research, and coding.
---

# pre-vibe

pre-vibe is a Codex intake workflow, not a template generator. It should feel like
Codex naturally preparing the task with the user before execution, not like the user is
manually calling a separate utility.

## Invocation

Use this workflow when a user starts with a vague, short, chaotic, or high-risk request,
especially at the beginning of a new session. Also use it when the user asks to prepare,
clarify, standardize, or inject first-turn context.

Do not announce "I am using a skill/plugin" in ordinary progress updates. Say what is
happening in natural task language, for example:

- "我先把这次任务整理成可执行的开工上下文。"
- "我先确认缺口，再读取必要的项目和环境信息。"
- "我会先把执行 prompt 收窄，避免把无关背景带进新会话。"

## Workflow State Machine

Follow this state machine. Do not skip gates.

1. `INTAKE_STARTED`
   - Preserve the user's raw input.
   - Classify scenario: `general`, `research`, `coding`, or `mixed`.
   - Choose intensity: `mini`, `default`, or `architect`.
   - Detect language from the user's input unless explicitly overridden.
   - Detect risk and uncertainty.

2. `NEEDS_USER_INPUT`
   - Enter this state when a blocking answer is missing.
   - Ask only questions whose answers change scope, architecture, data model,
     external dependency, user-facing behavior, acceptance criteria, permissions, or
     irreversible operations.
   - Use Codex's native question/user-input UI when available so the user can answer in
     the proper input surface. If that UI is unavailable, ask the same questions
     directly in chat.
   - Wait for the user's answer before continuing.
   - Do not generate final `PRE_VIBE_SPEC.md`, `INIT_AGENTS.md`, or `FIRST_PROMPT.md`
     in this state.
   - If intake notes are useful, keep them only in the current pre-vibe conversation
     context. Do not write `INTAKE.md`, `PRE_VIBE_INTAKE.md`, or any equivalent intake
     draft to disk.

3. `NEEDS_CONTEXT`
   - Enter this state when local project inspection, environment inspection, installed
     skills/plugins review, AGENTS/memory review, or external source lookup is needed.
   - Perform the context action before writing final artifacts.
   - Record evidence from actual files, tool outputs, user answers, or cited sources.
   - Keep temporary intake notes in conversation context only.
   - Do not write a final `FIRST_PROMPT.md` until required context actions are done.

4. `READY_TO_COMPILE`
   - Only now write the three final Markdown artifacts.
   - Every section must be custom-written from the user's task, project/environment
     evidence, and confirmed assumptions.

5. `AWAITING_APPROVAL`
   - Show the user the useful parts of `INIT_AGENTS.md` and `FIRST_PROMPT.md`.
   - Ask for approval before pre-vibe clears context and injects the first prompt.

6. `READY_TO_INJECT`
   - After approval, pre-vibe executes the clear-context command for the current
     workflow.
   - Then inject only `FIRST_PROMPT.md` content as the next session's initial context.
   - Do not ask the user to manually run `/clear`.

7. `DONE`
   - Exit the intake role. Leave the Markdown files on disk.

## Intensity Profiles

- `mini`: general work, simple writing, small research, tiny changes. Ask up to three
  blocking questions. Do not scan or fetch by default.
- `default`: normal research and coding tasks. Ask up to five blocking questions.
  Perform a light allowlist scan and fetch only when external facts affect execution.
- `architect`: new projects, major refactors, complex research, high-risk reverse or
  deployment work. Ask up to ten blocking questions in staged rounds, with broader
  context acquisition.

These are workflow intensity profiles, not strict token budgets. Still keep
`FIRST_PROMPT.md` minimal and executable.

## Context Acquisition

Use the bundled MCP/tools when available:

- `classify_intake` for routing and workflow state.
- `scan_project_safe` for allowlist project scanning.
- `inspect_codex_environment` for AGENTS, marketplace, plugin cache, and Codex setup.
- `write_pre_vibe_artifacts` only to write LLM-authored content, never to generate prose.

Safe scan defaults:

- Read project guides, PRDs/specs, package/config files, source tree summaries, and task
  files the user named.
- Do not read `.env`, private keys, tokens, credential stores, database dumps,
  production logs, or personal data exports.
- If environment variable information is needed, ask before reading names and never read
  secret values.

External lookup:

- Use it for research tasks, current API/framework behavior, deployment docs,
  compliance/security facts, or competitor/source evidence.
- Prefer official or primary sources when accuracy matters.
- Write a source map; do not paste long source summaries into `FIRST_PROMPT.md`.

Reverse or desktop target tasks:

- If the user says "desktop", "this thing", "这个东西", or similar without a path, ask
  for the exact target path and authorization first.
- If a target path is provided, do only read-only identification before planning:
  path, size, file type, hash, platform metadata, and package hints.
- Do not suggest bypassing DRM, licenses, access controls, or third-party protections.

## Artifact Rules

The three final Markdown files must be written for the user's actual task. They must
not contain reusable template language, placeholders, generic workflow advice, or text
about pre-vibe/plugin/skill/MCP internals unless the user's task is to work on this
tool itself.

### `PRE_VIBE_SPEC.md`

Audience: the user, especially a beginner. Treat it as a project handbook for this
task.

Must include:

- Raw user input.
- Normalized goal.
- Background and use case explained in plain language.
- In-scope and out-of-scope items.
- Functional and non-functional requirements.
- Acceptance criteria.
- Project/environment evidence with file paths and why each matters.
- Assumptions and unresolved unknowns.
- Practical suggestions, next steps, risk notes, and verification plan.
- Path guidance explaining which files are handbook/reference files and which file is
  meant for injection.

Use the user's language. Be clear enough for a junior builder to understand what will
happen and why.

### `INIT_AGENTS.md`

Audience: Codex or another coding agent.

Must include only durable project guidance:

- Existing global AGENTS summary and project AGENTS summary when available.
- Project-specific commands, conventions, directory rules, safety boundaries, and
  review expectations.
- Conflict policy: higher-priority user/system/global instructions remain higher.
- Conflict rule: never add guidance that contradicts, narrows, or weakens global
  AGENTS.md. If a useful project rule might conflict, rewrite it as subordinate to the
  global rule or omit it.

Do not include one-off task details, tutorial prose, user education, or long rationale.

### `FIRST_PROMPT.md`

Audience: Codex after pre-vibe clears context. This is the only default injected content.

Must include only:

- Goal.
- Current task for this execution round.
- Hard constraints.
- Key assumptions.
- Relevant file/source pointers and why they matter.
- Done-when criteria.
- Operating mode: start with a short plan, read only relevant files, ask only blocking
  questions, prefer the smallest safe action, and report verification.

Do not include the full spec, brainstorming history, scan logs, long source summaries,
artifact path instructions, or user-facing tutorial prose.

## Final Handoff

When final artifacts are ready, say that the three files were generated and briefly
summarize the next step. Ask for approval before pre-vibe clears context and injects.
After approval, execute the clear-context step and inject only `FIRST_PROMPT.md`.

## References

Load only what is needed:

- `references/workflow.md` for the state machine and intensity behavior.
- `references/scan-policy.md` for safe context acquisition.
- `references/question-bank.md` for blocking question rules.
- `references/templates.md` for artifact writing rules.
- `references/agent-adapters.md` for Codex-facing prompt structure.
- `references/context-pyramid.md` for injection hygiene.
- `references/language-policy.md` for language behavior.
