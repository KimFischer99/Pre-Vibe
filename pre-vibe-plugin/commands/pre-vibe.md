---
description: Start the pre-vibe Codex intake workflow for a rough first-session request
argument-hint: "\"用户初始问题\""
---

Start the installed pre-vibe Codex plugin workflow for this rough request:

$ARGUMENTS

Treat this as a slash-command launch, not as ordinary task execution.

Mandatory behavior:

- Preserve the raw user request.
- Run the safe project execution index and Codex component index before asking questions.
- Classify the task as general, research, coding, or mixed.
- Choose mini, default, or architect intensity.
- Ask only blocking questions through Codex's native question/user-input or approval UI.
- Do not ask blocking questions directly in ordinary chat.
- Keep intake notes in the active conversation only; do not write INTAKE.md or a draft intake file.
- Write exactly PRE_VIBE_SPEC.md, PROJECT_AGENTS.md, and FIRST_PROMPT.md when ready.
- Make all three files task-specific and evidence-based.
- Do not let PRE_VIBE_SPEC.md and PROJECT_AGENTS.md mention each other's filename or path.
- After user approval, clear the current context and inject only FIRST_PROMPT.md.
