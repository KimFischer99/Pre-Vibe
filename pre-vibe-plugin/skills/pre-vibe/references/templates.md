# Artifact Writing Rules

These are writing rules, not templates. Do not copy generic section prose into final
artifacts. Every sentence should be tied to the user's actual request, project files,
environment evidence, user answers, or explicit assumptions.

## Global Prohibitions

- No placeholders.
- No repeated template language.
- No generic workflow advice.
- No hidden implementation terms such as pre-vibe internals, plugin implementation,
  MCP server, or workflow plumbing unless the user's task is about building those things.
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
- Prioritized user scenarios and acceptance scenarios when the task involves a product,
  workflow, or user-facing behavior.
- In scope and out of scope.
- Functional requirements, non-functional requirements, edge cases, and measurable
  success criteria.
- Project/environment evidence, with paths and why they matter.
- Codex component recommendations based on installed components and searched/confirmed
  missing components.
- Assumptions and unknowns.
- Practical suggestions and explanation of tradeoffs.
- Verification plan and risk notes.
- Path guidance for user-relevant project files and references.

The spec may be educational. It should help the user understand what Codex will do and
why.

Do not mention the generated agent-guidance filename or path in this handbook.

## `PROJECT_AGENTS.md`

Audience: Codex or another agent. Keep it durable and terse.

Include:

- Existing global AGENTS guidance summary and project AGENTS summary when available.
- Project conventions, commands, directory boundaries, safety rules, and review rules.
- Conflict policy that preserves all higher-priority global rules.
- Task-relevant Codex component usage only when it affects how the agent should work in
  this project.

Exclude:

- One-off task details.
- Beginner explanations.
- Long rationale.
- Product brainstorming.
- Any rule that contradicts, narrows, or weakens global AGENTS.md.
- The generated handbook filename or path.

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
- References to generated artifact paths only when they help Codex start cleanly.

Exclude:

- Full spec content.
- Scan logs.
- Source summaries.
- Brainstorming history.
- Tutorial prose.
- Artifact path instructions beyond necessary file pointers.
