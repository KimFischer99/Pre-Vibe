# Artifact Writing Rules

These are writing rules, not templates. Do not copy generic section prose into final
artifacts. Every sentence should be tied to the user's actual request, project files,
environment evidence, user answers, or explicit assumptions.

## Global Prohibitions

- No placeholders.
- No repeated template language.
- No generic workflow advice.
- No hidden implementation terms such as plugin, skill, MCP, tool server, or component
  unless the user's task is about building those things.
- No claims that context was scanned, searched, or confirmed unless that happened.
- No `INTAKE.md`, `PRE_VIBE_INTAKE.md`, or equivalent intake draft written to disk.
- No final `FIRST_PROMPT.md` while blocking questions or required context actions remain.

## `PRE_VIBE_SPEC.md`

Audience: the user. Write it as a friendly project handbook that a beginner can
understand.

Include:

- Raw user input.
- Normalized goal in plain language.
- Background and use case.
- In scope and out of scope.
- Requirements and acceptance criteria.
- Project/environment evidence, with paths and why they matter.
- Assumptions and unknowns.
- Practical suggestions and explanation of tradeoffs.
- Verification plan and risk notes.
- Path guidance: what this handbook is for, what AGENTS guidance is for, and which
  prompt file is meant for injection.

The spec may be educational. It should help the user understand what Codex will do and
why.

## `INIT_AGENTS.md`

Audience: Codex or another agent. Keep it durable and terse.

Include:

- Existing global AGENTS guidance summary and project AGENTS summary when available.
- Project conventions, commands, directory boundaries, safety rules, and review rules.
- Conflict policy that preserves all higher-priority global rules.

Exclude:

- One-off task details.
- Beginner explanations.
- Long rationale.
- Product brainstorming.
- Any rule that contradicts, narrows, or weakens global AGENTS.md.

## `FIRST_PROMPT.md`

Audience: Codex after pre-vibe clears context.

Include:

- Goal.
- Current task.
- Hard constraints.
- Key assumptions.
- Relevant file/source pointers.
- Done-when criteria.
- Operating mode.

Exclude:

- Full spec content.
- Scan logs.
- Source summaries.
- Brainstorming history.
- Tutorial prose.
- Artifact path instructions beyond necessary file pointers.
