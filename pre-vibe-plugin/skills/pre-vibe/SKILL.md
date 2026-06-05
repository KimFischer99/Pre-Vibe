---
name: pre-vibe
description: Use when a user wants to turn a vague request into a token-disciplined first-turn context package for an agent, including general work, research, and coding tasks. Produces a handbook spec, project AGENTS guidance, and a compact first prompt, then asks for approval to clear context and inject the prompt.
---

# pre-vibe

This skill runs a quiet context-preparation phase before normal execution. In user-facing progress updates, describe the work as "整理上下文", "准备首轮上下文", or "生成预备文件"; avoid repeatedly naming the plugin unless the user asks about the plugin itself.

## Token Discipline

Pre-vibe is a context optimizer, not a context expander.

- Classify the request before expanding context.
- Assign a hard budget: `micro`, `standard`, `deep`, or `architect`.
- Ask only blocking questions.
- Prefer file/source pointers over long summaries.
- Never inject the full spec by default.
- Do not include brainstorming history, raw references, full repository summaries, or non-actionable background in the first prompt.
- If the task needs context expansion, explicitly perform or propose the expansion action: blocking question, safe local inspection, source/documentation lookup, or environment/tool check.

## Workflow

1. Identify the task scenario: `general`, `research`, `coding`, or `mixed`.
2. Assign budget and compression mode before reading context.
3. Read only the minimum safe context allowed by the budget.
3. Do not read secret files such as `.env`, private keys, token caches, local databases, or production logs.
4. Ask only high-impact clarification questions when the answer would materially change the output. Otherwise continue with explicit assumptions.
5. For missing task objects, paths, tools, permissions, or environment settings, ask for them before generating an execution-ready prompt. Do not fill the gap with generic context.
5. Generate exactly three project-facing Markdown outputs:
   - `PRE-VIBE-SPEC.MD` - handbook only, not injected into formal workflow.
   - `INIT-AGENTS.MD` - project-level AGENTS guidance based on global Codex AGENTS where available.
   - `FIRST-PROMPT.MD` - compact execution brief, the only default injected context.
6. Make `PRE-VIBE-SPEC.MD` include Codex workflow recommendations and missing tool/environment suggestions when relevant: `AGENTS.md`, `.codex/config.toml`, sandbox/approval, MCP, hooks, Goal/Plan mode, validation, and review.
7. Ask the user to review or edit all three files, especially `FIRST-PROMPT.MD`.
8. Continue until the user explicitly approves the next step: run `/clear`, inject only the reviewed `FIRST-PROMPT.MD`, and begin formal work.

## User-Facing Tone

Do not say "I will use the pre-vibe skill/plugin" in ordinary progress updates. Prefer natural workflow language:

- "我先整理这次任务的首轮上下文。"
- "我先确认目标对象和必要环境，再生成三份预备文件。"
- "我会保持上下文精简，缺口只用问题或文件指针补齐。"

## Scripted Path

When working in a local filesystem and file output is requested, prefer the bundled script:

```bash
python3 pre-vibe-plugin/scripts/pre_vibe.py --task "<raw task>" --project . --agent codex --mode auto --output-dir .
```

If the plugin is installed outside this repository, resolve the script path relative to the plugin root.

After the script runs, do not stop at file generation. Ask:

```text
我已生成 PRE-VIBE-SPEC.MD、INIT-AGENTS.MD、FIRST-PROMPT.MD。
请先查看/修改这三份文件，尤其是 FIRST-PROMPT.MD。
是否批准我执行 /clear，并仅注入修改后的 FIRST-PROMPT.MD 作为正式 workflow 的初始上下文？
```

## References

Load only what is needed:

- `references/workflow.md` for the full intake flow.
- `references/scan-policy.md` for safe project scanning.
- `references/question-bank.md` for scenario-specific clarification questions.
- `references/templates.md` for output structure.
- `references/agent-adapters.md` for Codex, Claude Code, and generic agent prompts.
- `references/language-policy.md` for Chinese/English behavior.
- `references/token-budget.md` for budget and compression rules.
- `references/context-pyramid.md` for what may enter the first prompt.
