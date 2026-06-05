# pre-vibe Codex Plugin v0.1.2

pre-vibe is a token-disciplined first-turn context compiler for agent workflows.

It writes exactly three project-facing Markdown files:

- `PRE-VIBE-SPEC.MD` - handbook only; do not inject it into the formal workflow.
- `INIT-AGENTS.MD` - project-level AGENTS guidance based on global Codex AGENTS where available.
- `FIRST-PROMPT.MD` - compact execution brief; the only default injected context.

## Run

```bash
python3 scripts/pre_vibe.py \
  --task "Describe the task here" \
  --project . \
  --agent codex \
  --mode auto \
  --output-dir .
```

For an interactive handoff:

```bash
python3 scripts/pre_vibe.py --task "..." --project . --interactive
```

## Workflow

1. Generate the three Markdown files.
2. Review or edit `PRE-VIBE-SPEC.MD` and `INIT-AGENTS.MD`.
3. Approve `/clear`.
4. Inject only `FIRST-PROMPT.MD`.
5. Start the formal agent workflow.

## Token Discipline

- General tasks default to `micro`.
- Research and ordinary coding default to `standard`.
- Large coding/spec/refactor work can use `deep` or `architect`.
- The first prompt uses pointers and constraints, not long summaries.
